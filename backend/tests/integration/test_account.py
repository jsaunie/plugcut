"""Integration tests for account management: change password/email, delete."""

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


async def _register_login(
    client: AsyncClient, email: str = "dev@example.com", password: str = "supersecret"
) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestChangePassword:
    async def test_change_then_login_with_new(self, client: AsyncClient) -> None:
        headers = await _register_login(client)
        resp = await client.put(
            "/api/v1/auth/me/password",
            json={"current_password": "supersecret", "new_password": "brandnewpass"},
            headers=headers,
        )
        assert resp.status_code == 204
        old = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        assert old.status_code == 401
        new = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "brandnewpass"}
        )
        assert new.status_code == 200

    async def test_rejects_wrong_current(self, client: AsyncClient) -> None:
        headers = await _register_login(client)
        resp = await client.put(
            "/api/v1/auth/me/password",
            json={"current_password": "wrong", "new_password": "brandnewpass"},
            headers=headers,
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "identity.invalid_credentials"

    async def test_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.put(
            "/api/v1/auth/me/password",
            json={"current_password": "supersecret", "new_password": "brandnewpass"},
        )
        assert resp.status_code == 401


class TestChangeEmail:
    async def test_change_then_me_reflects(self, client: AsyncClient) -> None:
        headers = await _register_login(client)
        resp = await client.put(
            "/api/v1/auth/me/email",
            json={"new_email": "new@example.com", "current_password": "supersecret"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "new@example.com"

    async def test_rejects_taken_email(self, client: AsyncClient) -> None:
        await _register_login(client, "taken@example.com")
        headers = await _register_login(client, "me@example.com")
        resp = await client.put(
            "/api/v1/auth/me/email",
            json={"new_email": "taken@example.com", "current_password": "supersecret"},
            headers=headers,
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "identity.email_already_registered"


class TestDeleteAccount:
    async def test_delete_erases_and_blocks_login(self, client: AsyncClient) -> None:
        headers = await _register_login(client)
        # Give the account some data to erase.
        await client.post(
            "/api/v1/profile/me",
            json={
                "handle": "dev-x",
                "display_name": "Dev",
                "headline": "",
                "skills": [],
                "bio": "",
                "available": True,
            },
            headers=headers,
        )
        resp = await client.request(
            "DELETE",
            "/api/v1/auth/me",
            json={"current_password": "supersecret"},
            headers=headers,
        )
        assert resp.status_code == 204
        # Login no longer works; the public profile is gone.
        login = await client.post(
            "/api/v1/auth/login", json={"email": "dev@example.com", "password": "supersecret"}
        )
        assert login.status_code == 401
        assert (await client.get("/api/v1/profiles/dev-x")).status_code == 404

    async def test_rejects_wrong_password(self, client: AsyncClient) -> None:
        headers = await _register_login(client)
        resp = await client.request(
            "DELETE", "/api/v1/auth/me", json={"current_password": "nope"}, headers=headers
        )
        assert resp.status_code == 401
