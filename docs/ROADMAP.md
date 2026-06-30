# Plugcut — Roadmap

The product sells **trust + execution of a private side-deal**, never matchmaking.
Every feature must reinforce one of: *attribution proof*, *a clean agreement*,
*recurring collection*, *discretion*.

## MVP — what the demo must show

- [x] **Auth (API)** — email+password signup/login, own JWT. Email verification stubbed.
- [x] **Auth (UI)** — signup/login screens wired to `/api/v1/auth`, Pinia store, route
      guards, HTTP client with localized errors.
- [x] **Landing page** (marketing) — i18n FR/EN, with interactive commission calculator.
- [ ] **Legal docs** — mentions légales, CGU/CGV, politique de confidentialité (i18n).
- [x] **Create referral deal (API)** — `POST/GET /api/v1/referrals`, owner-scoped,
      computes monthly/total commission. Persisted (SQLAlchemy + Alembic).
- [x] **Create referral deal (UI)** — dashboard lists deals, create form with live
      commission preview, deal detail page with the full schedule.
- [x] **Two-sided acceptance (API)** — qualify, accept (referrer + placed), activate
      transitions; signing seals the SHA-256 attribution hash. Owner-scoped.
- [ ] **Agreement generation** — render the contract (PDF) from the deal.
- [x] **Commission schedule** — generated on signing and **persisted**
      (`commission_installments` table); `GET /referrals/{id}` returns it with
      due/overdue status refreshed.
- [x] **Dashboard (v1)** — lists deals with monthly commission + status. Pipeline
      action buttons in the UI still to come.
- [x] **Mark commission paid (API)** — `POST /referrals/{id}/installments/{seq}/pay`,
      idempotent guard (409 if already paid).

Deal pipeline status: `SENT → IN_DISCUSSION → QUALIFIED → SIGNED → ACTIVE → COMPLETED`
(plus `CANCELLED`, `DISPUTED`).

## Differentiators — more than a handshake + invoice

- [ ] **Immutable attribution record** — who introduced whom, hash-chained /
      tamper-evident, both-party accepted.
- [ ] **Audit trail** per deal (status changes, acceptances, payments).
- [ ] **Dispute mode** — flag, freeze, export an evidence pack.

## Later — modeled now, built later

- [ ] Real recurring collection (Stripe Connect / SEPA) behind the payment port.
- [ ] Email reminders for due commissions.
- [ ] Real e-signature integration.
- [ ] Multi-currency.
- [ ] Accounting / CSV exports.

## Quality bar (non-negotiable from day one)

- DDD / hexagonal layering; pure domain with no framework imports.
- Unit tests on domain, integration tests on API.
- Full i18n FR/EN — front, API error messages, and emails.
- Typed end-to-end (mypy strict, vue-tsc); ruff + eslint clean.
- OpenAPI docs always working at `/docs`.
