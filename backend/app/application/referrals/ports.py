"""Ports for the referrals use cases."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from app.domain.billing.entities import CommissionInstallment
from app.domain.referrals.entities import Referral

if TYPE_CHECKING:
    from app.application.referrals.dtos import TimelineEntry

__all__ = [
    "AgreementRenderer",
    "EvidenceRenderer",
    "FileStorage",
    "InstallmentRepository",
    "InvoiceRenderer",
    "ReferralRepository",
]


class ReferralRepository(Protocol):
    async def add(self, referral: Referral) -> None: ...

    async def save(self, referral: Referral) -> None: ...

    async def get(self, referral_id: UUID) -> Referral | None: ...

    async def get_by_invitation_token(self, token: str) -> Referral | None: ...

    async def list_for_referrer(self, referrer_id: UUID) -> list[Referral]: ...

    async def list_for_user(self, user_id: UUID) -> list[Referral]: ...


class InstallmentRepository(Protocol):
    async def replace_for_referral(
        self, referral_id: UUID, installments: Iterable[CommissionInstallment]
    ) -> None: ...

    async def list_for_referral(self, referral_id: UUID) -> list[CommissionInstallment]: ...

    async def get(
        self, referral_id: UUID, sequence: int
    ) -> CommissionInstallment | None: ...

    async def update(self, referral_id: UUID, installment: CommissionInstallment) -> None: ...


class FileStorage(Protocol):
    """Stores and retrieves opaque file blobs by key (payment proofs, for now).

    Execution is simulated behind this port: the demo keeps bytes in the database
    so they survive container restarts, but a real deployment could swap in object
    storage (S3, Supabase Storage) without touching the use cases.
    """

    async def save(self, key: str, data: bytes, *, content_type: str) -> None: ...

    async def load(self, key: str) -> bytes | None: ...

    async def delete(self, key: str) -> None: ...


class AgreementRenderer(Protocol):
    """Renders the referral agreement document (HTML) for a signed deal."""

    def render(self, referral: Referral, *, referrer_email: str, locale: str) -> str: ...


class InvoiceRenderer(Protocol):
    """Renders the monthly commission invoice (HTML) for one installment."""

    def render(
        self,
        referral: Referral,
        installment: CommissionInstallment,
        *,
        referrer_email: str,
        locale: str,
    ) -> str: ...


class EvidenceRenderer(Protocol):
    """Renders the dispute evidence pack (HTML): parties, terms, proof, and timeline."""

    def render(
        self,
        referral: Referral,
        *,
        referrer_email: str,
        timeline: list[TimelineEntry],
        locale: str,
    ) -> str: ...
