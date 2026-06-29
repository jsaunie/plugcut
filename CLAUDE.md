# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Plugcut is

A **personal SaaS** (distinct from Freelance OS) that doubles as a Vue 3 + FastAPI
portfolio piece. It's a rail to **formalize and execute private referral commissions
between individuals**: someone places a freelancer/company, and the **placed person**
privately pays the **referrer** a cut of their daily rate (e.g. 10% of TJM over 12
months). The product sells the **agreement, attribution proof, recurring collection, and
discretion** — NOT matchmaking; the relationship already exists offline. Preserve this
framing — it is the whole reason the model works (see `docs/ROADMAP.md`, `PLUGCUT-brief.txt`).

## Commands

Backend (from `backend/`, needs `~/.local/bin` on PATH for `uv`):

```bash
uv sync                                   # install deps into .venv (Python 3.12 pinned)
uv run pytest -q                          # all tests
uv run pytest tests/unit/test_referral.py # a single test file
uv run ruff check .                       # lint
uv run mypy app                           # strict type-check
uv run uvicorn app.main:app --reload      # serve API (once main.py exists); docs at /docs
```

Frontend (from `frontend/`, once scaffolded): `pnpm install`, `pnpm dev`, `pnpm test`.

## Architecture (read `docs/ARCHITECTURE.md` first)

Hexagonal / DDD. The **domain is pure Python with zero framework imports** — the
dependency rule is `interfaces → application → domain`, and `infrastructure` implements
ports defined inward. Bounded contexts:

- `domain/identity` — users, auth.
- `domain/referrals` — the **Referral aggregate** (core): owns its status state machine
  (`_TRANSITIONS` in `entities.py`) and produces the tamper-evident `attribution_hash`
  on two-sided signing. `CommissionTerms` is the negotiated deal (TJM, %, duration).
- `domain/billing` — `CommissionScheduleService` forecasts recurring `CommissionInstallment`s
  from the terms. This pure, deterministic service is the showcase logic — keep it
  framework-free and exhaustively unit-tested.

Money is always `Decimal` via the `Money` value object (cents, rounded) — never float.
Value objects enforce invariants in `__post_init__`, so an invalid instance can't exist.

## Conventions

- **Domain errors carry a stable `code`** (e.g. `"money.currency_mismatch"`) so the API
  layer maps them to localized (i18n) messages — never leak raw English to users.
- **i18n is mandatory** (FR + EN), front and back, including API error messages and
  emails. No hardcoded user-facing strings. FR is the product's domain language
  (apporteur = referrer, personne placée = placed person, TJM = daily rate).
- Keep `mypy` strict, `ruff` clean, and tests green before considering work done.
- Payments are domain-modeled but execution is **simulated behind a port** — no real
  money flows in the demo.

## Status

Backend domain layer (referrals + billing value objects, aggregate, schedule service)
is built and fully tested (27 unit tests). Not yet built: identity/auth, application
use-cases, SQLAlchemy persistence + Alembic, FastAPI `interfaces/api` layer + `main.py`,
and the entire `frontend/`. Next milestones in `docs/ROADMAP.md`.
