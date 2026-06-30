"""The Referral aggregate root.

A Referral is the private deal between a *referrer* (apporteur) and the *placed person*
(personne placée): who introduced whom, at which client, on what commission terms. It
owns its lifecycle invariants and produces the tamper-evident attribution record that is
the product's core value.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.referrals.enums import ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms, SignatureRequired
from app.domain.shared.errors import IllegalStateTransition, InvariantViolation


class DisputeReasonRequired(InvariantViolation):
    """A dispute was raised without stating a reason."""

    code = "referral.dispute_reason_required"


# Allowed forward transitions. CANCELLED/DISPUTED are reachable from any live state.
_TRANSITIONS: dict[ReferralStatus, set[ReferralStatus]] = {
    ReferralStatus.SENT: {ReferralStatus.IN_DISCUSSION, ReferralStatus.QUALIFIED},
    ReferralStatus.IN_DISCUSSION: {ReferralStatus.QUALIFIED},
    ReferralStatus.QUALIFIED: {ReferralStatus.SIGNED},
    ReferralStatus.SIGNED: {ReferralStatus.ACTIVE},
    ReferralStatus.ACTIVE: {ReferralStatus.COMPLETED},
}
_LIVE = set(_TRANSITIONS) | {ReferralStatus.SIGNED, ReferralStatus.ACTIVE}


def _clean_signature(signature: str) -> str:
    cleaned = signature.strip()
    if not cleaned:
        raise SignatureRequired
    return cleaned


@dataclass(slots=True)
class Referral:
    id: UUID
    referrer_id: UUID
    placed_person_email: str
    client_reference: str
    terms: CommissionTerms
    created_at: datetime
    status: ReferralStatus = ReferralStatus.SENT
    placed_person_id: UUID | None = None
    accepted_by_referrer_at: datetime | None = None
    accepted_by_placed_at: datetime | None = None
    activated_at: datetime | None = None
    attribution_hash: str | None = field(default=None)
    invitation_token: str | None = None
    referrer_signature: str | None = None
    placed_signature: str | None = None
    disputed_at: datetime | None = None
    dispute_reason: str | None = None
    disputed_by: UUID | None = None
    status_before_dispute: ReferralStatus | None = None

    def __post_init__(self) -> None:
        if not self.client_reference.strip():
            raise InvariantViolation("client_reference is required")
        if "@" not in self.placed_person_email:
            raise InvariantViolation("placed_person_email must be an email")

    @property
    def is_fully_accepted(self) -> bool:
        return self.accepted_by_referrer_at is not None and self.accepted_by_placed_at is not None

    def _transition(self, to: ReferralStatus) -> None:
        if to not in _TRANSITIONS.get(self.status, set()):
            raise IllegalStateTransition(f"{self.status.value} -> {to.value}")
        self.status = to

    def mark_in_discussion(self) -> None:
        self._transition(ReferralStatus.IN_DISCUSSION)

    def qualify(self) -> None:
        self._transition(ReferralStatus.QUALIFIED)

    def accept_as_referrer(self, *, at: datetime, signature: str) -> None:
        self.referrer_signature = _clean_signature(signature)
        self.accepted_by_referrer_at = at
        self._sign_if_ready(at=at)

    def accept_as_placed_person(
        self, *, at: datetime, signature: str, placed_person_id: UUID | None = None
    ) -> None:
        self.placed_signature = _clean_signature(signature)
        self.accepted_by_placed_at = at
        if placed_person_id is not None:
            self.placed_person_id = placed_person_id
        self._sign_if_ready(at=at)

    def _sign_if_ready(self, *, at: datetime) -> None:
        if self.status is not ReferralStatus.QUALIFIED or not self.is_fully_accepted:
            return
        self.attribution_hash = self._compute_attribution_hash(signed_at=at)
        self._transition(ReferralStatus.SIGNED)

    def activate(self, *, at: datetime) -> None:
        self._transition(ReferralStatus.ACTIVE)
        self.activated_at = at

    def complete(self) -> None:
        self._transition(ReferralStatus.COMPLETED)

    def cancel(self) -> None:
        if self.status not in _LIVE:
            raise IllegalStateTransition(f"cannot cancel from {self.status.value}")
        self.status = ReferralStatus.CANCELLED

    @property
    def is_frozen(self) -> bool:
        """A disputed deal is frozen: no further lifecycle moves or payments."""
        return self.status is ReferralStatus.DISPUTED

    def dispute(self, *, at: datetime, reason: str, by: UUID) -> None:
        """Flag and freeze the deal. Either party may raise a dispute on a live deal.

        The prior status is recorded so the freeze can be lifted back to it.
        """
        if self.status not in _LIVE:
            raise IllegalStateTransition(f"cannot dispute from {self.status.value}")
        cleaned = reason.strip()
        if not cleaned:
            raise DisputeReasonRequired
        self.status_before_dispute = self.status
        self.status = ReferralStatus.DISPUTED
        self.disputed_at = at
        self.dispute_reason = cleaned
        self.disputed_by = by

    def resolve_dispute(self) -> None:
        """Lift the freeze and restore the deal to the status it held before."""
        if self.status is not ReferralStatus.DISPUTED:
            raise IllegalStateTransition(f"cannot resolve a {self.status.value} deal")
        self.status = self.status_before_dispute or ReferralStatus.ACTIVE
        self.status_before_dispute = None
        self.disputed_at = None
        self.dispute_reason = None
        self.disputed_by = None

    def _compute_attribution_hash(self, *, signed_at: datetime) -> str:
        """Tamper-evident fingerprint of the immutable facts of who introduced whom.

        Any later change to the parties, client, or terms would not match this hash,
        which is the evidence the product offers in case of dispute.
        """
        canonical = "|".join(
            [
                str(self.id),
                str(self.referrer_id),
                self.placed_person_email.lower(),
                self.client_reference.strip().lower(),
                str(self.terms.daily_rate),
                str(self.terms.commission),
                str(self.terms.duration_months),
                (self.referrer_signature or "").lower(),
                (self.placed_signature or "").lower(),
                self.created_at.isoformat(),
                signed_at.isoformat(),
            ]
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
