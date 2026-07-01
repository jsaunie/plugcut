"""Reputation value objects."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.errors import InvariantViolation


@dataclass(frozen=True, slots=True)
class Reputation:
    """A freelancer's trust standing, computed from their signed referral deals.

    Every count is over *sealed* deals only (both parties signed, so an
    ``attribution_hash`` exists). An instance cannot hold contradictory numbers.
    """

    sealed_deals: int
    completed_deals: int
    disputed_deals: int
    as_referrer: int
    as_placed: int
    trust_score: int

    def __post_init__(self) -> None:
        for name, value in (
            ("sealed_deals", self.sealed_deals),
            ("completed_deals", self.completed_deals),
            ("disputed_deals", self.disputed_deals),
            ("as_referrer", self.as_referrer),
            ("as_placed", self.as_placed),
        ):
            if value < 0:
                raise InvariantViolation(f"{name} cannot be negative")
        if self.completed_deals > self.sealed_deals:
            raise InvariantViolation("completed_deals cannot exceed sealed_deals")
        if self.disputed_deals > self.sealed_deals:
            raise InvariantViolation("disputed_deals cannot exceed sealed_deals")
        if self.as_referrer + self.as_placed != self.sealed_deals:
            raise InvariantViolation("roles must partition sealed_deals")
        if not 0 <= self.trust_score <= 100:
            raise InvariantViolation("trust_score must be within 0..100")

    @property
    def has_track_record(self) -> bool:
        return self.sealed_deals > 0
