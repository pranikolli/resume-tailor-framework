# app/prompts.py
import json
from typing import List
from .models import TailorRequest

# Categories shown to the model for consistent labeling
CATEGORIES: List[str] = [
    "Backend", "Frontend", "Data", "ML", "Cloud", "DevOps", "Security", "Other"
]

SYSTEM = f"""You are a resume tailoring engine. You rewrite resume bullets to match a job description while staying strictly grounded in the provided evidence.

Hard rules:
- Use ONLY the provided evidence for factual claims. No fabrication: never invent companies, tools, metrics, dates, scope, or responsibilities.
- You MUST rewrite: output bullet text MUST NOT be an exact copy of any single evidence bullet text.
- Preserve factual meaning: you may rephrase, reorder, and emphasize relevant skills, but do not change what happened.
- Each bullet must cite 1–2 evidence items that directly support it.
- Metrics rule: include a metric ONLY if the SAME evidence item contains that metric. Do not move metrics across sources.
- Each bullet ≤ 28 words. Start with a strong action verb.
- Choose exactly one category from: {", ".join(CATEGORIES)}.
- Choose the MOST specific applicable category; do NOT default to Backend.
- Use Backend only if no other category fits better.
- If evidence is insufficient for a bullet, omit the bullet rather than guessing.
- Output MUST be pure JSON with top-level keys: "bullets" (array) and "notes" (string or null).
- Each bullet object must be: {{"text": str, "evidence": [{{"source": str, "text": str}}], "category": str}}.
- Do not include markdown, backticks, prose, or any keys other than specified.
- Prefer synthesizing 2 related evidence items into a single bullet when possible.


Notes field:
- If ANY job description responsibility or requirement is not supported by the evidence, list it briefly in "notes".
- Otherwise set "notes" to null.

"""


# A tiny few-shot to anchor style/shape. (Used later by the LLM wrapper if desired.)
FEW_SHOT = {
    "jd": {
        "title": "Backend Engineer",
        "company": "ExampleCo",
        "responsibilities": ["Design REST APIs", "Write unit tests"]
    },
    "evidence": [
        {"source": "Master:Citi#2", "text": "Built Spring Boot REST APIs; reduced reporting time 30%"},
        {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
    ],
    "expect": {
        "bullets": [
            {
                "text": "Built RESTful APIs in Spring Boot to streamline finance reporting workflows, cutting manual reporting time by 30%.",
                "evidence": [
                    {"source": "Master:Citi#2", "text": "Built Spring Boot REST APIs; reduced reporting time 30%"}
                ],
                "category": "Backend"
            },
            {
                "text": "Developed a FastAPI microservice backed by PostgreSQL and Docker to support backend resume-processing workflows.",
                "evidence": [
                    {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
                ],
                "category": "Backend"
            }
        ],
        "notes": "JD mentions unit tests; no evidence explicitly demonstrates unit/integration testing."
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
