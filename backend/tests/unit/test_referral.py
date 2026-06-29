"""Unit tests for the Referral aggregate lifecycle and attribution."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.errors import IllegalStateTransition, InvariantViolation
from app.domain.shared.value_objects import Money, Percentage


def make_referral() -> Referral:
    return Referral(
        id=uuid4(),
        referrer_id=uuid4(),
        placed_person_email="dev@example.com",
        client_reference="ACME (discreet)",
        terms=CommissionTerms(
            daily_rate=Money(Decimal("500")),
            commission=Percentage(Decimal("10")),
            duration_months=12,
        ),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def bring_to_signed(referral: Referral) -> None:
    referral.qualify()
    at = datetime(2026, 1, 2, tzinfo=UTC)
    referral.accept_as_referrer(at=at)
    referral.accept_as_placed_person(at=at, placed_person_id=uuid4())


class TestConstruction:
    def test_requires_client_reference(self) -> None:
        with pytest.raises(InvariantViolation):
            ref = make_referral()
            Referral(
                id=ref.id,
                referrer_id=ref.referrer_id,
                placed_person_email=ref.placed_person_email,
                client_reference="   ",
                terms=ref.terms,
                created_at=ref.created_at,
            )

    def test_starts_sent(self) -> None:
        assert make_referral().status is ReferralStatus.SENT


class TestLifecycle:
    def test_happy_path_to_active(self) -> None:
        referral = make_referral()
        bring_to_signed(referral)
        assert referral.status is ReferralStatus.SIGNED
        referral.activate(at=datetime(2026, 2, 1, tzinfo=UTC))
        assert referral.status is ReferralStatus.ACTIVE

    def test_illegal_transition_is_rejected(self) -> None:
        referral = make_referral()
        with pytest.raises(IllegalStateTransition):
            referral.activate(at=datetime(2026, 2, 1, tzinfo=UTC))

    def test_signing_needs_both_acceptances(self) -> None:
        referral = make_referral()
        referral.qualify()
        referral.accept_as_referrer(at=datetime(2026, 1, 2, tzinfo=UTC))
        assert referral.status is ReferralStatus.QUALIFIED
        assert referral.attribution_hash is None

    def test_can_dispute_a_live_deal(self) -> None:
        referral = make_referral()
        bring_to_signed(referral)
        referral.dispute()
        assert referral.status is ReferralStatus.DISPUTED


class TestAttribution:
    def test_hash_set_on_signing(self) -> None:
        referral = make_referral()
        bring_to_signed(referral)
        assert referral.attribution_hash is not None
        assert len(referral.attribution_hash) == 64  # sha256 hex

    def test_hash_is_deterministic_for_same_facts(self) -> None:
        a, b = make_referral(), make_referral()
        # force identical immutable facts
        b.id = a.id
        b.referrer_id = a.referrer_id
        at = datetime(2026, 1, 2, tzinfo=UTC)
        for ref in (a, b):
            ref.qualify()
            ref.accept_as_referrer(at=at)
            ref.accept_as_placed_person(at=at)
        assert a.attribution_hash == b.attribution_hash
