"""SQLAlchemy implementation of the AccountEraser port (right to be forgotten).

Deletes everything a user owns across every context, then the user row itself.
Installments cascade with their referral (FK ondelete=CASCADE); proof blobs are
keyed by string so they are cleaned by prefix.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import (
    ContactModel,
    IntroRequestModel,
    PaymentProofBlobModel,
    ProfileModel,
    ReferralModel,
    UserModel,
)


class SqlAlchemyAccountEraser:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def erase(self, user_id: UUID) -> None:
        referral_ids = list(
            (
                await self._session.scalars(
                    select(ReferralModel.id).where(
                        (ReferralModel.referrer_id == user_id)
                        | (ReferralModel.placed_person_id == user_id)
                    )
                )
            ).all()
        )
        for rid in referral_ids:
            await self._session.execute(
                delete(PaymentProofBlobModel).where(
                    PaymentProofBlobModel.storage_key.like(f"proof:{rid}:%")
                )
            )
        await self._session.execute(
            delete(ReferralModel).where(ReferralModel.id.in_(referral_ids))
        )
        await self._session.execute(
            delete(ProfileModel).where(ProfileModel.owner_id == user_id)
        )
        await self._session.execute(
            delete(IntroRequestModel).where(
                (IntroRequestModel.from_user_id == user_id)
                | (IntroRequestModel.to_user_id == user_id)
            )
        )
        await self._session.execute(
            delete(ContactModel).where(ContactModel.owner_id == user_id)
        )
        await self._session.execute(delete(UserModel).where(UserModel.id == user_id))
