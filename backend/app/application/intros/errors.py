"""Application-level intro errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class IntroNotFound(DomainError):
    code = "intro.not_found"


class IntroForbidden(DomainError):
    code = "intro.forbidden"


class IntroAlreadyPending(DomainError):
    code = "intro.already_pending"


class ProfileRequired(DomainError):
    """You must have a profile (be a network member) before requesting an intro."""

    code = "intro.profile_required"
