"""SQLAlchemy implementation of the commission installment repository port."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.billing.entities import CommissionInstallment, PaymentProof
from app.domain.referrals.enums import InstallmentStatus
from app.domain.shared.value_objects import Money
from app.infrastructure.persistence.models import CommissionInstallmentModel


def _proof_to_domain(model: CommissionInstallmentModel) -> PaymentProof | None:
    if (
        model.proof_filename is None
        or model.proof_content_type is None
        or model.proof_size is None
        or model.proof_storage_key is None
        or model.proof_uploaded_at is None
    ):
        return None
    return PaymentProof(
        filename=model.proof_filename,
        content_type=model.proof_content_type,
        size=model.proof_size,
        storage_key=model.proof_storage_key,
        uploaded_at=model.proof_uploaded_at,
    )


def _to_domain(model: CommissionInstallmentModel) -> CommissionInstallment:
    actual_amount = (
        Money(model.actual_amount, model.currency) if model.actual_amount is not None else None
    )
    return CommissionInstallment(
        sequence=model.sequence,
        period_start=model.period_start,
        period_end=model.period_end,
        due_date=model.due_date,
        expected_days=model.expected_days,
        expected_amount=Money(model.expected_amount, model.currency),
        actual_days=model.actual_days,
        actual_amount=actual_amount,
        status=InstallmentStatus(model.status),
        paid_at=model.paid_at,
        last_reminded_at=model.last_reminded_at,
        proof=_proof_to_domain(model),
    )


def _to_model(referral_id: UUID, installment: CommissionInstallment) -> CommissionInstallmentModel:
    proof = installment.proof
    return CommissionInstallmentModel(
        referral_id=referral_id,
        sequence=installment.sequence,
        period_start=installment.period_start,
        period_end=installment.period_end,
        due_date=installment.due_date,
        expected_days=installment.expected_days,
        expected_amount=installment.expected_amount.amount,
        currency=installment.expected_amount.currency,
        actual_days=installment.actual_days,
        actual_amount=installment.actual_amount.amount if installment.actual_amount else None,
        status=installment.status.value,
        paid_at=installment.paid_at,
        last_reminded_at=installment.last_reminded_at,
        proof_filename=proof.filename if proof else None,
        proof_content_type=proof.content_type if proof else None,
        proof_size=proof.size if proof else None,
        proof_storage_key=proof.storage_key if proof else None,
        proof_uploaded_at=proof.uploaded_at if proof else None,
    )


class SqlAlchemyInstallmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_for_referral(
        self, referral_id: UUID, installments: Iterable[CommissionInstallment]
    ) -> None:
        await self._session.execute(
            delete(CommissionInstallmentModel).where(
                CommissionInstallmentModel.referral_id == referral_id
            )
        )
        for installment in installments:
            self._session.add(_to_model(referral_id, installment))

    async def list_for_referral(self, referral_id: UUID) -> list[CommissionInstallment]:
        result = await self._session.scalars(
            select(CommissionInstallmentModel)
            .where(CommissionInstallmentModel.referral_id == referral_id)
            .order_by(CommissionInstallmentModel.sequence)
        )
        return [_to_domain(model) for model in result.all()]

    async def get(
        self, referral_id: UUID, sequence: int
    ) -> CommissionInstallment | None:
        model = await self._session.get(CommissionInstallmentModel, (referral_id, sequence))
        return _to_domain(model) if model is not None else None

    async def update(self, referral_id: UUID, installment: CommissionInstallment) -> None:
        await self._session.merge(_to_model(referral_id, installment))
