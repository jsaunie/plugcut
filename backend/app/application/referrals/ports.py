"""Ports for the referrals use cases."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from app.domain.billing.entities import CommissionInstallment
from app.domain.referrals.entities import Referral

__all__ = [
    "AgreementRenderer",
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
