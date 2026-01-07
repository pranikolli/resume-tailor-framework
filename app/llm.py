# app/llm.py
import json
import os
from typing import Any, Dict, Set, List
from .models import TailorRequest, TailorResponse, Evidence, ResumeBullet
from .prompts import SYSTEM, render_user_prompt, CATEGORIES
from .utils import log_event


#  JSON helpers 

def _salvage_json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise

def _enforce_guardrails(req: TailorRequest, resp: TailorResponse) -> TailorResponse:
    master_sources: Set[str] = {e.source for e in req.master_resume_bullets}
    for b in resp.bullets:
        if not b.evidence or any(ev.source not in master_sources for ev in b.evidence):
            raise ValueError("Bullet cites unknown/missing evidence (violates no-fabrication).")
        if len(b.text.split()) > 28:
            raise ValueError("Bullet exceeds 28-word limit.")
        if b.category not in CATEGORIES:
            b.category = "Other"
    return resp

#  Demo mode (no LLM) 

def _demo_response(req: TailorRequest) -> TailorResponse:
    """
    Build short bullets directly from evidence so you can test the API
    without an LLM or tokens.
    Includes safety bounds checking to ensure generated bullets are valid.
    """
    bullets: List[ResumeBullet] = []
    
    # Safety: Limit to reasonable number of bullets
    max_bullets = min(req.target_count, len(req.master_resume_bullets), 20)
    
    for ev in req.master_resume_bullets[:max_bullets]:
        # Safety: Validate evidence text is not empty
        if not ev.text or not ev.text.strip():
            continue
            
        # Safety: Truncate very long evidence text to prevent issues
        evidence_text = ev.text.strip()
        if len(evidence_text) > 500:  # Reasonable limit for evidence
            evidence_text = evidence_text[:497] + "..."
        
        # Make a short, safe bullet from evidence text (<= 28 words)
        words = evidence_text.rstrip(".").split()
        
        # Safety: Ensure we don't exceed word limit
        # "Applied experience: " = 2 words, so we have 26 words left
        max_evidence_words = min(len(words), 24)  # Leave room for prefix and suffix
        bullet_words = words[:max_evidence_words]
        
        # Create bullet text with safety checks
        if bullet_words:
            text = "Applied experience: " + " ".join(bullet_words) + "."
        else:
            # Fallback for empty evidence
            text = "Applied experience: [No details available]."
        
        # Final safety check: ensure bullet is within word limit
        word_count = len(text.split())
        if word_count > 28:
            # Emergency truncation if somehow we exceeded limit
            words = text.split()[:28]
            text = " ".join(words)
        
        bullets.append(
            ResumeBullet(
                text=text,
                evidence=[Evidence(source=ev.source, text=ev.text)],
                category="Other"
            )
        )
    
    return TailorResponse(bullets=bullets, notes="demo mode")

# Real LLM call (OpenAI) 

def call_llm(system: str, user: str) -> str:
    """
    Real LLM call via OpenAI. Keep signature so tests can monkeypatch.
    """
    from .settings import get_settings
    from openai import OpenAI

    s = get_settings()
    client = OpenAI(api_key=s.openai_api_key, base_url=s.openai_base_url)

    resp = client.chat.completions.create(
        model=s.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        top_p=0.9,
        seed=42,
        response_format={"type": "json_object"},  # ask for strict JSON
    )
    return resp.choices[0].message.content

# Public API 

def generate(req: TailorRequest) -> TailorResponse:
    # Fast path: Demo mode returns valid JSON without LLM
    if os.getenv("DEMO_MODE", "0").lower() in {"1", "true", "yes"}:
        resp = _demo_response(req)
        return _enforce_guardrails(req, resp)

    # Otherwise render prompt and call the model
    user = render_user_prompt(req)
    # log request (redacted)
    log_event("request", {
        "system": SYSTEM,
        "user": user,
        "jd": req.jd.model_dump(),
        "master_resume_bullets": [e.model_dump() for e in req.master_resume_bullets],
        "target_count": req.target_count
    })
    raw = call_llm(SYSTEM, user)
    data = _salvage_json(raw)
    resp = TailorResponse(**data)
    log_event("response", {"response": resp.model_dump()})
    return _enforce_guardrails(req, resp)
