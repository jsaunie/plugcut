"""Billing entities: commission installments and the schedule that groups them."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.referrals.enums import InstallmentStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.errors import IllegalStateTransition, InvariantViolation
from app.domain.shared.value_objects import Money


class AlreadyPaid(IllegalStateTransition):
    code = "installment.already_paid"


class NothingToRemind(IllegalStateTransition):
    """A reminder was requested for an installment that is already settled."""

    code = "installment.nothing_to_remind"


class ProofRequiresPaid(IllegalStateTransition):
    """A payment proof was attached to an installment that is not settled yet."""

    code = "installment.proof_requires_paid"


class EmptyProof(InvariantViolation):
    code = "proof.empty"


class UnsupportedProofType(InvariantViolation):
    code = "proof.unsupported_type"


class ProofTooLarge(InvariantViolation):
    code = "proof.too_large"


# A payment proof is a receipt or bank record. Keep the allowlist tight: documents
# and images only, capped so a stored blob stays small.
MAX_PROOF_BYTES = 5 * 1024 * 1024
ALLOWED_PROOF_TYPES = frozenset({"application/pdf", "image/png", "image/jpeg"})


@dataclass(frozen=True, slots=True)
class PaymentProof:
    """Evidence that a paid installment was actually settled.

    The bytes live behind the ``FileStorage`` port; this value object is the
    metadata kept on the installment, and it cannot exist in an invalid state.
    """

    filename: str
    content_type: str
    size: int
    storage_key: str
    uploaded_at: datetime

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise EmptyProof
        if self.size > MAX_PROOF_BYTES:
            raise ProofTooLarge
        if self.content_type not in ALLOWED_PROOF_TYPES:
            raise UnsupportedProofType
        if not self.filename.strip():
            raise InvariantViolation("a payment proof needs a filename")
        if not self.storage_key:
            raise InvariantViolation("a payment proof needs a storage key")


@dataclass(slots=True)
class CommissionInstallment:
    """One recurring commission owed for a billing period.

    Carries both a *forecast* (``expected_*``, from the terms estimate) and an *actual*
    amount, reconciled once real billed days are recorded.
    """

    sequence: int
    period_start: date
    period_end: date
    due_date: date
    expected_days: int
    expected_amount: Money
    actual_days: int | None = None
    actual_amount: Money | None = None
    status: InstallmentStatus = InstallmentStatus.PENDING
    paid_at: datetime | None = None
    last_reminded_at: datetime | None = None
    proof: PaymentProof | None = None

    def attach_proof(self, proof: PaymentProof) -> None:
        """Attach evidence the installment was settled. Only meaningful once paid."""
        if self.status is not InstallmentStatus.PAID:
            raise ProofRequiresPaid
        self.proof = proof

    @property
    def amount_due(self) -> Money:
        """Actual amount once reconciled, otherwise the forecast."""
        return self.actual_amount if self.actual_amount is not None else self.expected_amount

    def reconcile(self, *, days: int, terms: CommissionTerms) -> None:
        """Record the real billed days and recompute the owed amount."""
        if self.status is InstallmentStatus.PAID:
            raise AlreadyPaid
        self.actual_days = days
        self.actual_amount = terms.commission_for_days(days)

    def mark_paid(self, *, at: datetime | None = None) -> None:
        if self.status is InstallmentStatus.PAID:
            raise AlreadyPaid
        self.status = InstallmentStatus.PAID
        self.paid_at = at

    def mark_reminded(self, *, at: datetime) -> None:
        """Record that a payment reminder was sent. Pointless once paid."""
        if self.status is InstallmentStatus.PAID:
            raise NothingToRemind
        self.last_reminded_at = at

    def refresh_status(self, *, as_of: date) -> None:
        """Move PENDING -> DUE -> OVERDUE based on the due date. Paid is terminal."""
        if self.status is InstallmentStatus.PAID:
            return
        if as_of < self.period_end:
            self.status = InstallmentStatus.PENDING
        elif as_of <= self.due_date:
            self.status = InstallmentStatus.DUE
        else:
            self.status = InstallmentStatus.OVERDUE


@dataclass(slots=True)
class CommissionSchedule:
    """The full set of installments forecast for a referral."""

    installments: list[CommissionInstallment] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.installments:
            raise InvariantViolation("a schedule must have at least one installment")

    @property
    def total_expected(self) -> Money:
        total = self.installments[0].expected_amount * 0  # zero in the right currency
        for installment in self.installments:
            total = total + installment.expected_amount
        return total

    def outstanding(self, *, as_of: date) -> Money:
        total: Money | None = None
        for installment in self.installments:
            installment.refresh_status(as_of=as_of)
            if installment.status is not InstallmentStatus.PAID:
                total = installment.amount_due if total is None else total + installment.amount_due
        return total if total is not None else self.installments[0].expected_amount * 0
