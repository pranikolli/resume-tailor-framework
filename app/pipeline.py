# app/pipeline.py
# Orchestrates the resume tailoring process:
# 1. Calls the LLM to generate tailored resume bullets.
# 2. Deduplicates bullets by normalizing text.
# 3. Trims to the target number specified in TailorRequest.
from typing import Set
from .models import TailorRequest, TailorResponse, ResumeBullet
from . import llm

def _normalize_text(s: str) -> str:
# Lowercase and collapse whitespace so duplicates can be detected reliably
    return " ".join(s.lower().split())

def _dedupe_keep_first(bullets: list[ResumeBullet]) -> list[ResumeBullet]:
    seen: Set[str] = set()
    out: list[ResumeBullet] = []
    for b in bullets:
        key = _normalize_text(b.text) # normalize spacing + case
        if key not in seen:  # keep first occurrence only
            out.append(b)
            seen.add(key)
    return out

def tailor(req: TailorRequest) -> TailorResponse:
    # Call the LLM to generate tailored bullets
    resp = llm.generate(req)
    # Deduplicate and trim bullets down to target_count
    resp.bullets = _dedupe_keep_first(resp.bullets)[: req.target_count]
    return resp
