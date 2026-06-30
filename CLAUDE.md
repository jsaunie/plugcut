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

## Deployment (read `docs/DEPLOY.md`)

SPA on **Vercel** (static, `frontend/vercel.json` declares the build and rewrites `/api/*`
to the API host), FastAPI as a long-lived container (`backend/Dockerfile`) on
**DigitalOcean App Platform** (spec in `.do/app.yaml`; the image is portable to Railway /
Fly / Render too), data on **Supabase Postgres**. The container runs `alembic upgrade head`
on boot, then serves on `$PORT`; production sets `PLUGCUT_AUTO_CREATE_SCHEMA=false` so
Alembic owns the schema. Local dev stays on SQLite. The engine adds pooler-safe settings
(`pool_pre_ping`, asyncpg `statement_cache_size=0`) only for Postgres URLs.

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

**Read `DESIGN.md` before any visual or UI change.** It is the art-direction source
of truth (direction "Billet Emeraude": softened navy ink + warm ticket paper +
emerald spot color, with the ticket/tear-off-stub as the signature motif). All
colors, fonts, spacing, and aesthetic decisions are defined there and implemented as
CSS variables in `frontend/src/ui/tokens.css`; editing those variables recolors every
page. Do not deviate without explicit approval, and flag any code that drifts from it.

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

Runs end-to-end (backend 130 tests, frontend 25 tests; all gates green: pytest + ruff +
mypy strict, vitest + vue-tsc + eslint).

Backend:
- Domain: `identity` (User), `referrals` (Referral aggregate + state machine + two-sided
  signatures + attribution hash + invitation token + dispute freeze/resolve), `billing`
  (schedule + installments).
- Application: auth (register/authenticate/refresh) + referral use-cases (create, list,
  read, qualify, accept, activate, record payment, stats, agreement, invoice, invitation
  view/sign, dispute, resolve dispute, evidence pack). Reads are owner-or-placed scoped
  (`_load_visible`); mutations are referrer-scoped (`_load_owned`).
- Infrastructure: bcrypt, own JWT (access + refresh), SQLAlchemy async repos, Alembic,
  HTML renderers behind ports (`AgreementRenderer`, `InvoiceRenderer`, `EvidenceRenderer`,
  `ReminderEmailRenderer`), email transport behind an `EmailSender` port (Resend adapter +
  logging fallback when no API key).
- API under `/api/v1`: `auth/{register,login,refresh,me}`, full `referrals` lifecycle +
  `installments/{seq}/{pay,invoice,remind}` + `agreement` + `stats` + `dispute` +
  `dispute/resolve` + `evidence`, public `invitations/{token}`; CORS; localized FR/EN
  errors; Swagger at `/docs`.

Frontend (Vue 3 + TS):
- `src/ui/` design-system package; landing; auth (Pinia, guards, 401-refresh retry);
  dashboard with **KPI stats** + deal list (each deal tagged with the viewer's role);
  create-deal form (with a "from your network" contact picker); deal detail driving the
  full lifecycle (qualify / sign-with-name / invite link / activate / pay / contract /
  invoice / **dispute + resolve + evidence pack** / **payment reminder email**); contacts
  CRM (search + tag filter, PDF import); public **invitation signing page**; real legal
  pages. Full FR/EN i18n.
- **SEO/GEO**: head meta + JSON-LD, OG image, robots/sitemap/llms.txt, `useSeo` per route,
  placeholders for Search Console + pixels (see `docs/ARCHITECTURE.md`).

Collection model: **system of record (Model A)** — Plugcut renders contract + invoices and
tracks payment; money flows peer to peer. Managed collection (Model B, marketplace PSP) is
deferred. **Bidirectional**: a user can owe or be owed; either party can raise a dispute
that freezes the deal until resolved. Payment reminders are sent via **Resend** behind an
`EmailSender` port (logging fallback when `PLUGCUT_RESEND_API_KEY` is unset, so no real
mail in the demo). Not built (intentional, post-MVP): real payment rails (Model B),
payment-proof upload, real e-signature. See `docs/ROADMAP.md`.
