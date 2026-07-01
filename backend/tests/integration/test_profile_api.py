"""Integration tests for the profile endpoints (own + public with reputation)."""

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


async def _headers(client: AsyncClient, email: str = "ref@example.com") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _sign_a_deal(client: AsyncClient, headers: dict[str, str]) -> None:
    created = await client.post(
        "/api/v1/referrals",
        json={
            "placed_person_email": "dev@example.com",
            "client_reference": "ACME",
            "daily_rate": "500",
            "commission_rate": "10",
            "duration_months": 12,
            "currency": "EUR",
        },
        headers=headers,
    )
    deal_id = created.json()["id"]
    await client.post(f"/api/v1/referrals/{deal_id}/qualify", headers=headers)
    await client.post(
        f"/api/v1/referrals/{deal_id}/accept",
        json={"party": "referrer", "signature": "Jean"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/referrals/{deal_id}/accept",
        json={"party": "placed", "signature": "Dev"},
        headers=headers,
    )


_PROFILE = {
    "handle": "jean-dev",
    "display_name": "Jean Dev",
    "headline": "Backend freelance",
    "skills": ["Python", "FastAPI"],
    "bio": "10 ans d'XP",
    "available": True,
}


class TestOwnProfile:
    async def test_missing_profile_returns_404(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        assert (await client.get("/api/v1/profile/me", headers=headers)).status_code == 404

    async def test_upsert_then_read(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        created = await client.put("/api/v1/profile/me", json=_PROFILE, headers=headers)
        assert created.status_code == 200
        assert created.json()["handle"] == "jean-dev"
        assert created.json()["skills"] == ["Python", "FastAPI"]

        read = await client.get("/api/v1/profile/me", headers=headers)
        assert read.json()["display_name"] == "Jean Dev"

    async def test_upsert_is_idempotent_and_updates(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        await client.put("/api/v1/profile/me", json=_PROFILE, headers=headers)
        updated = await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "jean-2", "available": False},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["handle"] == "jean-2"
        assert updated.json()["available"] is False

    async def test_invalid_handle_rejected(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        response = await client.put(
            "/api/v1/profile/me", json={**_PROFILE, "handle": "no"}, headers=headers
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "profile.invalid_handle"

    async def test_handle_taken_by_another_user(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        await client.put("/api/v1/profile/me", json=_PROFILE, headers=owner)
        intruder = await _headers(client, "intruder@example.com")
        response = await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "display_name": "Someone Else"},
            headers=intruder,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "profile.handle_taken"


class TestPublicProfile:
    async def test_public_profile_shows_reputation(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        await client.put("/api/v1/profile/me", json=_PROFILE, headers=headers)
        await _sign_a_deal(client, headers)

        response = await client.get("/api/v1/profiles/jean-dev")  # no auth
        assert response.status_code == 200
        body = response.json()
        assert body["profile"]["display_name"] == "Jean Dev"
        assert body["reputation"]["sealed_deals"] == 1
        assert body["reputation"]["trust_score"] > 0

    async def test_unknown_handle_returns_404(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/profiles/nobody-here")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "profile.not_found"


class TestDirectory:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        assert (await client.get("/api/v1/profiles")).status_code == 401

    async def test_ranks_by_trust_score(self, client: AsyncClient) -> None:
        # Trusted owner: a profile plus a sealed deal (trust > 0).
        trusted = await _headers(client, "trusted@example.com")
        await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "trusted-dev", "display_name": "Trusted Dev"},
            headers=trusted,
        )
        await _sign_a_deal(client, trusted)
        # Newcomer: a profile, no deals (trust 0).
        newcomer = await _headers(client, "newcomer@example.com")
        await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "new-dev", "display_name": "New Dev"},
            headers=newcomer,
        )

        response = await client.get("/api/v1/profiles", headers=trusted)
        assert response.status_code == 200
        handles = [row["profile"]["handle"] for row in response.json()]
        assert handles == ["trusted-dev", "new-dev"]
        assert response.json()[0]["reputation"]["trust_score"] > 0

    async def test_filters_by_skill(self, client: AsyncClient) -> None:
        pydev = await _headers(client, "py@example.com")
        await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "py-dev", "skills": ["Python", "FastAPI"]},
            headers=pydev,
        )
        vuedev = await _headers(client, "vue@example.com")
        await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "vue-dev", "skills": ["Vue"]},
            headers=vuedev,
        )
        response = await client.get("/api/v1/profiles?skill=python", headers=pydev)
        handles = [row["profile"]["handle"] for row in response.json()]
        assert handles == ["py-dev"]

    async def test_hides_unavailable_by_default(self, client: AsyncClient) -> None:
        away = await _headers(client, "away@example.com")
        await client.put(
            "/api/v1/profile/me",
            json={**_PROFILE, "handle": "away-dev", "available": False},
            headers=away,
        )
        default = await client.get("/api/v1/profiles", headers=away)
        assert default.json() == []
        including = await client.get("/api/v1/profiles?available=false", headers=away)
        assert [r["profile"]["handle"] for r in including.json()] == ["away-dev"]
