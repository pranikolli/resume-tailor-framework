# tests/conftest.py
import pytest

@pytest.fixture(autouse=True)
def _default_env(monkeypatch):
    # Ensure demo mode is OFF during tests so monkeypatched call_llm is used
    monkeypatch.setenv("DEMO_MODE", "0")
