import json
from pathlib import Path
from app.models import JobDescription, Evidence, TailorRequest, TailorResponse, ResumeBullet

def test_models_load_from_fixtures():
    jd = JobDescription(**json.loads(Path("tests/fixtures/jd_sample.json").read_text()))
    master = [Evidence(**e) for e in json.loads(Path("tests/fixtures/resume_master.json").read_text())]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=2)
    assert req.jd.title == "Backend Software Engineer"
    assert len(req.master_resume_bullets) == 2

def test_response_shape_minimal():
    # Ensure TailorResponse enforces evidence and fields
    bullet = ResumeBullet(
        text="Developed FastAPI microservice with PostgreSQL and Docker.",
        evidence=[Evidence(source="Master:Proj#1", text="Developed FastAPI microservice with PostgreSQL and Docker")],
        category="Backend"
    )
    resp = TailorResponse(bullets=[bullet], notes="ok")
    assert resp.bullets[0].category == "Backend"
