"""
Filter Agent - Filters jobs based on relevance using LLM (batch mode, with timeout)
"""
from typing import List, Dict
import json
from langchain_openai import ChatOpenAI
from backend.config import settings

MAX_JOBS_PER_BATCH = 20   # cap to avoid huge prompts
REQUEST_TIMEOUT     = 30  # seconds per OpenAI call


class FilterAgent:
    """Agent that filters jobs based on relevance criteria"""

    def __init__(self):
        self.llm = None
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-your"):
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",        # fast + cheap
                    temperature=0.0,
                    api_key=settings.OPENAI_API_KEY,
                    request_timeout=REQUEST_TIMEOUT,
                )
                print("Success: FilterAgent: OpenAI (gpt-4o-mini) ready")
            except Exception as e:
                print(f"Warning: FilterAgent: Could not initialise OpenAI: {e}")

    # ── public API ────────────────────────────────────────────
    def filter_jobs(self, jobs: List[Dict], min_score: float = 0.6) -> List[Dict]:
        if not jobs:
            return []

        jobs = jobs[:MAX_JOBS_PER_BATCH]

        if not self.llm:
            print("Warning: OpenAI not available, using keyword filter")
            return self._basic_filter(jobs)

        try:
            return self._batch_filter(jobs, min_score)
        except Exception as e:
            print(f"Warning: Batch filter failed ({e}), falling back to keyword filter")
            return self._basic_filter(jobs)

    def run(self, state: dict) -> dict:
        """LangGraph node"""
        print("\n🔍 Filter Agent: filtering relevant jobs...")
        jobs = state.get("jobs", [])
        relevant = self.filter_jobs(jobs)
        state["relevant_jobs"] = relevant
        state["filtered_count"] = len(relevant)
        print(f"Success: {len(relevant)}/{len(jobs)} jobs are relevant")
        return state

    # ── internal ──────────────────────────────────────────────
    def _batch_filter(self, jobs: List[Dict], min_score: float) -> List[Dict]:
        """Send ALL jobs in one prompt → parse JSON array back."""
        jobs_text = "\n".join(
            f"{i+1}. Title: {j.get('title','N/A')} | Tags: {j.get('tags','N/A')}"
            for i, j in enumerate(jobs)
        )

        prompt = (
            "You are a job-relevance filter for a freelance software developer.\n"
            "Rate each job 0.0-1.0 for relevance (1.0 = perfectly relevant developer/tech job).\n"
            "Return ONLY a JSON array (no markdown, no explanation), one object per job, in order:\n"
            '[{"relevant": true/false, "score": 0.0-1.0, "reason": "short reason"}, ...]\n\n'
            f"Jobs:\n{jobs_text}"
        )

        response = self.llm.invoke(prompt)
        raw = response.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        results = json.loads(raw)

        relevant_jobs = []
        for job, res in zip(jobs, results):
            if res.get("relevant", False) and res.get("score", 0) >= min_score:
                job["is_relevant"]      = True
                job["relevance_score"]  = float(res.get("score", 0.7))
                job["relevance_reason"] = res.get("reason", "")
                relevant_jobs.append(job)

        return relevant_jobs

    def _basic_filter(self, jobs: List[Dict]) -> List[Dict]:
        """Keyword-based fallback"""
        keywords = {
            "python", "developer", "engineer", "programmer", "software",
            "backend", "frontend", "fullstack", "full-stack", "web", "react",
            "nodejs", "fastapi", "django", "flask", "typescript", "javascript",
            "ai", "ml", "data", "devops", "cloud", "aws",
        }
        relevant = []
        for job in jobs:
            text = f"{job.get('title','')} {job.get('tags','')}".lower()
            if any(k in text for k in keywords):
                job["is_relevant"]      = True
                job["relevance_score"]  = 0.7
                job["relevance_reason"] = "keyword match"
                relevant.append(job)
        print(f"Success: Keyword filter: {len(relevant)}/{len(jobs)} jobs relevant")
        return relevant
