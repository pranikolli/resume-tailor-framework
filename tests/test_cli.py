# tests/test_cli.py
import json
from pathlib import Path
from app import llm as llm_mod
from cli.tailor import run

def test_cli_run_writes_output(monkeypatch, tmp_path):
    # Minimal fixtures
    jd = {
        "title": "Backend Software Engineer",
        "company": "ExampleCo",
        "responsibilities": ["Design REST APIs"],
        "requirements": [{"text": "Python"}],
        "nice_to_haves": []
    }
    master = [
        {"source": "Master:Proj#1", "text": "Developed FastAPI microservice with PostgreSQL and Docker"}
    ]

    # Stub the LLM call so test is deterministic
    payload = {
        "bullets": [
            {
                "text": "Developed FastAPI microservice with PostgreSQL and Docker.",
                "evidence": [master[0]],
                "category": "Backend"
            }
        ],
        "notes": "ok"
    }
    def fake_call(system, user):  # signature must match llm.call_llm
        return json.dumps(payload)

    monkeypatch.setattr(llm_mod, "call_llm", fake_call)

    # Write temp inputs
    jd_path = tmp_path / "jd.json"
    master_path = tmp_path / "master.json"
    out_path = tmp_path / "out.json"
    jd_path.write_text(json.dumps(jd))
    master_path.write_text(json.dumps(master))

    # Run CLI function
    wrote = run(str(jd_path), str(master_path), str(out_path), target_count=1)
    assert Path(wrote).exists()
    data = json.loads(out_path.read_text())
    assert "bullets" in data and len(data["bullets"]) == 1
    assert data["bullets"][0]["category"] == "Backend"
