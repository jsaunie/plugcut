"""Application-level referral errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class ReferralNotFound(DomainError):
    code = "referral.not_found"


class ReferralForbidden(DomainError):
    code = "referral.forbidden"
