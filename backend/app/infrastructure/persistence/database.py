"""Async SQLAlchemy engine + session factory, wrapped for app-wide lifecycle."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _engine_options(url: str) -> dict[str, Any]:
    """Driver-specific tuning. Managed Postgres (Supabase, etc.) needs a couple of
    safeguards that SQLite does not: pre-ping to survive idle-dropped connections, and
    disabling asyncpg's prepared-statement cache so the app works through a transaction
    pooler (pgbouncer) without 'prepared statement already exists' errors.
    """
    if url.startswith("postgresql"):
        return {
            "pool_pre_ping": True,
            "pool_recycle": 1800,
            "connect_args": {"statement_cache_size": 0},
        }
    return {}


class Database:
    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url, future=True, **_engine_options(url))
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    async def create_all(self) -> None:
        """Create tables from metadata. Dev/test convenience; prod uses Alembic."""
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self._engine.dispose()
