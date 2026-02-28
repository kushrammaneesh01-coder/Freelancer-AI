from pydantic import BaseModel
from typing import List, Optional

class JobSchema(BaseModel):
    platform: str
    title: str
    description: str
    budget: Optional[int]
    skills: Optional[List[str]]

class ProposalSchema(BaseModel):
    proposal: str
    bid: int
    approved: bool

class AgentRequest(BaseModel):
    jobs: List[JobSchema]
