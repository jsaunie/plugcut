"""The Contact aggregate: one entry in a user's private network address book.

Intentionally general: a contact may be a freelancer, a coach, a company, or anyone the
user could place or be placed by. No field is tech-specific.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.contacts.enums import ContactKind, ContactSource
from app.domain.shared.errors import InvariantViolation


class ContactNameRequired(InvariantViolation):
    code = "contact.name_required"


@dataclass(slots=True)
class Contact:
    id: UUID
    owner_id: UUID
    full_name: str
    created_at: datetime
    updated_at: datetime
    kind: ContactKind = ContactKind.PERSON
    headline: str = ""
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    company: str | None = None
    location: str | None = None
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    source: ContactSource = ContactSource.MANUAL

    def __post_init__(self) -> None:
        self.full_name = self.full_name.strip()
        if not self.full_name:
            raise ContactNameRequired
        self.tags = [tag.strip() for tag in self.tags if tag.strip()]
