"""ORM models. These live only in infrastructure — the domain never imports them."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class ReferralModel(Base):
    __tablename__ = "referrals"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    referrer_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    placed_person_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    placed_person_email: Mapped[str] = mapped_column(String(320))
    client_reference: Mapped[str] = mapped_column(String(255))

    daily_rate_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    duration_months: Mapped[int] = mapped_column(Integer)
    frequency: Mapped[str] = mapped_column(String(20))
    expected_days_per_period: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_by_referrer_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    accepted_by_placed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attribution_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
