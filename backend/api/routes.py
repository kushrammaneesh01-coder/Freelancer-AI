<<<<<<< HEAD
﻿"""
FastAPI Routes - API endpoints for the application
Production-ready: background tasks, proper status tracking, all agents
"""
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt

from backend.db.session import get_db, SessionLocal
from backend.db import crud
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ── In-memory workflow status tracker ─────────────────────────
_workflow_status: Dict[str, Any] = {
    "running": False,
    "last_run": None,
    "last_result": None,
}

# ── Pydantic schemas ──────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    is_relevant: bool
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True

class ProposalResponse(BaseModel):
    id: int
    job_id: int
    content: str
    suggested_price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Auth helpers ──────────────────────────────────────────────

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Auth routes ───────────────────────────────────────────────

@router.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db, user.username, user.email, user.password)
    return {"access_token": create_access_token({"sub": user.username}), "token_type": "bearer"}

@router.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": user.username}), "token_type": "bearer"}


# ── Jobs routes ───────────────────────────────────────────────

@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, relevant_only: bool = False,
             db: Session = Depends(get_db)):
    return crud.get_jobs(db, skip=skip, limit=limit, relevant_only=relevant_only)

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ── Proposals routes ──────────────────────────────────────────

@router.get("/proposals", response_model=List[ProposalResponse])
def get_proposals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_proposals(db, skip=skip, limit=limit)

@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = crud.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


# ── Scrape-only endpoint (fast, no AI) ────────────────────────

@router.post("/scrape")
def scrape_jobs(db: Session = Depends(get_db)):
    """
    Fast endpoint: Scrape jobs from all sources → save to DB.
    No AI calls - returns immediately.
    """
    from scraper.remoteok import RemoteOKScraper
    from scraper.weworkremotely import WeWorkRemotelyScraper
    from scraper.adzuna import AdzunaScraper
    from backend.agents.filter_agent import FilterAgent

    all_jobs = []
    errors = []

    try:
        all_jobs += RemoteOKScraper().scrape_jobs(limit=10)
    except Exception as e:
        errors.append(f"RemoteOK: {e}")

    try:
        all_jobs += WeWorkRemotelyScraper().scrape_jobs(category="programming", limit=10)
    except Exception as e:
        errors.append(f"WeWorkRemotely: {e}")

    try:
        az = AdzunaScraper(app_id=settings.ADZUNA_APP_ID, app_key=settings.ADZUNA_APP_KEY)
        all_jobs += az.scrape_jobs(limit=5)
    except Exception as e:
        errors.append(f"Adzuna: {e}")

    # Keyword-based quick filter (no AI)
    fa = FilterAgent()
    relevant = fa._basic_filter(all_jobs)

    # Save all jobs to DB
    # Bulk save — single commit = one Neon roundtrip
    try:
        saved_jobs = crud.bulk_create_jobs(db, all_jobs)
        saved = len(saved_jobs)
    except Exception as e:
        logger.error(f"Bulk job save error: {e}")
        saved = 0

    logger.info(f"Scraped {len(all_jobs)} jobs, {saved} saved to DB")

    return {
        "status": "success",
        "jobs_scraped": len(all_jobs),
        "jobs_relevant_keyword": len(relevant),
        "jobs_saved_to_db": saved,
        "errors": errors,
    }


# ── Background workflow worker ────────────────────────────────

def _workflow_background(job_ids: List[int]):
    """Run AI steps in background thread against already-saved jobs."""
    from backend.agents.proposal_agent import ProposalAgent
    from backend.agents.pricing_agent import PricingAgent
    from backend.agents.memory_agent import MemoryAgent
    from backend.db.session import SessionLocal as SL

    _workflow_status["running"] = True
    result = {"proposals_generated": 0, "proposals_saved": 0, "errors": []}

    db = SL()
    try:
        pa  = ProposalAgent()
        pra = PricingAgent()
        ma  = MemoryAgent()

        jobs_to_propose = []
        for jid in job_ids[:5]:  # max 5 proposals
            job = crud.get_job_by_id(db, jid)
            if job:
                jobs_to_propose.append(job)

        for job_obj in jobs_to_propose:
            job_dict = {
                "title":       job_obj.title,
                "description": job_obj.description or "",
                "company":     job_obj.company or "",
                "tags":        job_obj.tags or "",
                "job_type":    job_obj.job_type or "",
                "source":      job_obj.source,
                "source_url":  job_obj.source_url or "",
            }
            try:
                proposal_text = pa.generate_proposal(job_dict)
                pricing       = pra.suggest_pricing(job_dict)
                crud.create_proposal(
                    db,
                    job_id=job_obj.id,
                    content=proposal_text,
                    suggested_price=pricing.get("recommended_price"),
                    pricing_rationale=pricing.get("rationale"),
                )
                result["proposals_generated"] += 1
                result["proposals_saved"] += 1
                logger.info(f"Success: Proposal created for job #{job_obj.id}: {job_obj.title}")
            except Exception as e:
                result["errors"].append(str(e))
                logger.warning(f"Proposal error for job #{job_obj.id}: {e}")

        # Memory
        try:
            state = {"relevant_jobs": [{"title": j.title} for j in jobs_to_propose], "proposals": []}
            ma.run(state)
        except Exception as e:
            logger.warning(f"Memory agent (non-critical): {e}")

    except Exception as e:
        result["errors"].append(str(e))
        logger.error(f"Background workflow error: {e}", exc_info=True)
    finally:
        db.close()

    _workflow_status["running"] = False
    _workflow_status["last_run"] = datetime.utcnow().isoformat()
    _workflow_status["last_result"] = result
    logger.info(f"Background workflow done: {result}")


def _full_pipeline_background():
    """
    Run the ENTIRE pipeline in a background thread:
    scrape → keyword filter → bulk save to Neon → mark relevant → proposals.
    Uses create_background_session() with NullPool (independent connection, no pool sharing).
    """
    from scraper.remoteok import RemoteOKScraper
    from scraper.weworkremotely import WeWorkRemotelyScraper
    from scraper.adzuna import AdzunaScraper
    from backend.agents.filter_agent import FilterAgent
    from backend.agents.proposal_agent import ProposalAgent
    from backend.agents.pricing_agent import PricingAgent
    from backend.agents.memory_agent import MemoryAgent
    from backend.db.session import create_background_session

    _workflow_status["running"] = True
    _workflow_status["last_result"] = {"status": "running", "step": "scraping"}
    logger.info("Full pipeline background started")

    db = create_background_session()
    result = {
        "status": "success",
        "jobs_scraped": 0,
        "jobs_relevant": 0,
        "jobs_saved": 0,
        "proposals_generated": 0,
        "proposals_saved": 0,
        "errors": [],
    }
    try:
        # ── 1. Scrape ──────────────────────────────────────────
        all_jobs = []
        for scraper_fn, label in [
            (lambda: RemoteOKScraper().scrape_jobs(limit=10), "RemoteOK"),
            (lambda: WeWorkRemotelyScraper().scrape_jobs(category="programming", limit=10), "WeWorkRemotely"),
            (lambda: AdzunaScraper(app_id=settings.ADZUNA_APP_ID, app_key=settings.ADZUNA_APP_KEY).scrape_jobs(limit=5), "Adzuna"),
        ]:
            try:
                jobs = scraper_fn()
                all_jobs.extend(jobs)
                logger.info(f"{label}: {len(jobs)} jobs")
            except Exception as e:
                result["errors"].append(f"{label}: {e}")
                logger.warning(f"{label} scrape error: {e}")

        result["jobs_scraped"] = len(all_jobs)
        _workflow_status["last_result"] = {**result, "step": "filtering"}

        # ── 2. Keyword Filter (fast, no AI) ────────────────────
        fa = FilterAgent()
        relevant = fa._basic_filter(all_jobs)
        result["jobs_relevant"] = len(relevant)
        logger.info(f"Keyword filter: {len(relevant)}/{len(all_jobs)} relevant")

        # ── 3. Bulk save all jobs to Neon DB ───────────────────
        _workflow_status["last_result"] = {**result, "step": "saving_to_db"}
        saved_jobs = crud.bulk_create_jobs(db, all_jobs)
        result["jobs_saved"] = len(saved_jobs)
        title_map = {j.title: j for j in saved_jobs}
        logger.info(f"Saved {len(saved_jobs)} jobs to Neon DB")

        # ── 4. Mark relevant jobs in DB ────────────────────────
        relevant_db_jobs = []
        for rel in relevant:
            db_job = title_map.get(rel.get("title", ""))
            if db_job:
                try:
                    crud.update_job_relevance(db, db_job.id, True, rel.get("relevance_score", 0.7))
                    relevant_db_jobs.append(db_job)
                except Exception as e:
                    logger.warning(f"Relevance update: {e}")

        # ── 5. Generate AI proposals (max 5) ───────────────────
        _workflow_status["last_result"] = {**result, "step": "generating_proposals"}
        pa  = ProposalAgent()
        pra = PricingAgent()
        for db_job in relevant_db_jobs[:5]:
            job_dict = {
                "title":       db_job.title,
                "description": db_job.description or "",
                "company":     db_job.company or "",
                "tags":        db_job.tags or "",
                "source":      db_job.source,
                "source_url":  db_job.source_url or "",
            }
            try:
                proposal_text = pa.generate_proposal(job_dict)
                pricing       = pra.suggest_pricing(job_dict)
                crud.create_proposal(
                    db,
                    job_id=db_job.id,
                    content=proposal_text,
                    suggested_price=pricing.get("recommended_price"),
                    pricing_rationale=pricing.get("rationale"),
                )
                result["proposals_generated"] += 1
                result["proposals_saved"] += 1
                logger.info(f"Proposal saved for '{db_job.title}'")
            except Exception as e:
                result["errors"].append(str(e))
                logger.warning(f"Proposal error for {db_job.id}: {e}")

        # ── 6. ChromaDB memory ─────────────────────────────────
        try:
            MemoryAgent().run({
                "relevant_jobs": [{"title": j.title} for j in relevant_db_jobs],
                "proposals": [],
            })
        except Exception as e:
            logger.warning(f"Memory agent (non-critical): {e}")

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        logger.error(f"Full pipeline error: {e}", exc_info=True)
    finally:
        db.close()

    _workflow_status["running"] = False
    _workflow_status["last_run"] = datetime.utcnow().isoformat()
    _workflow_status["last_result"] = {**result, "step": "done"}
    logger.info(f"Full pipeline complete: {result}")


# ── Main workflow endpoint (fast + background AI) ─────────────

@router.post("/workflow/run")
def run_workflow(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Full pipeline workflow — returns IMMEDIATELY.
    All heavy work (scraping, AI filter, proposals) runs in a background thread.
    Poll GET /api/workflow/status to track progress and results.
    """
    if _workflow_status.get("running"):
        return {
            "status": "already_running",
            "message": "A workflow is already running. Check /api/workflow/status for progress.",
        }

    # Kick off the entire pipeline in the background
    background_tasks.add_task(_full_pipeline_background)

    return {
        "status": "started",
        "message": "Full pipeline started in background (scrape → filter → save → AI proposals).",
        "check_progress": "/api/workflow/status",
    }


@router.get("/workflow/status")
def workflow_status():
    """Check the status of the background AI proposal generation"""
    return {
        "running":     _workflow_status.get("running", False),
        "last_run":    _workflow_status.get("last_run"),
        "last_result": _workflow_status.get("last_result"),
    }


# ── Root ──────────────────────────────────────────────────────

@router.get("/")
def api_root():
    return {
        "message": "AI Freelancing Automation Agency API",
        "version": "1.0.0",
        "endpoints": {
            "auth":             "/api/auth/register, /api/auth/login",
            "jobs":             "/api/jobs",
            "proposals":        "/api/proposals",
            "scrape_only":      "POST /api/scrape",
            "full_workflow":    "POST /api/workflow/run",
            "workflow_status":  "GET  /api/workflow/status",
        },
    }
=======
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.graph.workflow import workflow

router = APIRouter()

@router.post("/run-agents")
def run_agents(payload: dict, db: Session = Depends(get_db)):
    """
    Payload format:
    {
        "jobs": [ {...}, {...} ]
    }
    """
    result = workflow.invoke(payload)
    return result
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.crud import create_job

router = APIRouter()

@router.post("/save-job")
def save_job(job: dict, db: Session = Depends(get_db)):
    """
    This is where create_job() BELONGS
    """
    saved_job = create_job(
        db=db,
        platform=job["platform"],
        title=job["title"],
        score=job.get("score", 0),
        proposal=job.get("proposal", ""),
        approved=False
    )
    return {"status": "saved", "job_id": saved_job.id}
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
