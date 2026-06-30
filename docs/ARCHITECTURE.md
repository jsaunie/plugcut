# Plugcut — Architecture

## Principles

- **Hexagonal / DDD.** The domain is pure Python with zero framework imports. Everything
  framework-specific (FastAPI, SQLAlchemy, email, PDF) lives at the edges as adapters
  behind ports (abstract interfaces).
- **Bounded contexts.** `identity` (users, auth), `referrals` (the core deal +
  attribution aggregate), `billing` (commission schedules + payments). Contexts talk via
  application services and IDs, never by reaching into each other's tables.
- **Dependency rule.** `interfaces → application → domain`; `infrastructure` implements
  ports defined in `domain`/`application`. Nothing in `domain` imports outward.

## Backend layout

```
backend/app/
├── domain/                 # pure business logic, no framework
│   ├── shared/             # Money, Percentage, base errors, base entity
│   ├── identity/           # User aggregate, password policy (port)
│   ├── referrals/          # Referral aggregate, terms, attribution, repo port
│   └── billing/            # CommissionSchedule, Installment, payment port
├── application/            # use cases (commands/handlers), port interfaces, DTOs
├── infrastructure/         # adapters: SQLAlchemy repos, JWT, email, PDF, config, db
└── interfaces/
    └── api/                # FastAPI routers, pydantic schemas, deps, i18n
```

Layer responsibilities:

- **domain** — aggregates, value objects, invariants, domain services, repository
  *interfaces*. Unit-tested in isolation; no I/O.
- **application** — orchestrates use cases (e.g. `CreateReferral`, `AcceptReferral`,
  `RecordPayment`), defines ports (`EmailSender`, `PdfRenderer`, `Clock`, `UnitOfWork`).
- **infrastructure** — concrete adapters: SQLAlchemy models + repositories + mappers,
  JWT/password hashing, SMTP, PDF, settings (`pydantic-settings`).
- **interfaces/api** — thin FastAPI routers translating HTTP ↔ application DTOs; request
  validation via pydantic schemas; localized error responses.

## Core domain model (referrals + billing)

- **Money** — `Decimal` amount + currency (EUR default), arithmetic with invariants.
- **Percentage** — bounded rate (0–100).
- **Referral** (aggregate root) — referrer, placed person, discreet client ref,
  `CommissionTerms` (daily rate, rate %, duration months, billing frequency), status,
  acceptance timestamps, attribution hash. Owns its state-transition invariants.
- **CommissionSchedule / CommissionInstallment** — derived from the terms: per-period
  due date, expected days, expected amount (`TJM × days × rate`), actual amount once
  days worked are recorded, and status (`PENDING → DUE → PAID`, or `OVERDUE`).

The schedule generator is a pure domain service — the showcase piece for "real FastAPI
domain logic", fully unit-tested without any I/O.

## Frontend layout (feature-sliced)

```
frontend/src/
├── app/        # shell, router, providers, query client
├── pages/      # route-level views (landing, legal, auth, dashboard, deal)
├── features/   # deals/, auth/, billing/ — each with api/ components/ composables/ store/
├── shared/     # ui kit, http client, utils, types
└── i18n/       # vue-i18n setup + locales/{fr,en}.json
```

State via Pinia; server state via TanStack Query; i18n via vue-i18n (FR + EN complete,
no hardcoded user-facing strings).

## Security

- **Passwords**: bcrypt with a per-password salt; only the hash is stored. Verification
  fails closed on a malformed hash.
- **Tokens**: own JWTs (HS256), short-lived access (15 min) + refresh (14 d). The token
  type is encoded and checked, so a refresh token cannot be used as an access token and
  `POST /auth/refresh` rejects an access token presented as a refresh token.
- **CORS**: `CORSMiddleware` allows only the configured SPA origins
  (`PLUGCUT_CORS_ORIGINS`, default `http://localhost:5173`).
- **Authorization**: every referral/installment operation is owner-scoped (a deal is only
  visible and mutable by its referrer), returning `403`/`404` accordingly.
- **Errors**: domain errors carry stable codes mapped to localized messages, so the API
  never leaks internal detail or raw English.
- **Rate limiting**: not implemented in the demo. In production it would sit at the edge
  (reverse proxy / API gateway) or via middleware (e.g. SlowAPI) on the auth endpoints
  (`/auth/login`, `/auth/register`, `/auth/refresh`) to blunt credential stuffing.

## Testing strategy

- **Domain** — fast pure unit tests (pytest), covering invariants and the schedule math.
- **API** — integration tests via httpx `AsyncClient` against the app with a test DB
  (aiosqlite), covering each use case end-to-end.
- **Frontend** — Vitest for composables/components, Playwright for the critical flow
  (signup → create deal → accept → see schedule).
