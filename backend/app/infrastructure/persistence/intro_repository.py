"""SQLAlchemy implementation of the intro repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.intros.entities import IntroRequest, IntroStatus
from app.infrastructure.persistence.models import IntroRequestModel


def _to_domain(model: IntroRequestModel) -> IntroRequest:
    return IntroRequest(
        id=model.id,
        from_user_id=model.from_user_id,
        to_user_id=model.to_user_id,
        message=model.message,
        created_at=model.created_at,
        status=IntroStatus(model.status),
        responded_at=model.responded_at,
    )


def _to_model(intro: IntroRequest) -> IntroRequestModel:
    return IntroRequestModel(
        id=intro.id,
        from_user_id=intro.from_user_id,
        to_user_id=intro.to_user_id,
        message=intro.message,
        status=intro.status.value,
        created_at=intro.created_at,
        responded_at=intro.responded_at,
    )


class SqlAlchemyIntroRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, intro: IntroRequest) -> None:
        self._session.add(_to_model(intro))

    async def save(self, intro: IntroRequest) -> None:
        await self._session.merge(_to_model(intro))

    async def get(self, intro_id: UUID) -> IntroRequest | None:
        model = await self._session.get(IntroRequestModel, intro_id)
        return _to_domain(model) if model is not None else None

    async def list_inbound(self, to_user_id: UUID) -> list[IntroRequest]:
        result = await self._session.scalars(
            select(IntroRequestModel)
            .where(IntroRequestModel.to_user_id == to_user_id)
            .order_by(IntroRequestModel.created_at.desc())
        )
        return [_to_domain(m) for m in result.all()]

    async def list_outbound(self, from_user_id: UUID) -> list[IntroRequest]:
        result = await self._session.scalars(
            select(IntroRequestModel)
            .where(IntroRequestModel.from_user_id == from_user_id)
            .order_by(IntroRequestModel.created_at.desc())
        )
        return [_to_domain(m) for m in result.all()]

    async def pending_between(
        self, from_user_id: UUID, to_user_id: UUID
    ) -> IntroRequest | None:
        model = await self._session.scalar(
            select(IntroRequestModel).where(
                IntroRequestModel.from_user_id == from_user_id,
                IntroRequestModel.to_user_id == to_user_id,
                IntroRequestModel.status == IntroStatus.PENDING.value,
            )
        )
        return _to_domain(model) if model is not None else None
