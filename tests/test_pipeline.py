# tests/test_pipeline.py
import json
from pathlib import Path
from app.models import JobDescription, Evidence, TailorRequest
from app import llm as llm_mod
from app.pipeline import tailor

def _load(fi):
    return json.loads(Path(fi).read_text())

def test_pipeline_dedupes_and_trims(monkeypatch):
    jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
    master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=1)

    payload = {
        "bullets": [
            {
                "text": "Developed FastAPI microservice with PostgreSQL and Docker.",
                "evidence": [master[1].model_dump()],
                "category": "Backend",
            },
            {
                # duplicate text with weird spacing/case to test normalization
                "text": "developed   FastAPI microservice with  postgresql and docker.",
                "evidence": [master[1].model_dump()],
                "category": "Backend",
            },
        ],
        "notes": None,
    }

    def fake_call(system, user):
        return json.dumps(payload)

    # Patch llm.call_llm so llm.generate returns the payload above
    monkeypatch.setattr(llm_mod, "call_llm", fake_call)

    resp = tailor(req)
    assert len(resp.bullets) == 1
    assert resp.bullets[0].text.lower().startswith("developed fastapi microservice")

def test_pipeline_respects_target_count(monkeypatch):
    jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
    master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=2)

    payload = {
        "bullets": [
            {
                "text": "Built REST endpoints that improved reporting workflows by 30%.",
                "evidence": [master[0].model_dump()],
                "category": "Backend",
            },
            {
                "text": "Developed FastAPI microservice with PostgreSQL and Docker.",
                "evidence": [master[1].model_dump()],
                "category": "Backend",
            },
            {
                "text": "Implemented CI workflows for backend services.",
                "evidence": [master[1].model_dump()],
                "category": "DevOps",
            },
        ],
        "notes": "many bullets",
    }

    def fake_call(system, user):
        return json.dumps(payload)

    monkeypatch.setattr(llm_mod, "call_llm", fake_call)
    resp = tailor(req)
    assert len(resp.bullets) == 2  # trimmed to target_count
