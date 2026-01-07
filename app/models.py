# app/models.py
# Defines all Pydantic models used in the tailoring framework:
# - JobDescription and JobRequirement: input job data
# - ResumeBullet and Evidence: core resume bullet representation
# - TailorRequest and TailorResponse: pipeline input/output contracts
from pydantic import BaseModel, Field
from typing import List, Optional

class JobRequirement(BaseModel):
    text: str

class JobDescription(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)
    nice_to_haves: List[str] = Field(default_factory=list)

class Evidence(BaseModel):
    source: str  # e.g., "Master:Citi#2"
    text: str

class ResumeBullet(BaseModel):
    text: str
     # Every bullet must be backed by at least one piece of evidence
    evidence: List[Evidence] = Field(..., min_length=1)
    category: str

class TailorRequest(BaseModel):
    jd: JobDescription
    master_resume_bullets: List[Evidence]
    target_count: int = 6
    # Default constraints ensure generated bullets are truthful, concise, and well-structured
    constraints: List[str] = Field(
        default_factory=lambda: [
            "No fabrication—only use provided evidence.",
            "Use action verbs; past tense.",
            "≤ 28 words per bullet."
        ]
    )

class TailorResponse(BaseModel):
    bullets: List[ResumeBullet]
    notes: Optional[str] = None
