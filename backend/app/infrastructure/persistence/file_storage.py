"""SQLAlchemy-backed implementation of the FileStorage port.

Blobs persist in the database so payment proofs survive container restarts (the
API runs on ephemeral disk). A real deployment can swap this for object storage
(S3, Supabase Storage) without touching the use cases.
"""

from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import PaymentProofBlobModel


class SqlAlchemyFileStorage:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, key: str, data: bytes, *, content_type: str) -> None:
        # merge() upserts so re-uploading a proof replaces the previous blob.
        await self._session.merge(
            PaymentProofBlobModel(storage_key=key, content_type=content_type, data=data)
        )

    async def load(self, key: str) -> bytes | None:
        model = await self._session.get(PaymentProofBlobModel, key)
        return model.data if model is not None else None

    async def delete(self, key: str) -> None:
        await self._session.execute(
            delete(PaymentProofBlobModel).where(PaymentProofBlobModel.storage_key == key)
        )
