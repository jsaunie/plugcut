"""Application-level profile errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class ProfileNotFound(DomainError):
    code = "profile.not_found"
