"""The pure, deterministic reputation service.

Turns a person's referral deals into a trust standing. No framework imports, no I/O:
give it the deals and the subject, it returns a :class:`Reputation`. This is the
non-gameable core of the trust network, so keep it exhaustively unit-tested.
"""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import ReferralStatus
from app.domain.reputation.entities import Reputation

# Trust score weights. Volume caps quickly (a long track record is good, but the
# first honest deals matter most), completion rewards finishing what you start, and
# an open dispute is the strongest negative signal a counterparty can raise.
_VOLUME_CAP = 10
_VOLUME_WEIGHT = 0.55
_COMPLETION_WEIGHT = 0.45
_DISPUTE_WEIGHT = 0.60


class ReputationService:
    def compute(self, deals: Iterable[Referral], *, subject_id: UUID) -> Reputation:
        sealed = [d for d in deals if d.attribution_hash is not None]

        as_referrer = sum(1 for d in sealed if d.referrer_id == subject_id)
        as_placed = sum(1 for d in sealed if d.placed_person_id == subject_id)
        # A sealed deal always involves the subject on exactly one side; guard anyway
        # so a mislabelled caller can't produce a nonsensical reputation.
        counted = as_referrer + as_placed
        sealed_count = counted

        completed = sum(
            1
            for d in sealed
            if d.status is ReferralStatus.COMPLETED and _involves(d, subject_id)
        )
        disputed = sum(
            1
            for d in sealed
            if d.status is ReferralStatus.DISPUTED and _involves(d, subject_id)
        )

        return Reputation(
            sealed_deals=sealed_count,
            completed_deals=completed,
            disputed_deals=disputed,
            as_referrer=as_referrer,
            as_placed=as_placed,
            trust_score=self._score(sealed_count, completed, disputed),
        )

    def _score(self, sealed: int, completed: int, disputed: int) -> int:
        if sealed == 0:
            return 0
        volume = min(sealed / _VOLUME_CAP, 1.0)
        completion = completed / sealed
        dispute_rate = disputed / sealed
        raw = (
            _VOLUME_WEIGHT * volume
            + _COMPLETION_WEIGHT * completion
            - _DISPUTE_WEIGHT * dispute_rate
        )
        return round(max(0.0, min(1.0, raw)) * 100)


def _involves(deal: Referral, subject_id: UUID) -> bool:
    return subject_id in (deal.referrer_id, deal.placed_person_id)
