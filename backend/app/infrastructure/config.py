"""Application settings, loaded from environment / .env file."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="PLUGCUT_", extra="ignore"
    )

    # SECURITY: override in every real environment via PLUGCUT_JWT_SECRET.
    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 14

    database_url: str = "sqlite+aiosqlite:///./plugcut.db"

    default_locale: str = "fr"


@lru_cache
def get_settings() -> Settings:
    return Settings()
