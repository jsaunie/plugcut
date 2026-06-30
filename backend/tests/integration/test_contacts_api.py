"""Integration tests for the contacts API (private, owner-scoped)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import Settings
from app.main import create_app

PAYLOAD = {
    "full_name": "Marie Coach",
    "kind": "person",
    "headline": "Coach indépendante",
    "linkedin_url": "https://linkedin.com/in/marie",
    "tags": ["coaching", "bien-être"],
    "notes": "Rencontrée à un meetup.",
}


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


async def _headers(client: AsyncClient, email: str = "owner@example.com") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestContactsCrud:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        assert (await client.post("/api/v1/contacts", json=PAYLOAD)).status_code == 401

    async def test_create_and_list(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        created = await client.post("/api/v1/contacts", json=PAYLOAD, headers=headers)
        assert created.status_code == 201
        body = created.json()
        assert body["full_name"] == "Marie Coach"
        assert body["source"] == "manual"
        assert body["tags"] == ["coaching", "bien-être"]

        listed = await client.get("/api/v1/contacts", headers=headers)
        assert listed.status_code == 200
        assert len(listed.json()) == 1

    async def test_update(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        contact_id = (await client.post("/api/v1/contacts", json=PAYLOAD, headers=headers)).json()[
            "id"
        ]
        updated = await client.put(
            f"/api/v1/contacts/{contact_id}",
            json={**PAYLOAD, "full_name": "Marie Martin", "company": "Acme"},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["full_name"] == "Marie Martin"
        assert updated.json()["company"] == "Acme"

    async def test_delete(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        contact_id = (await client.post("/api/v1/contacts", json=PAYLOAD, headers=headers)).json()[
            "id"
        ]
        deleted = await client.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
        assert deleted.status_code == 204
        missing = await client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
        assert missing.status_code == 404

    async def test_empty_name_is_422(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        response = await client.post(
            "/api/v1/contacts", json={**PAYLOAD, "full_name": ""}, headers=headers
        )
        assert response.status_code == 422

    async def test_company_kind(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        response = await client.post(
            "/api/v1/contacts",
            json={"full_name": "Acme SAS", "kind": "company"},
            headers=headers,
        )
        assert response.json()["kind"] == "company"

    async def test_import_requires_auth(self, client: AsyncClient) -> None:
        files = {"file": ("p.pdf", b"%PDF-1.4 x", "application/pdf")}
        assert (await client.post("/api/v1/contacts/import", files=files)).status_code == 401

    async def test_import_returns_a_suggestion(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        files = {"file": ("profile.pdf", b"%PDF-1.4 not-really-a-pdf", "application/pdf")}
        response = await client.post(
            "/api/v1/contacts/import?source=linkedin_pdf", headers=headers, files=files
        )
        assert response.status_code == 200
        assert response.json()["source"] == "linkedin_pdf"

    async def test_cannot_access_another_users_contact(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        contact_id = (await client.post("/api/v1/contacts", json=PAYLOAD, headers=owner)).json()[
            "id"
        ]
        intruder = await _headers(client, "intruder@example.com")
        response = await client.get(f"/api/v1/contacts/{contact_id}", headers=intruder)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "contact.forbidden"
