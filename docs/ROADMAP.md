# Plugcut — Roadmap

The product sells **trust + execution of a private side-deal**, never matchmaking.
Every feature must reinforce one of: *attribution proof*, *a clean agreement*,
*recurring collection*, *discretion*.

## MVP — what the demo must show

- [x] **Auth (API)** — email+password signup/login, own JWT. Email verification stubbed.
- [ ] **Auth (UI)** — signup/login screens wired to `/api/v1/auth`.
- [x] **Landing page** (marketing) — i18n FR/EN, with interactive commission calculator.
- [ ] **Legal docs** — mentions légales, CGU/CGV, politique de confidentialité (i18n).
- [ ] **Create referral deal** — referrer, placed person, discreet client reference,
      TJM (daily rate), commission %, duration, billing frequency.
- [ ] **Two-sided acceptance** — invite counterparty by link; both accept → attribution
      proof (timestamped, both-party signed).
- [ ] **Agreement generation** — render the contract (PDF) from the deal.
- [ ] **Commission schedule** — auto-generate recurring installments from the terms.
- [ ] **Dashboard** — deal pipeline + commissions due / paid / overdue.
- [ ] **Mark commission paid** — manual, with audit trail.

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
