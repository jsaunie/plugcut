"""Unit tests for the reputation domain service."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.reputation.entities import Reputation
from app.domain.reputation.service import ReputationService
from app.domain.shared.errors import InvariantViolation
from app.domain.shared.value_objects import Money, Percentage


def _terms() -> CommissionTerms:
    return CommissionTerms(
        daily_rate=Money(Decimal("500")),
        commission=Percentage(Decimal("10")),
        duration_months=12,
    )


def unsealed(referrer_id: UUID) -> Referral:
    """A deal that only one side (or nobody) signed: no attribution hash yet."""
    return Referral(
        id=uuid4(),
        referrer_id=referrer_id,
        placed_person_email="dev@example.com",
        client_reference="ACME",
        terms=_terms(),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def sealed(
    *,
    referrer_id: UUID,
    placed_id: UUID,
    status: ReferralStatus = ReferralStatus.SIGNED,
) -> Referral:
    """A deal both parties signed (carries an attribution hash), forced to `status`."""
    deal = unsealed(referrer_id)
    deal.qualify()
    at = datetime(2026, 1, 2, tzinfo=UTC)
    deal.accept_as_referrer(at=at, signature="Referrer")
    deal.accept_as_placed_person(at=at, signature="Placed", placed_person_id=placed_id)
    assert deal.attribution_hash is not None
    deal.status = status
    return deal


class TestReputationService:
    def test_no_deals_has_no_track_record(self) -> None:
        me = uuid4()
        rep = ReputationService().compute([], subject_id=me)
        assert rep.sealed_deals == 0
        assert rep.trust_score == 0
        assert rep.has_track_record is False

    def test_unsealed_deals_do_not_count(self) -> None:
        me = uuid4()
        rep = ReputationService().compute([unsealed(me), unsealed(me)], subject_id=me)
        assert rep.sealed_deals == 0
        assert rep.trust_score == 0

    def test_counts_role_split(self) -> None:
        me = uuid4()
        deals = [
            sealed(referrer_id=me, placed_id=uuid4()),
            sealed(referrer_id=me, placed_id=uuid4()),
            sealed(referrer_id=uuid4(), placed_id=me),
        ]
        rep = ReputationService().compute(deals, subject_id=me)
        assert rep.sealed_deals == 3
        assert rep.as_referrer == 2
        assert rep.as_placed == 1

    def test_completed_deals_score_higher_than_merely_signed(self) -> None:
        me = uuid4()
        signed = [sealed(referrer_id=me, placed_id=uuid4()) for _ in range(4)]
        completed = [
            sealed(referrer_id=me, placed_id=uuid4(), status=ReferralStatus.COMPLETED)
            for _ in range(4)
        ]
        svc = ReputationService()
        assert (
            svc.compute(completed, subject_id=me).trust_score
            > svc.compute(signed, subject_id=me).trust_score
        )

    def test_disputes_lower_the_score(self) -> None:
        me = uuid4()
        clean = [
            sealed(referrer_id=me, placed_id=uuid4(), status=ReferralStatus.COMPLETED)
            for _ in range(5)
        ]
        with_dispute = [
            *clean[:-1],
            sealed(referrer_id=me, placed_id=uuid4(), status=ReferralStatus.DISPUTED),
        ]
        svc = ReputationService()
        assert (
            svc.compute(with_dispute, subject_id=me).trust_score
            < svc.compute(clean, subject_id=me).trust_score
        )

    def test_perfect_long_record_reaches_100(self) -> None:
        me = uuid4()
        deals = [
            sealed(referrer_id=me, placed_id=uuid4(), status=ReferralStatus.COMPLETED)
            for _ in range(10)
        ]
        assert ReputationService().compute(deals, subject_id=me).trust_score == 100

    def test_score_is_monotonic_in_volume(self) -> None:
        me = uuid4()
        svc = ReputationService()
        scores = [
            svc.compute(
                [sealed(referrer_id=me, placed_id=uuid4()) for _ in range(n)],
                subject_id=me,
            ).trust_score
            for n in range(1, 8)
        ]
        assert scores == sorted(scores)

    def test_all_disputed_clamps_to_zero(self) -> None:
        me = uuid4()
        deals = [
            sealed(referrer_id=me, placed_id=uuid4(), status=ReferralStatus.DISPUTED)
            for _ in range(3)
        ]
        rep = ReputationService().compute(deals, subject_id=me)
        assert rep.disputed_deals == 3
        assert rep.trust_score == 0


class TestReputationInvariants:
    def test_rejects_completed_over_sealed(self) -> None:
        with pytest.raises(InvariantViolation):
            Reputation(
                sealed_deals=1,
                completed_deals=2,
                disputed_deals=0,
                as_referrer=1,
                as_placed=0,
                trust_score=50,
            )

    def test_rejects_roles_not_partitioning_sealed(self) -> None:
        with pytest.raises(InvariantViolation):
            Reputation(
                sealed_deals=3,
                completed_deals=0,
                disputed_deals=0,
                as_referrer=1,
                as_placed=1,
                trust_score=10,
            )

    def test_rejects_out_of_range_score(self) -> None:
        with pytest.raises(InvariantViolation):
            Reputation(
                sealed_deals=1,
                completed_deals=1,
                disputed_deals=0,
                as_referrer=1,
                as_placed=0,
                trust_score=101,
            )
