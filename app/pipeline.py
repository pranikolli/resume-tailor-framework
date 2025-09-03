# app/pipeline.py
from typing import Set
from .models import TailorRequest, TailorResponse, ResumeBullet
from . import llm

def _normalize_text(s: str) -> str:
    return " ".join(s.lower().split())

def _dedupe_keep_first(bullets: list[ResumeBullet]) -> list[ResumeBullet]:
    seen: Set[str] = set()
    out: list[ResumeBullet] = []
    for b in bullets:
        key = _normalize_text(b.text)
        if key not in seen:
            out.append(b)
            seen.add(key)
    return out

def tailor(req: TailorRequest) -> TailorResponse:
    resp = llm.generate(req)
    resp.bullets = _dedupe_keep_first(resp.bullets)[: req.target_count]
    return resp
