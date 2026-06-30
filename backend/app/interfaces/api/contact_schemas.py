"""Pydantic request/response models for the contacts API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.contacts.dtos import ContactData
from app.domain.contacts.entities import Contact
from app.domain.contacts.enums import ContactKind, ContactSource


class ContactWriteRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    kind: ContactKind = ContactKind.PERSON
    headline: str = Field(default="", max_length=300)
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    company: str | None = None
    location: str | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str = ""


class ContactSuggestionResponse(BaseModel):
    """A suggested contact extracted from an uploaded document (for the user to confirm)."""

    full_name: str
    headline: str
    linkedin_url: str | None
    notes: str
    source: str

    @classmethod
    def from_data(cls, data: ContactData, source: ContactSource) -> ContactSuggestionResponse:
        return cls(
            full_name=data.full_name,
            headline=data.headline,
            linkedin_url=data.linkedin_url,
            notes=data.notes,
            source=source.value,
        )


class ContactResponse(BaseModel):
    id: UUID
    full_name: str
    kind: str
    headline: str
    email: str | None
    phone: str | None
    linkedin_url: str | None
    company: str | None
    location: str | None
    tags: list[str]
    notes: str
    source: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, contact: Contact) -> ContactResponse:
        return cls(
            id=contact.id,
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
