# app/llm.py
import json
from typing import Any, Dict, Set
from .models import TailorRequest, TailorResponse
from .prompts import SYSTEM, render_user_prompt, CATEGORIES

def call_llm(system: str, user: str) -> str:
    """
    Placeholder LLM call. Intentionally unimplemented so tests can monkeypatch it.
    Later you'll replace this with an OpenAI call.
    """
    raise NotImplementedError("call_llm is not wired yet. Monkeypatch in tests or integrate OpenAI.")

def _salvage_json(raw: str) -> Dict[str, Any]:
    """
    Try to parse JSON; if extra prose surrounds it, pull the outermost {...}.
    """
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
        # evidence present and from supplied master resume
        if not b.evidence or any(ev.source not in master_sources for ev in b.evidence):
            raise ValueError("Bullet cites unknown/missing evidence (violates no-fabrication).")
        # ≤ 28 words
        if len(b.text.split()) > 28:
            raise ValueError("Bullet exceeds 28-word limit.")
        # category normalization
        if b.category not in CATEGORIES:
            b.category = "Other"
    return resp

def generate(req: TailorRequest) -> TailorResponse:
    user = render_user_prompt(req)
    raw = call_llm(SYSTEM, user)
    data = _salvage_json(raw)
    resp = TailorResponse(**data)
    return _enforce_guardrails(req, resp)
