"""
Proposal Agent - Generates AI-powered proposals for jobs (fast batch mode)
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from backend.config import settings

MAX_PROPOSALS   = 5    # keep costs/time reasonable
REQUEST_TIMEOUT = 30   # seconds


class ProposalAgent:
    """Agent that generates custom proposals for jobs"""

    def __init__(self):
        self.llm = None
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-your"):
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",        # fast + cheap, very good quality
                    temperature=0.7,
                    api_key=settings.OPENAI_API_KEY,
                    request_timeout=REQUEST_TIMEOUT,
                )
                print("Success: ProposalAgent: OpenAI (gpt-4o-mini) ready")
            except Exception as e:
                print(f"Warning: ProposalAgent: Could not initialise OpenAI: {e}")

    # ── public API ────────────────────────────────────────────
    def generate_proposal(self, job: Dict) -> str:
        if not self.llm:
            return self._template_proposal(job)
        try:
            prompt = (
                "You are an expert freelance proposal writer. Write a compelling, professional "
                "proposal (150-200 words) in first person for the job below. "
                "Be specific, enthusiastic, and end with a call to action.\n\n"
                f"Job Title: {job.get('title','N/A')}\n"
                f"Company: {job.get('company','N/A')}\n"
                f"Description: {job.get('description','')[:600]}\n"
                f"Skills: {job.get('tags','N/A')}\n\n"
                "Write the proposal:"
            )
            resp = self.llm.invoke(prompt)
            proposal = resp.content.strip()
            print(f"Success: Proposal generated for '{job.get('title','N/A')}'")
            return proposal
        except Exception as e:
            print(f"Warning: Proposal generation failed ({e}), using template")
            return self._template_proposal(job)

    def run(self, state: dict) -> dict:
        """LangGraph node"""
        print("\n✍️  Proposal Agent: generating proposals...")
        relevant_jobs = state.get("relevant_jobs", [])[:MAX_PROPOSALS]

        proposals = []
        for job in relevant_jobs:
            text = self.generate_proposal(job)
            proposals.append({"job": job, "proposal": text})

        state["proposals"]       = proposals
        state["proposal_count"]  = len(proposals)
        print(f"Success: Generated {len(proposals)} proposals")
        return state

    # ── internal ──────────────────────────────────────────────
    def _template_proposal(self, job: Dict) -> str:
        title   = job.get("title", "this position")
        company = job.get("company", "your company")
        tags    = job.get("tags", "relevant technologies")
        return (
            f"Dear Hiring Manager at {company},\n\n"
            f"I am excited to apply for the {title} role. With hands-on experience in "
            f"{tags}, I have delivered high-quality software solutions for clients across "
            "various industries. I write clean, maintainable code and communicate proactively "
            "throughout the project lifecycle.\n\n"
            "I understand your needs and am confident I can exceed your expectations. "
            "I am available to start immediately and would love to discuss the project further. "
            "Please feel free to reach out — I look forward to hearing from you!\n\n"
            "Best regards"
        )
