"""One-off prod maintenance: purge test data and seed demo data for the real user.

Scoped and safe:
  * PURGE  deletes every row owned by users whose email ends in @plugcut-test.dev
           (their referrals, installments, proof blobs, profiles, intros, contacts,
           then the users themselves). Nothing else is touched.
  * SEED   creates realistic contacts + referral deals (and a profile) owned by
           OWNER_EMAIL, driving the real domain use-cases so the data is valid
           (schedules generated, attribution sealed).

Run from backend/ with the production database URL in the environment:

    PLUGCUT_DATABASE_URL="postgresql+asyncpg://...supabase..." \
        uv run python scripts/prod_seed.py --yes

Without --yes it prints what it would do and exits (dry run).
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.application.referrals.dtos import CreateReferralCommand
from app.application.referrals.use_cases import (
    AcceptReferral,
    ActivateReferral,
    CreateReferral,
    QualifyReferral,
    RecordInstallmentPayment,
)
from app.infrastructure.config import Settings
from app.infrastructure.persistence.database import Database
from app.infrastructure.persistence.installment_repository import (
    SqlAlchemyInstallmentRepository,
)
from app.infrastructure.persistence.models import (
    ContactModel,
    IntroRequestModel,
    PaymentProofBlobModel,
    ProfileModel,
    ReferralModel,
    UserModel,
)
from app.infrastructure.persistence.profile_repository import SqlAlchemyProfileRepository
from app.infrastructure.persistence.referral_repository import SqlAlchemyReferralRepository

OWNER_EMAIL = "jean.saunie@meiz.co"
TEST_SUFFIX = "@plugcut-test.dev"


def _clock(moment: datetime):
    return lambda: moment


async def preview_counts(db: Database) -> dict[str, int]:
    """Read-only: how many rows the purge WOULD remove, plus the owner's current data."""
    async with db.session_factory() as session:
        user_ids = list(
            (
                await session.scalars(
                    select(UserModel.id).where(UserModel.email.like(f"%{TEST_SUFFIX}"))
                )
            ).all()
        )

        async def count(model, *where) -> int:  # type: ignore[no-untyped-def]
            return len(list((await session.scalars(select(model.id).where(*where))).all()))

        owner_id = await session.scalar(
            select(UserModel.id).where(UserModel.email == OWNER_EMAIL)
        )
        result: dict[str, int] = {"test_users": len(user_ids)}
        if user_ids:
            result["test_referrals"] = await count(
                ReferralModel,
                (ReferralModel.referrer_id.in_(user_ids))
                | (ReferralModel.placed_person_id.in_(user_ids)),
            )
            result["test_profiles"] = await count(
                ProfileModel, ProfileModel.owner_id.in_(user_ids)
            )
            result["test_contacts"] = await count(
                ContactModel, ContactModel.owner_id.in_(user_ids)
            )
            result["test_intros"] = await count(
                IntroRequestModel,
                (IntroRequestModel.from_user_id.in_(user_ids))
                | (IntroRequestModel.to_user_id.in_(user_ids)),
            )
        result["owner_registered"] = 1 if owner_id is not None else 0
        if owner_id is not None:
            result["owner_referrals_now"] = await count(
                ReferralModel, ReferralModel.referrer_id == owner_id
            )
            result["owner_contacts_now"] = await count(
                ContactModel, ContactModel.owner_id == owner_id
            )
        return result


async def purge_test_data(db: Database) -> dict[str, int]:
    counts: dict[str, int] = {}
    async with db.session_factory() as session:
        user_ids = list(
            (
                await session.scalars(
                    select(UserModel.id).where(UserModel.email.like(f"%{TEST_SUFFIX}"))
                )
            ).all()
        )
        counts["test_users"] = len(user_ids)
        if not user_ids:
            return counts

        referral_ids = list(
            (
                await session.scalars(
                    select(ReferralModel.id).where(
                        (ReferralModel.referrer_id.in_(user_ids))
                        | (ReferralModel.placed_person_id.in_(user_ids))
                    )
                )
            ).all()
        )
        # Proof blobs are keyed by "proof:{referral_id}:{seq}", no FK, so clean by prefix.
        for rid in referral_ids:
            await session.execute(
                delete(PaymentProofBlobModel).where(
                    PaymentProofBlobModel.storage_key.like(f"proof:{rid}:%")
                )
            )
        # Installments cascade on referral delete (FK ondelete=CASCADE).
        r = await session.execute(
            delete(ReferralModel).where(ReferralModel.id.in_(referral_ids))
        )
        counts["referrals"] = r.rowcount or 0
        r = await session.execute(
            delete(ProfileModel).where(ProfileModel.owner_id.in_(user_ids))
        )
        counts["profiles"] = r.rowcount or 0
        r = await session.execute(
            delete(IntroRequestModel).where(
                (IntroRequestModel.from_user_id.in_(user_ids))
                | (IntroRequestModel.to_user_id.in_(user_ids))
            )
        )
        counts["intros"] = r.rowcount or 0
        r = await session.execute(
            delete(ContactModel).where(ContactModel.owner_id.in_(user_ids))
        )
        counts["contacts"] = r.rowcount or 0
        r = await session.execute(delete(UserModel).where(UserModel.id.in_(user_ids)))
        counts["users_deleted"] = r.rowcount or 0
        await session.commit()
    return counts


_CONTACTS = [
    ("Marie Dupont", "person", "Dev backend freelance", "Meiz", ["dev", "backend"]),
    ("Thomas Leroy", "person", "Consultant data", "indépendant", ["data", "consulting"]),
    ("Sophie Martin", "person", "Product designer", "freelance", ["design", "product"]),
    ("Agence Pixel", "company", "Studio web & mobile", "Agence Pixel", ["agence"]),
    ("Karim Benali", "person", "Lead DevOps", "freelance", ["devops", "cloud"]),
]

# (client_reference, placed_email, tjm, rate%, months, state, months_ago)
_DEALS = [
    ("Acme Corp", "marie@example.com", "600", "10", 12, "active", 4),
    ("Globex", "thomas@example.com", "550", "12", 12, "signed", 1),
    ("Initech", "sophie@example.com", "700", "8", 6, "sent", 0),
]


async def seed_owner(db: Database) -> dict[str, int]:
    async with db.session_factory() as session:
        owner_id = await session.scalar(
            select(UserModel.id).where(UserModel.email == OWNER_EMAIL)
        )
        if owner_id is None:
            raise SystemExit(f"Owner {OWNER_EMAIL} is not registered on this database.")

        now = datetime.now(UTC)

        # Profile (so the trust-network features are demoable for the owner).
        profiles = SqlAlchemyProfileRepository(session)
        if await profiles.get_by_owner(owner_id) is None:
            from app.domain.profiles.entities import Profile

            await profiles.add(
                Profile(
                    id=uuid4(),
                    owner_id=owner_id,
                    handle="jean-saunie",
                    display_name="Jean Saunie",
                    created_at=now,
                    updated_at=now,
                    headline="Dev fullstack, apporteur d'affaires",
                    skills=["Vue", "FastAPI", "Python", "DevOps"],
                    bio="Je place et je me fais placer. Discret, contractuel.",
                    available=True,
                )
            )

        # Contacts.
        for full_name, kind, headline, company, tags in _CONTACTS:
            session.add(
                ContactModel(
                    id=uuid4(),
                    owner_id=owner_id,
                    full_name=full_name,
                    kind=kind,
                    headline=headline,
                    company=company,
                    email=None,
                    phone=None,
                    linkedin_url=None,
                    location="Paris",
                    tags=tags,
                    notes="",
                    source="manual",
                    created_at=now,
                    updated_at=now,
                )
            )
        await session.commit()

        # Deals, driven through the real use-cases so schedules + attribution are valid.
        referrals = SqlAlchemyReferralRepository(session)
        installments = SqlAlchemyInstallmentRepository(session)
        for client, placed_email, tjm, rate, months, state, months_ago in _DEALS:
            created = now - timedelta(days=months_ago * 30)
            deal = await CreateReferral(referrals, now=_clock(created)).execute(
                CreateReferralCommand(
                    referrer_id=owner_id,
                    placed_person_email=placed_email,
                    client_reference=client,
                    daily_rate=Decimal(tjm),
                    commission_rate=Decimal(rate),
                    duration_months=months,
                )
            )
            await session.commit()
            if state == "sent":
                continue
            await QualifyReferral(referrals).execute(deal.id, requester_id=owner_id)
            await session.commit()
            accept = AcceptReferral(referrals, installments, now=_clock(created))
            await accept.execute(
                deal.id, requester_id=owner_id, party="referrer", signature="Jean Saunie"
            )
            await accept.execute(
                deal.id, requester_id=owner_id, party="placed", signature="Personne placee"
            )
            await session.commit()
            if state == "active":
                await ActivateReferral(referrals, now=_clock(created)).execute(
                    deal.id, requester_id=owner_id
                )
                await session.commit()
                pay = RecordInstallmentPayment(referrals, installments)
                for seq in (1, 2):
                    await pay.execute(deal.id, seq, requester_id=owner_id)
                await session.commit()
    return {"contacts": len(_CONTACTS), "deals": len(_DEALS)}


async def main(apply: bool) -> None:
    settings = Settings()
    if not settings.database_url.startswith("postgresql"):
        raise SystemExit(
            "Refusing to run: PLUGCUT_DATABASE_URL is not a Postgres URL "
            f"({settings.database_url!r}). Point it at production."
        )
    print(f"Target DB: {settings.database_url.split('@')[-1]}")
    db = Database(settings.database_url)
    if not apply:
        try:
            print("DRY RUN (read-only preview). Nothing is modified.")
            print("Would delete (scoped to @plugcut-test.dev):", await preview_counts(db))
            print("Re-run with --yes to purge and seed", OWNER_EMAIL)
        finally:
            await db.dispose()
        return
    try:
        print("Purging test data...", await purge_test_data(db))
        print("Seeding owner data...", await seed_owner(db))
        print("Done.")
    finally:
        await db.dispose()


if __name__ == "__main__":
    asyncio.run(main(apply="--yes" in sys.argv))
