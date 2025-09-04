# tests/test_utils.py
import json, os
from pathlib import Path
from app.utils import log_event

def test_log_event_writes_file(tmp_path, monkeypatch):
    # Direct logs to a temp dir
    log_dir = tmp_path / "logs"
    monkeypatch.setenv("LOG_DIR", str(log_dir))

    payload = {
        "openai_api_key": "sk-should-not-appear",
        "evidence": [{"source": "Master:Proj#1", "text": "My detailed resume line"}],
        "note": "hello"
    }
    log_event("request", payload, redact=True)

    files = list(log_dir.glob("*.json"))
    assert len(files) == 1

    data = json.loads(files[0].read_text())
    # Ensure redaction happened
    assert data["openai_api_key"] == "[redacted]"
    assert data["evidence"][0]["text"] == "[redacted]"
    assert data["note"] == "hello"
