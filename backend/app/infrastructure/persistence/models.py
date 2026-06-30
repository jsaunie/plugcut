"""ORM models. These live only in infrastructure — the domain never imports them."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
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
    invitation_token: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True, index=True
    )
    referrer_signature: Mapped[str | None] = mapped_column(String(120), nullable=True)
    placed_signature: Mapped[str | None] = mapped_column(String(120), nullable=True)
    disputed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dispute_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    disputed_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    status_before_dispute: Mapped[str | None] = mapped_column(String(20), nullable=True)


class CommissionInstallmentModel(Base):
    __tablename__ = "commission_installments"

    referral_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("referrals.id", ondelete="CASCADE"), primary_key=True
    )
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    expected_days: Mapped[int] = mapped_column(Integer)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    actual_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(20))
    headline: Mapped[str] = mapped_column(String(300), default="")
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
