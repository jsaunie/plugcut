"""Application-level identity errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class EmailAlreadyRegistered(DomainError):
    code = "identity.email_already_registered"


class InvalidCredentials(DomainError):
    code = "identity.invalid_credentials"


class InactiveUser(DomainError):
    code = "identity.inactive_user"


class InvalidToken(DomainError):
    code = "identity.invalid_token"
