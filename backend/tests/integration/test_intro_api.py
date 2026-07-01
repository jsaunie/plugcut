"""Integration tests for warm intro requests."""

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


async def _headers(client: AsyncClient, email: str) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _with_profile(client: AsyncClient, email: str, handle: str) -> dict[str, str]:
    headers = await _headers(client, email)
    await client.put(
        "/api/v1/profile/me",
        json={
            "handle": handle,
            "display_name": handle.title(),
            "headline": "",
            "skills": [],
            "bio": "",
            "available": True,
        },
        headers=headers,
    )
    return headers


class TestRequestIntro:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/profiles/x/intro", json={"message": "hi"})
        assert response.status_code == 401

    async def test_requester_needs_a_profile(self, client: AsyncClient) -> None:
        await _with_profile(client, "target@example.com", "target-dev")
        requester = await _headers(client, "nobody@example.com")  # no profile
        response = await client.post(
            "/api/v1/profiles/target-dev/intro", json={"message": "hi"}, headers=requester
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "intro.profile_required"

    async def test_unknown_handle_404(self, client: AsyncClient) -> None:
        requester = await _with_profile(client, "req@example.com", "req-dev")
        response = await client.post(
            "/api/v1/profiles/ghost/intro", json={"message": "hi"}, headers=requester
        )
        assert response.status_code == 404

    async def test_request_then_visible_both_sides(self, client: AsyncClient) -> None:
        target = await _with_profile(client, "target@example.com", "target-dev")
        requester = await _with_profile(client, "req@example.com", "req-dev")

        created = await client.post(
            "/api/v1/profiles/target-dev/intro",
            json={"message": "On a un client commun."},
            headers=requester,
        )
        assert created.status_code == 201

        req_inbox = await client.get("/api/v1/intros", headers=requester)
        outbound = req_inbox.json()["outbound"]
        assert len(outbound) == 1
        assert outbound[0]["counterpart"]["handle"] == "target-dev"
        assert outbound[0]["status"] == "pending"

        tgt_inbox = await client.get("/api/v1/intros", headers=target)
        inbound = tgt_inbox.json()["inbound"]
        assert len(inbound) == 1
        assert inbound[0]["counterpart"]["handle"] == "req-dev"

    async def test_no_duplicate_pending(self, client: AsyncClient) -> None:
        await _with_profile(client, "target@example.com", "target-dev")
        requester = await _with_profile(client, "req@example.com", "req-dev")
        await client.post(
            "/api/v1/profiles/target-dev/intro", json={"message": "1"}, headers=requester
        )
        again = await client.post(
            "/api/v1/profiles/target-dev/intro", json={"message": "2"}, headers=requester
        )
        assert again.status_code == 409
        assert again.json()["error"]["code"] == "intro.already_pending"


class TestRespondToIntro:
    async def _make_intro(self, client: AsyncClient) -> tuple[dict[str, str], dict[str, str], str]:
        target = await _with_profile(client, "target@example.com", "target-dev")
        requester = await _with_profile(client, "req@example.com", "req-dev")
        created = await client.post(
            "/api/v1/profiles/target-dev/intro", json={"message": "hi"}, headers=requester
        )
        return target, requester, created.json()["id"]

    async def test_target_accepts(self, client: AsyncClient) -> None:
        target, _, intro_id = await self._make_intro(client)
        response = await client.post(
            f"/api/v1/intros/{intro_id}/respond", json={"accept": True}, headers=target
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    async def test_only_target_may_respond(self, client: AsyncClient) -> None:
        _, requester, intro_id = await self._make_intro(client)
        response = await client.post(
            f"/api/v1/intros/{intro_id}/respond", json={"accept": True}, headers=requester
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "intro.forbidden"

    async def test_cannot_respond_twice(self, client: AsyncClient) -> None:
        target, _, intro_id = await self._make_intro(client)
        await client.post(
            f"/api/v1/intros/{intro_id}/respond", json={"accept": True}, headers=target
        )
        again = await client.post(
            f"/api/v1/intros/{intro_id}/respond", json={"accept": False}, headers=target
        )
        assert again.status_code == 409
        assert again.json()["error"]["code"] == "intro.already_resolved"
