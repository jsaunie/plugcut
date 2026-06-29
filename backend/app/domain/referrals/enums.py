"""Enumerations for the referrals bounded context."""

from __future__ import annotations

from enum import StrEnum


class BillingFrequency(StrEnum):
    """How often a commission installment falls due."""

    MONTHLY = "monthly"


class ReferralStatus(StrEnum):
    """Lifecycle of a referral deal.

    Mirrors the business pipeline: envoyée -> en discussion -> qualifiée -> signée
    -> active -> terminée, with cancellation and dispute as off-ramps.
    """

    SENT = "sent"
    IN_DISCUSSION = "in_discussion"
    QUALIFIED = "qualified"
    SIGNED = "signed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class InstallmentStatus(StrEnum):
    PENDING = "pending"
    DUE = "due"
    PAID = "paid"
    OVERDUE = "overdue"
