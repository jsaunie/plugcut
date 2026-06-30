"""Integration tests: HTTP -> use-case -> SQLAlchemy, against a real (sqlite) DB."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import Settings
from app.main import create_app


@pytest_asyncio.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    settings = Settings(
        jwt_secret="x" * 48,
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        auto_create_schema=True,
    )
    app = create_app(settings)
    await app.state.database.create_all()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await app.state.database.dispose()


async def _register(client: AsyncClient, email: str = "dev@example.com") -> None:
    response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "supersecret"}
    )
    assert response.status_code == 201


class TestRegister:
    async def test_creates_user(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "Dev@Example.com", "password": "supersecret"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "dev@example.com"  # normalized
        assert body["email_verified"] is False
        assert "password" not in body and "password_hash" not in body

    async def test_duplicate_email_conflicts(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dev@example.com", "password": "anotherone"},
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "identity.email_already_registered"

    async def test_weak_password_is_422(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register", json={"email": "dev@example.com", "password": "short"}
        )
        assert response.status_code == 422

    async def test_error_message_is_localized_french(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dev@example.com", "password": "supersecret"},
            headers={"Accept-Language": "fr-FR,fr;q=0.9"},
        )
        assert "déjà utilisé" in response.json()["error"]["message"]


class TestLoginAndMe:
    async def test_login_returns_tokens(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"] and body["refresh_token"]

    async def test_wrong_password_is_401(self, client: AsyncClient) -> None:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "nope-nope"}
        )
        assert response.status_code == 401

    async def test_me_requires_token(self, client: AsyncClient) -> None:
        assert (await client.get("/api/v1/auth/me")).status_code == 401

    async def test_me_returns_current_user(self, client: AsyncClient) -> None:
        await _register(client)
        login = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        token = login.json()["access_token"]
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "dev@example.com"


class TestRefresh:
    async def test_refresh_returns_new_pair(self, client: AsyncClient) -> None:
        await _register(client)
        login = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        refresh_token = login.json()["refresh_token"]

        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        new_access = response.json()["access_token"]

        me = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access}"}
        )
        assert me.status_code == 200

    async def test_access_token_rejected_as_refresh(self, client: AsyncClient) -> None:
        await _register(client)
        login = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        access_token = login.json()["access_token"]

        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": access_token}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "identity.invalid_token"


class TestMeta:
    async def test_health(self, client: AsyncClient) -> None:
        assert (await client.get("/health")).json() == {"status": "ok"}

    async def test_openapi_docs_available(self, client: AsyncClient) -> None:
        assert (await client.get("/openapi.json")).status_code == 200
