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
uv run uvicorn app.main:app --reload      # serve API; Swagger at /docs
uv run alembic upgrade head               # apply DB migrations
uv run alembic revision --autogenerate -m "msg"  # generate a migration
```

Frontend (from `frontend/`):

```bash
pnpm install
pnpm dev          # Vite dev server on :5173, proxies /api -> :8000
pnpm build        # type-check (vue-tsc -p tsconfig.app.json) + production build
pnpm lint         # eslint
```

Frontend is Vue 3 + TS, feature-sliced under `src/` (pages, components/landing,
components/shared, i18n, router). Marketing/landing uses bespoke CSS with design tokens
in `src/styles/base.css` (deliberately not utility-first, for a distinctive look). All
user-facing copy goes through vue-i18n (`src/i18n/locales/{fr,en}.json`) — never hardcode
strings.

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

## Design & copy rules (hard requirements)

Avoid "AI-looking" output. These are enforced, not suggestions:

- **No em dashes (—)** in any user-facing copy. Use commas, periods, colons, parentheses,
  or rephrase. (Code comments are exempt but prefer to avoid them too.)
- **No "pastille" badges** — no small colored/glowing dot chips prefixing labels. Eyebrows
  are plain mono uppercase text.
- **No cramped titles** — large multi-line headings use line-height ≈ 1.02–1.08 (the type
  scale in `frontend/src/ui/tokens.css` encodes per-size line-heights). Never 0.98 on
  multi-line display text.
- Reusable UI lives in the **`frontend/src/ui/` design-system package** (tokens + components
  + tests). Landing and app screens compose those, not ad-hoc markup.

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

The MVP is complete and runs end-to-end (backend 77 tests, frontend 20 tests; all gates
green: pytest + ruff + mypy strict, vitest + vue-tsc + eslint).

Backend:
- Domain: `identity` (User), `referrals` (Referral aggregate + state machine +
  attribution hash), `billing` (commission schedule + installments).
- Application: auth (register/authenticate/refresh) + referral use-cases
  (create/list/read, qualify/accept/activate, record payment, agreement).
- Infrastructure: bcrypt, own JWT (access + refresh), SQLAlchemy async repos, Alembic
  migrations (users, referrals, commission_installments), HTML agreement renderer.
- API under `/api/v1`: `auth/{register,login,refresh,me}`, full `referrals` lifecycle +
  `installments/{seq}/pay` + `agreement`; CORS; localized FR/EN errors; Swagger at `/docs`.

Frontend (Vue 3 + TS):
- `src/ui/` design-system package (tokens + UiButton/UiEyebrow/UiCard/UiField/UiTextInput).
- Landing page; auth (login/register, Pinia store, guards, 401-refresh retry); dashboard
  (deal list); create-deal form with live preview; deal detail driving the full lifecycle
  and opening the generated contract; real legal pages. Full FR/EN i18n.

Not built (intentional, post-MVP): real payment rails (Stripe/SEPA), email
reminders/verification, dispute mode, audit-trail UI. See `docs/ROADMAP.md`.
