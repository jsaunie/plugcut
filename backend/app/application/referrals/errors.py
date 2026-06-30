"""Application-level referral errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class ReferralNotFound(DomainError):
    code = "referral.not_found"


class ReferralForbidden(DomainError):
    code = "referral.forbidden"


class InstallmentNotFound(DomainError):
    code = "installment.not_found"


class ProofNotFound(DomainError):
    code = "proof.not_found"


class AgreementNotReady(DomainError):
    code = "agreement.not_ready"


class InvitationNotFound(DomainError):
    code = "invitation.not_found"


class DealFrozen(DomainError):
    """The deal is under dispute and frozen, so this action is not allowed."""

    code = "referral.frozen"
