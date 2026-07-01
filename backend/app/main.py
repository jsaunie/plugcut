"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import Settings, get_settings
from app.infrastructure.persistence.database import Database
from app.interfaces.api.errors import register_error_handlers
from app.interfaces.api.routers import (
    auth,
    contacts,
    intros,
    invitations,
    profiles,
    referrals,
    reputation,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if settings.auto_create_schema:
            await database.create_all()
        yield
        await database.dispose()

    app = FastAPI(title="Plugcut API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.database = database

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(referrals.router, prefix="/api/v1")
    app.include_router(invitations.router, prefix="/api/v1")
    app.include_router(contacts.router, prefix="/api/v1")
    app.include_router(reputation.router, prefix="/api/v1")
    app.include_router(profiles.router, prefix="/api/v1")
    app.include_router(intros.router, prefix="/api/v1")

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
