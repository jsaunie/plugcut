"""SQLAlchemy implementation of the contact repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.contacts.entities import Contact
from app.domain.contacts.enums import ContactKind, ContactSource
from app.infrastructure.persistence.models import ContactModel


def _to_domain(model: ContactModel) -> Contact:
    return Contact(
        id=model.id,
        owner_id=model.owner_id,
        full_name=model.full_name,
        created_at=model.created_at,
        updated_at=model.updated_at,
        kind=ContactKind(model.kind),
        headline=model.headline,
        email=model.email,
        phone=model.phone,
        linkedin_url=model.linkedin_url,
        company=model.company,
        location=model.location,
        tags=list(model.tags or []),
        notes=model.notes,
        source=ContactSource(model.source),
    )


def _to_model(contact: Contact) -> ContactModel:
    return ContactModel(
        id=contact.id,
        owner_id=contact.owner_id,
        full_name=contact.full_name,
        kind=contact.kind.value,
        headline=contact.headline,
        email=contact.email,
        phone=contact.phone,
        linkedin_url=contact.linkedin_url,
        company=contact.company,
        location=contact.location,
        tags=list(contact.tags),
        notes=contact.notes,
        source=contact.source.value,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


class SqlAlchemyContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, contact: Contact) -> None:
        self._session.add(_to_model(contact))

    async def save(self, contact: Contact) -> None:
        await self._session.merge(_to_model(contact))

    async def get(self, contact_id: UUID) -> Contact | None:
        model = await self._session.get(ContactModel, contact_id)
        return _to_domain(model) if model is not None else None

    async def list_for_owner(self, owner_id: UUID) -> list[Contact]:
        result = await self._session.scalars(
            select(ContactModel)
            .where(ContactModel.owner_id == owner_id)
            .order_by(ContactModel.full_name)
        )
        return [_to_domain(model) for model in result.all()]

    async def delete(self, contact_id: UUID) -> None:
        await self._session.execute(
            delete(ContactModel).where(ContactModel.id == contact_id)
        )
