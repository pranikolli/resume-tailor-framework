# app/prompts.py
import json
from typing import List
from .models import TailorRequest

# Categories shown to the model for consistent labeling
CATEGORIES: List[str] = [
    "Backend", "Frontend", "Data", "ML", "Cloud", "DevOps", "Security", "Other"
]

SYSTEM = f"""You generate resume bullets from a job description using ONLY the provided evidence.

Rules:
- No fabrication. Never invent companies, tools, metrics, or dates.
- Each bullet ≤ 28 words. Start with a strong action verb; include a metric only if present in evidence.
- Choose one category from: {", ".join(CATEGORIES)}.
- If evidence is insufficient, omit the bullet rather than guessing.
- Output MUST be pure JSON with top-level keys: "bullets" (array) and "notes" (string or null).
- Each bullet object must be: {{"text": str, "evidence": [{{"source": str, "text": str}}], "category": str}}.
- Do not include markdown, backticks, prose, or any keys other than specified.
"""

# A tiny few-shot to anchor style/shape. (Used later by the LLM wrapper if desired.)
FEW_SHOT = {
    "jd": {"title": "Backend Engineer", "company": "ExampleCo", "responsibilities": ["Design REST APIs"]},
    "evidence": [
        {"source": "Master:Citi#2", "text": "Built Spring Boot REST APIs; reduced reporting time 30%"},
        {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
    ],
    "expect": {
        "bullets": [
            {
                "text": "Developed FastAPI microservice and REST endpoints, improving reporting workflows by 30%.",
                "evidence": [
                    {"source": "Master:Citi#2", "text": "Built Spring Boot REST APIs; reduced reporting time 30%"},
                    {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
                ],
                "category": "Backend"
            }
        ],
        "notes": "Grounded in provided evidence only."
    }
}

USER_TEMPLATE = """Job Description (JSON):
{jd}

Evidence from my master resume (trusted facts, JSON list):
{evidence}

Constraints:
{constraints}

Target # of bullets: {n}

Return ONLY JSON with keys "bullets" and "notes".
"""

def render_user_prompt(req: TailorRequest) -> str:
    """Serialize the request into the user prompt the model will see."""
    jd_str = json.dumps(req.jd.model_dump(), indent=2)
    ev_str = json.dumps([e.model_dump() for e in req.master_resume_bullets], indent=2)
    return USER_TEMPLATE.format(
        jd=jd_str,
        evidence=ev_str,
        constraints="\n".join(f"- {c}" for c in req.constraints),
        n=req.target_count,
    )
