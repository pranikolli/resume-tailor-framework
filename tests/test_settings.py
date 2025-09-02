import os
import importlib
import pytest

def _reload_settings_module():
    import app.settings as settings_module
    settings_module.get_settings.cache_clear()
    return importlib.reload(settings_module)

def test_get_settings_missing_key_raises(monkeypatch):
    # Override any .env value by setting an empty env var
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "any-model")

    settings_module = _reload_settings_module()
    with pytest.raises(RuntimeError):
        settings_module.get_settings()
