# Plugcut

A rail to **formalize and execute private referral commissions between individuals**
(apport d'affaires de particulier à particulier).

Someone you know places a freelancer/company; the **placed person** privately pays the
**referrer** a negotiated cut of their daily rate (e.g. 10% of TJM over 12 months).
Plugcut sells the **agreement, the attribution proof, the recurring collection, and the
discretion** — not the matchmaking. The relationship already exists offline.

## Stack

| Layer    | Tech                                                                          |
| -------- | ----------------------------------------------------------------------------- |
| Frontend | Vue 3 · TypeScript · Vite · Pinia · Vue Router · vue-i18n · TanStack Query     |
| Backend  | FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · Alembic · PostgreSQL · JWT    |
| Quality  | DDD / hexagonal · pytest · ruff · mypy · Vitest · Playwright · i18n (FR/EN)    |

## Layout

```
plugcut/
├── backend/    # FastAPI app — DDD bounded contexts (identity, referrals, billing)
├── frontend/   # Vue 3 SPA — feature-sliced
└── docs/       # ARCHITECTURE.md, ROADMAP.md
```

## Develop

Backend:

```bash
cd backend
uv sync                 # creates .venv with pinned Python, installs deps
uv run pytest           # run tests
uv run uvicorn app.main:app --reload   # API at http://localhost:8000, docs at /docs
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

See `docs/ARCHITECTURE.md` for the design and `docs/ROADMAP.md` for the feature plan.
