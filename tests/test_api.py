# tests/test_api.py
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.api import app
from app import llm as llm_mod

def _load(fi):
    return json.loads(Path(fi).read_text())

def test_post_tailor_returns_response(monkeypatch):
    jd = _load("tests/fixtures/jd_sample.json")
    master = _load("tests/fixtures/resume_master.json")

    # Model output (what the LLM would return)
    model_payload = {
        "bullets": [
            {
                "text": "Developed FastAPI microservice with PostgreSQL and Docker.",
                "evidence": [master[1]],  # cite 'Proj#1' evidence
                "category": "Backend",
            }
        ],
        "notes": "ok",
    }

    def fake_call(system, user):
        return json.dumps(model_payload)

    monkeypatch.setattr(llm_mod, "call_llm", fake_call)

    client = TestClient(app)
    req_body = {
        "jd": jd,
        "master_resume_bullets": master,
        "target_count": 1
    }
    r = client.post("/tailor", json=req_body)
    assert r.status_code == 200
    body = r.json()
    assert "bullets" in body and len(body["bullets"]) == 1
    assert body["bullets"][0]["category"] == "Backend"
