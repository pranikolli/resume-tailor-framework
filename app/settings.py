# app/settings.py
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv

# Load variables from a local .env file if present
load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_base_url: Optional[str] = None  # optional for Azure/OpenRouter/local proxy

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Read and validate required env vars once (cached).
    Raises a clear error if OPENAI_API_KEY is missing.
    """
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Create a .env from .env.example and set your key."
        )
    return Settings(openai_api_key=key, openai_model=model, openai_base_url=base_url)
