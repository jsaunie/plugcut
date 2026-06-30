"""DTOs for the contacts use cases."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.contacts.enums import ContactKind


@dataclass(frozen=True, slots=True)
class ContactData:
    """The editable fields of a contact (shared by create and update)."""

    full_name: str
    kind: ContactKind = ContactKind.PERSON
    headline: str = ""
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    company: str | None = None
    location: str | None = None
    tags: tuple[str, ...] = ()
    notes: str = ""
