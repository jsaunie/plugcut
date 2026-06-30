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

    # Origins allowed to call the API from a browser (the SPA). Override in prod.
    cors_origins: list[str] = ["http://localhost:5173"]

    # Create tables from ORM metadata on startup. Convenient for local/sqlite dev;
    # set false in production and manage schema with Alembic migrations.
    auto_create_schema: bool = True

    default_locale: str = "fr"

    # Email (Resend). Leave the API key empty to fall back to a logging sender that
    # never sends real mail (the demo default). Set PLUGCUT_RESEND_API_KEY +
    # PLUGCUT_EMAIL_FROM to send through Resend.
    resend_api_key: str = ""
    email_from: str = "Plugcut <onboarding@resend.dev>"

    @property
    def email_enabled(self) -> bool:
        return bool(self.resend_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
