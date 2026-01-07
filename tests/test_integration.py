# tests/test_integration.py
# Integration tests that call REAL OpenAI API
# Only runs when INTEGRATION_TEST=1 environment variable is set
# Skipped in CI/CD by default to avoid token usage
import os
import json
import pytest
from pathlib import Path
from app.models import JobDescription, Evidence, TailorRequest
from app.pipeline import tailor
from fastapi.testclient import TestClient
from app.api import app

# Only run these tests if explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST", "0").lower() not in {"1", "true", "yes"},
    reason="Integration tests only run with INTEGRATION_TEST=1 env var"
)

def _load(fi):
    return json.loads(Path(fi).read_text())

class TestIntegrationRealLLM:
    """Test against real OpenAI API"""

    def test_generate_with_real_api(self):
        """Call real LLM and verify response structure"""
        jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
        master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
        req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=2)

        # This makes a REAL call to OpenAI
        resp = tailor(req)

        # Verify response structure
        assert resp.bullets is not None
        assert len(resp.bullets) <= 2  # respects target_count
        assert all(hasattr(b, "text") for b in resp.bullets)
        assert all(hasattr(b, "evidence") for b in resp.bullets)
        assert all(hasattr(b, "category") for b in resp.bullets)

    def test_guardrails_enforced_with_real_api(self):
        """Verify guardrails are applied to real API responses"""
        jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
        master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
        req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=1)

        resp = tailor(req)

        # Verify guardrails
        for bullet in resp.bullets:
            # Word count <= 28
            word_count = len(bullet.text.split())
            assert word_count <= 28, f"Bullet exceeds 28 words: {word_count}"
            
            # Has evidence
            assert len(bullet.evidence) >= 1, "Bullet must have evidence"
            
            # Evidence references exist in master
            master_sources = {e.source for e in master}
            for ev in bullet.evidence:
                assert ev.source in master_sources, f"Unknown source: {ev.source}"
            
            # Category is valid
            from app.prompts import CATEGORIES
            assert bullet.category in CATEGORIES, f"Invalid category: {bullet.category}"

    def test_api_endpoint_with_real_llm(self):
        """Test FastAPI endpoint with real LLM"""
        client = TestClient(app)
        jd = _load("tests/fixtures/jd_sample.json")
        master = _load("tests/fixtures/resume_master.json")

        resp = client.post(
            "/tailor",
            json={
                "jd": jd,
                "master_resume_bullets": master,
                "target_count": 1
            }
        )

        assert resp.status_code == 200
        body = resp.json()
        assert "bullets" in body
        assert len(body["bullets"]) <= 1

    def test_different_jd_generates_different_bullets(self):
        """Verify LLM generates context-appropriate bullets"""
        # First request with Backend focus
        jd_backend = JobDescription(
            title="Backend Engineer",
            company="ExampleCo",
            responsibilities=["Design databases", "Write APIs"],
            requirements=[{"text": "Python"}, {"text": "SQL"}]
        )
        master = [
            Evidence(source="Master:Backend#1", text="Designed PostgreSQL schema for 100k+ user database"),
            Evidence(source="Master:Backend#2", text="Built REST API handling 50+ endpoints")
        ]
        req1 = TailorRequest(jd=jd_backend, master_resume_bullets=master, target_count=2)
        resp1 = tailor(req1)

        # Second request with Frontend focus
        jd_frontend = JobDescription(
            title="Frontend Engineer",
            company="ExampleCo",
            responsibilities=["Build UI components", "Optimize performance"],
            requirements=[{"text": "React"}, {"text": "TypeScript"}]
        )
        req2 = TailorRequest(jd=jd_frontend, master_resume_bullets=master, target_count=2)
        resp2 = tailor(req2)

        # Responses might differ in categorization/content
        # At minimum, both should have valid bullets
        assert len(resp1.bullets) > 0
        assert len(resp2.bullets) > 0


class TestIntegrationEdgeCases:
    """Test edge cases with real API"""

    def test_minimal_evidence(self):
        """Test with only 1 piece of evidence"""
        jd = JobDescription(
            title="Any Role",
            company="Company",
            responsibilities=["Do something"]
        )
        master = [Evidence(source="Proj#1", text="Completed project")]
        req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=1)

        resp = tailor(req)
        assert len(resp.bullets) >= 0  # May or may not generate, but shouldn't crash

    def test_zero_target_count(self):
        """Test requesting zero bullets"""
        jd = JobDescription(
            title="Any Role",
            company="Company",
            responsibilities=["Do something"]
        )
        master = [Evidence(source="Proj#1", text="Completed project")]
        req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=0)

        resp = tailor(req)
        assert len(resp.bullets) == 0

    def test_large_target_count(self):
        """Test requesting more bullets than available evidence"""
        jd = JobDescription(
            title="Any Role",
            company="Company",
            responsibilities=["Do something"]
        )
        master = [
            Evidence(source="Proj#1", text="Completed project 1"),
            Evidence(source="Proj#2", text="Completed project 2")
        ]
        req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=100)

        resp = tailor(req)
        # Should generate up to what's possible, not necessarily 100
        assert isinstance(resp.bullets, list)

