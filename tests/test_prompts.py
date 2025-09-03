# tests/test_prompts.py
import json
from pathlib import Path
from app.models import JobDescription, Evidence, TailorRequest
from app.prompts import render_user_prompt, SYSTEM, CATEGORIES, FEW_SHOT

def _load(fi):
    return json.loads(Path(fi).read_text())

def test_render_user_prompt_contains_core_parts():
    jd = JobDescription(**_load("tests/fixtures/jd_sample.json"))
    master = [Evidence(**e) for e in _load("tests/fixtures/resume_master.json")]
    req = TailorRequest(jd=jd, master_resume_bullets=master, target_count=3)

    prompt = render_user_prompt(req)
    # Basic sanity checks
    assert "Job Description (JSON):" in prompt
    assert '"Backend Software Engineer"' in prompt  # from fixture
    assert '"Master:Citi#2"' in prompt
    assert "Target # of bullets: 3" in prompt

def test_system_prompt_mentions_categories_and_json_rules():
    assert all(cat in SYSTEM for cat in CATEGORIES)
    assert '"bullets"' in SYSTEM and '"notes"' in SYSTEM
    assert "pure JSON" in SYSTEM or "ONLY JSON" in SYSTEM

def test_few_shot_shape_is_valid_json_like():
    # Sanity: few-shot has the expected keys and can be json-dumped
    assert {"jd", "evidence", "expect"}.issubset(set(FEW_SHOT.keys()))
    json.dumps(FEW_SHOT)  # should not raise
