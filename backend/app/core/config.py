"""
app/core/config.py
------------------
Centralised application settings powered by pydantic-settings.

All sensitive values are loaded exclusively from the `.env` file —
NOTHING is hard-coded in this file.

Startup warnings are emitted for optional keys that are absent,
so the server still starts cleanly even without third-party credentials.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    #  Application metadata
    # ------------------------------------------------------------------ #
    APP_NAME: str = Field(default="AgriSmart AI", description="Human-readable app name")
    APP_VERSION: str = Field(default="1.0.0", description="Semantic version string")
    APP_DESCRIPTION: str = Field(
        default=(
            "AI-powered agricultural intelligence platform — "
            "crop disease detection, irrigation advisory, weather risk analysis, "
            "and Gemini-powered farmer guidance."
        ),
        description="Shown in Swagger UI",
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode and verbose logging")

    # ------------------------------------------------------------------ #
    #  API routing
    # ------------------------------------------------------------------ #
    API_V1_PREFIX: str = Field(default="/api/v1", description="Root prefix for all v1 routes")

    # ------------------------------------------------------------------ #
    #  CORS
    # ------------------------------------------------------------------ #
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description=(
            "Allowed CORS origins. Use ['*'] for open-access during hackathon; "
            "restrict to specific domains in production."
        ),
    )

    # ------------------------------------------------------------------ #
    #  Supabase
    # ------------------------------------------------------------------ #
    SUPABASE_URL: Optional[str] = Field(
        default=None,
        description=(
            "Supabase project URL. "
            "Find at: Supabase Dashboard → Project Settings → API → Project URL. "
            "Example: https://xyzxyzxyz.supabase.co"
        ),
    )
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = Field(
        default=None,
        description=(
            "Supabase anon/publishable key — safe to expose. "
            "Find at: Supabase Dashboard → Project Settings → API → Project API Keys → anon/public. "
            "Used for Supabase Auth / Storage client calls."
        ),
    )

    # ------------------------------------------------------------------ #
    #  Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./agrismart.db",
        description=(
            "SQLAlchemy async database URL. "
            "Default: SQLite (local dev). "
            "Supabase/Production: postgresql+asyncpg://postgres.[ref]:[password]@[host]:5432/postgres. "
            "When this field is blank in .env the default SQLite URL is used automatically."
        ),
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _coerce_empty_database_url(cls, v: str) -> str:
        """Fall back to SQLite when DATABASE_URL is present but empty in .env."""
        if not v or not v.strip():
            return "sqlite+aiosqlite:///./agrismart.db"
        return v

    # ------------------------------------------------------------------ #
    #  ML Model
    # ------------------------------------------------------------------ #
    MODEL_PATH: str = Field(
        default="",
        description=(
            "Path to a trained image-classification model file "
            "(.onnx, .pt, .pth, .h5). "
            "Leave empty to activate the built-in mock inference service."
        ),
    )
    MODEL_INPUT_SIZE: int = Field(
        default=224,
        description="Square pixel dimension the model expects (height == width)",
    )
    CONFIDENCE_THRESHOLD: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to accept a prediction; below this returns a safe fallback",
    )

    # ------------------------------------------------------------------ #
    #  Google Gemini AI
    # ------------------------------------------------------------------ #
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description=(
            "Google Gemini API key. "
            "Obtain at: https://aistudio.google.com/app/apikey. "
            "When absent, the assistant falls back to the built-in mock engine."
        ),
    )
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description=(
            "Gemini model identifier. "
            "'gemini-1.5-flash' is fast and cost-efficient; "
            "'gemini-1.5-pro' provides higher reasoning quality."
        ),
    )

    # ------------------------------------------------------------------ #
    #  Weather API  (OpenWeatherMap)
    # ------------------------------------------------------------------ #
    WEATHER_API_KEY: Optional[str] = Field(
        default=None,
        description=(
            "OpenWeatherMap API key. "
            "Sign up at: https://openweathermap.org/api. "
            "When absent, weather endpoints return mock data."
        ),
    )
    WEATHER_API_BASE_URL: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        description="Base URL for the OpenWeatherMap REST API",
    )

    # ------------------------------------------------------------------ #
    #  pydantic-settings config
    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    #  Post-init warnings  (graceful degradation)
    # ------------------------------------------------------------------ #
    def emit_startup_warnings(self) -> None:
        """
        Log informational warnings for missing optional credentials.
        Called once from app lifespan — server always starts regardless.
        """
        # ── Supabase ─────────────────────────────────────────────────────
        if not self.SUPABASE_URL:
            logger.warning(
                "⚠  SUPABASE_URL is not set in .env — Supabase client features disabled. "
                "Paste your Project URL from: Supabase Dashboard → Project Settings → API."
            )
        else:
            logger.info("✅ SUPABASE_URL loaded: %s", self.SUPABASE_URL)

        if not self.SUPABASE_PUBLISHABLE_KEY:
            logger.warning(
                "⚠  SUPABASE_PUBLISHABLE_KEY is not set in .env — Supabase Auth/Storage disabled. "
                "Paste your anon key from: Supabase Dashboard → Project Settings → API."
            )
        else:
            logger.info("✅ SUPABASE_PUBLISHABLE_KEY loaded.")

        if self.DATABASE_URL.startswith("sqlite"):
            logger.warning(
                "⚠  DATABASE_URL is using SQLite (local dev mode). "
                "Paste your Supabase direct connection string into DATABASE_URL in .env "
                "to connect to PostgreSQL."
            )
        else:
            # Mask password in log output — find :password@ and replace with :***@
            safe_url = self.DATABASE_URL
            try:
                if "@" in safe_url and ":" in safe_url.split("@")[0]:
                    prefix, rest = safe_url.rsplit("@", 1)
                    user_part = prefix.rsplit(":", 1)[0]
                    safe_url = f"{user_part}:***@{rest}"
            except Exception:
                safe_url = "<configured>"
            logger.info("✅ DATABASE_URL set to PostgreSQL: %s", safe_url)

        # ── ML Model ──────────────────────────────────────────────────────
        if not self.MODEL_PATH:
            logger.warning(
                "⚠  MODEL_PATH is not set in .env — running in mock inference mode. "
                "Set MODEL_PATH to a .onnx/.pt/.h5 file to enable real predictions."
            )
        elif not os.path.isfile(self.MODEL_PATH):
            logger.warning(
                "⚠  Model file not found at '%s' — falling back to mock predictions.",
                self.MODEL_PATH,
            )
        else:
            logger.info("✅ Model file found at '%s'.", self.MODEL_PATH)

        if not self.GEMINI_API_KEY:
            logger.warning(
                "⚠  GEMINI_API_KEY is not set in .env — AI assistant will use mock engine. "
                "Set GEMINI_API_KEY to activate Gemini-powered responses."
            )
        else:
            logger.info("✅ GEMINI_API_KEY loaded (model: %s).", self.GEMINI_MODEL)

        if not self.WEATHER_API_KEY:
            logger.warning(
                "⚠  WEATHER_API_KEY is not set in .env — weather endpoints will return mock data. "
                "Set WEATHER_API_KEY from https://openweathermap.org/api."
            )
        else:
            logger.info("✅ WEATHER_API_KEY loaded.")


# Singleton — import this everywhere instead of re-instantiating Settings()
settings = Settings()
