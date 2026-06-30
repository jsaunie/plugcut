"""Contacts use cases: a private, owner-scoped network address book."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.contacts.dtos import ContactData
from app.application.contacts.errors import ContactForbidden, ContactNotFound
from app.application.contacts.ports import ContactRepository
from app.domain.contacts.entities import Contact
from app.domain.contacts.enums import ContactSource


def _utc_now() -> datetime:
    return datetime.now(UTC)


async def _load_owned(
    contacts: ContactRepository, contact_id: UUID, requester_id: UUID
) -> Contact:
    contact = await contacts.get(contact_id)
    if contact is None:
        raise ContactNotFound
    if contact.owner_id != requester_id:
        raise ContactForbidden
    return contact


class CreateContact:
    def __init__(
        self,
        contacts: ContactRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._contacts = contacts
        self._now = now
        self._id_factory = id_factory

    async def execute(
        self,
        owner_id: UUID,
        data: ContactData,
        *,
        source: ContactSource = ContactSource.MANUAL,
    ) -> Contact:
        timestamp = self._now()
        contact = Contact(
            id=self._id_factory(),
            owner_id=owner_id,
            full_name=data.full_name,
            created_at=timestamp,
            updated_at=timestamp,
            kind=data.kind,
            headline=data.headline,
            email=data.email,
            phone=data.phone,
            linkedin_url=data.linkedin_url,
            company=data.company,
            location=data.location,
            tags=list(data.tags),
            notes=data.notes,
            source=source,
        )
        await self._contacts.add(contact)
        return contact


class ListContacts:
    def __init__(self, contacts: ContactRepository) -> None:
        self._contacts = contacts

    async def execute(self, owner_id: UUID) -> list[Contact]:
        return await self._contacts.list_for_owner(owner_id)


class GetContact:
    def __init__(self, contacts: ContactRepository) -> None:
        self._contacts = contacts

    async def execute(self, contact_id: UUID, *, requester_id: UUID) -> Contact:
        return await _load_owned(self._contacts, contact_id, requester_id)


class UpdateContact:
    def __init__(
        self, contacts: ContactRepository, *, now: Callable[[], datetime] = _utc_now
    ) -> None:
        self._contacts = contacts
        self._now = now

    async def execute(
        self, contact_id: UUID, *, requester_id: UUID, data: ContactData
    ) -> Contact:
        contact = await _load_owned(self._contacts, contact_id, requester_id)
        updated = replace(
            contact,
            full_name=data.full_name,
            kind=data.kind,
            headline=data.headline,
            email=data.email,
            phone=data.phone,
            linkedin_url=data.linkedin_url,
            company=data.company,
            location=data.location,
            tags=list(data.tags),
            notes=data.notes,
            updated_at=self._now(),
        )
        await self._contacts.save(updated)
        return updated


class DeleteContact:
    def __init__(self, contacts: ContactRepository) -> None:
        self._contacts = contacts

    async def execute(self, contact_id: UUID, *, requester_id: UUID) -> None:
        await _load_owned(self._contacts, contact_id, requester_id)
        await self._contacts.delete(contact_id)
