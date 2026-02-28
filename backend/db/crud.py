<<<<<<< HEAD
﻿"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from backend.models import User, Job, Proposal
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User CRUD
def create_user(db: Session, username: str, email: str, password: str) -> User:
    """Create a new user"""
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
=======
from sqlalchemy.orm import Session
from backend.models import User, Job


# =========================
# USER CRUD
# =========================

def create_user(db: Session, email: str, password: str):
    user = User(email=email, password=password)
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


<<<<<<< HEAD
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


# Job CRUD
_VALID_JOB_FIELDS = {
    'title', 'description', 'source', 'source_url', 'company',
    'location', 'job_type', 'tags', 'posted_date', 'scraped_at',
    'is_relevant', 'relevance_score'
}

def _build_job(job_data: dict) -> Job:
    """Build a Job ORM object from raw dict (no DB interaction)."""
    filtered = {k: v for k, v in job_data.items() if k in _VALID_JOB_FIELDS}
    filtered.setdefault('title', 'Untitled Job')
    filtered.setdefault('description', 'No description available')
    filtered.setdefault('source', 'unknown')
    return Job(**filtered)


def create_job(db: Session, job_data: dict) -> Job:
    """Create a single job (one commit per call)."""
    job = _build_job(job_data)
=======
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user_plan(db: Session, user_id: int, plan: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.plan = plan
    db.commit()
    db.refresh(user)
    return user


# =========================
# JOB CRUD
# =========================

def create_job(
    db: Session,
    platform: str,
    title: str,
    score: int,
    proposal: str,
    approved: bool = False
):
    job = Job(
        platform=platform,
        title=title,
        score=score,
        proposal=proposal,
        approved=approved
    )
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


<<<<<<< HEAD
def bulk_create_jobs(db: Session, jobs_data: List[dict]) -> List[Job]:
    """
    Bulk-insert all jobs in ONE commit.
    Uses flush() to get auto-generated IDs without N extra SELECT roundtrips.
    """
    if not jobs_data:
        return []
    objects = [_build_job(j) for j in jobs_data]
    db.add_all(objects)
    db.flush()    # assigns IDs without committing
    db.commit()   # single commit = one Neon roundtrip
    return objects



def get_jobs(db: Session, skip: int = 0, limit: int = 100, relevant_only: bool = False) -> List[Job]:
    """Get list of jobs"""
    query = db.query(Job)
    if relevant_only:
        query = query.filter(Job.is_relevant == True)
    return query.order_by(Job.scraped_at.desc()).offset(skip).limit(limit).all()


def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
    """Get job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()


def update_job_relevance(db: Session, job_id: int, is_relevant: bool, relevance_score: float = None):
    """Update job relevance status"""
    job = get_job_by_id(db, job_id)
    if job:
        job.is_relevant = is_relevant
        if relevance_score is not None:
            job.relevance_score = relevance_score
        db.commit()
        db.refresh(job)
    return job


# Proposal CRUD
def create_proposal(db: Session, job_id: int, content: str, suggested_price: float = None, 
                   pricing_rationale: str = None, user_id: int = None) -> Proposal:
    """Create a new proposal"""
    proposal = Proposal(
        job_id=job_id,
        user_id=user_id,
        content=content,
        suggested_price=suggested_price,
        pricing_rationale=pricing_rationale
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def get_proposals(db: Session, skip: int = 0, limit: int = 100) -> List[Proposal]:
    """Get list of proposals"""
    return db.query(Proposal).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()


def get_proposal_by_id(db: Session, proposal_id: int) -> Optional[Proposal]:
    """Get proposal by ID"""
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()


def get_proposals_by_job(db: Session, job_id: int) -> List[Proposal]:
    """Get all proposals for a specific job"""
    return db.query(Proposal).filter(Proposal.job_id == job_id).all()


def mark_proposal_submitted(db: Session, proposal_id: int):
    """Mark proposal as submitted"""
    proposal = get_proposal_by_id(db, proposal_id)
    if proposal:
        proposal.is_submitted = True
        proposal.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(proposal)
    return proposal
=======
def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def get_jobs_by_platform(db: Session, platform: str):
    return db.query(Job).filter(Job.platform == platform).all()


def get_approved_jobs(db: Session):
    return db.query(Job).filter(Job.approved == True).all()


def approve_job(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)
    if not job:
        return None
    job.approved = True
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True


# =========================
# ANALYTICS HELPERS
# =========================

def count_total_jobs(db: Session):
    return db.query(Job).count()


def count_approved_jobs(db: Session):
    return db.query(Job).filter(Job.approved == True).count()
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
