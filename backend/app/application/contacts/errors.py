"""Application-level contact errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class ContactNotFound(DomainError):
    code = "contact.not_found"


class ContactForbidden(DomainError):
    code = "contact.forbidden"
