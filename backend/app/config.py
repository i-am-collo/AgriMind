"""
AgriMind — Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Uses pydantic-settings BaseSettings so every value can be overridden by
environment variables or a .env file without touching source code.

Priority (highest → lowest):
  1. Real environment variables
  2. .env file in the project root (loaded automatically)
  3. Default values defined below

All sensitive values (API keys, endpoint URLs, tokens) must be supplied via
the environment — never hardcoded in source or committed to version control.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _PYDANTIC_SETTINGS = True
except ImportError:  # pragma: no cover — pydantic-settings not installed yet
    from pydantic import BaseModel as BaseSettings  # type: ignore[assignment]
    _PYDANTIC_SETTINGS = False


class Settings(BaseSettings):
    """Central configuration object.  Instantiated once as ``settings``."""

    # ------------------------------------------------------------------
    # Project meta
    # ------------------------------------------------------------------
    PROJECT_NAME: str = "AgriMind"
    API_V1_STR: str = "/api/v1"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./agrimind.db"

    # ------------------------------------------------------------------
    # File storage
    # ------------------------------------------------------------------
    UPLOAD_DIR: str = str(
        Path(__file__).resolve().parent.parent / "uploads"
    )

    # ------------------------------------------------------------------
    # Legacy Gemini (kept for optional fallback; leave blank to disable)
    # ------------------------------------------------------------------
    GEMINI_API_KEY: Optional[str] = None

    # ------------------------------------------------------------------
    # Self-hosted VLM inference endpoint (vLLM / NVIDIA NIM)
    # ------------------------------------------------------------------

    # Base URL of the OpenAI-compatible inference server.
    # Example: http://10.0.0.1:8000  or  https://nim.example.com
    INFERENCE_ENDPOINT_URL: str = "http://localhost:8000"

    # HuggingFace model ID exactly as passed to --model when starting vLLM.
    # Must match the model the server was launched with.
    INFERENCE_MODEL_NAME: str = "Qwen/Qwen2-VL-7B-Instruct"

    # Seconds before an individual HTTP request to the VLM is abandoned.
    INFERENCE_TIMEOUT_SECONDS: int = 120

    # Number of HTTP-level retries on transient connectivity errors.
    # Does NOT retry on 4xx errors (those are fail-fast).
    INFERENCE_MAX_RETRIES: int = 3

    if _PYDANTIC_SETTINGS:
        model_config = SettingsConfigDict(
            env_file=["../.env", ".env"],
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )


settings = Settings()

# Ensure the upload directory exists at import time
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
