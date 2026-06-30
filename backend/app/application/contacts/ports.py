"""Ports for the contacts use cases."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.contacts.entities import Contact


class ContactRepository(Protocol):
    async def add(self, contact: Contact) -> None: ...

    async def save(self, contact: Contact) -> None: ...

    async def get(self, contact_id: UUID) -> Contact | None: ...

    async def list_for_owner(self, owner_id: UUID) -> list[Contact]: ...

    async def delete(self, contact_id: UUID) -> None: ...
