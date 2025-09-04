# app/utils.py
import os, time, uuid, json
from pathlib import Path
from typing import Any, Dict

SENSITIVE_KEYS = {"openai_api_key", "api_key", "password", "token"}

def _redact(obj: Any) -> Any:
    """Recursively redact sensitive fields & evidence 'text'."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            kl = k.lower()
            if kl in SENSITIVE_KEYS:
                out[k] = "[redacted]"
            elif kl == "text" and isinstance(v, str):
                out[k] = "[redacted]"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    return obj

def _get_log_dir() -> Path:
    # Read env at call-time so tests can override LOG_DIR
    return Path(os.getenv("LOG_DIR", "logs"))

def log_event(kind: str, payload: Dict[str, Any], redact: bool = True) -> None:
    """
    Write a JSON log file like: logs/1699999999999-kind-deadbeef.json
    Never throw—logging must not break the app.
    """
    try:
        log_dir = _get_log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        data = _redact(payload) if redact else payload
        ts = int(time.time() * 1000)
        fname = log_dir / f"{ts}-{kind}-{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(data, indent=2))
    except Exception:
        # swallow logging errors (best-effort)
        pass
