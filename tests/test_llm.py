# tests/test_llm.py
import json
from pathlib import Path
from app.models import JobDescription, Evidence, TailorRequest
from app import llm as llm_mod

def _load(fi):
    return json.loads(Path(fi).read_text())

def test_generate_with_stubbed_llm(monkeypatch):
    jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
    master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=1)

    # Deterministic JSON from the "model"
    payload = {
        "bullets": [
            {
                "text": "Developed FastAPI microservice with PostgreSQL and Docker.",
                "evidence": [master[1].model_dump()],
                "category": "Backend",
            }
        ],
        "notes": "ok",
    }

    def fake_call(system, user):
        return json.dumps(payload)

    monkeypatch.setattr(llm_mod, "call_llm", fake_call)
    resp = llm_mod.generate(req)
    assert len(resp.bullets) == 1
    assert resp.bullets[0].evidence[0].source == master[1].source

def test_generate_salvages_json_when_wrapped_in_prose(monkeypatch):
    jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
    master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=1)

    payload = {
        "bullets": [
            {
                "text": "Built REST endpoints that improved reporting workflows by 30%.",
                "evidence": [master[0].model_dump()],
                "category": "Backend",
            }
        ],
        "notes": None,
    }

    def fake_call(system, user):
        # Simulate extra text around JSON
        return "Sure, here you go:\n" + json.dumps(payload) + "\nDone."

    monkeypatch.setattr(llm_mod, "call_llm", fake_call)
    resp = llm_mod.generate(req)
    assert resp.bullets[0].evidence[0].source == master[0].source
