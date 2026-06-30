# Plugcut — Roadmap

The product sells **trust + execution of a private side-deal**, never matchmaking.
Every feature must reinforce one of: *attribution proof*, *a clean agreement*,
*recurring collection*, *discretion*.

## MVP — what the demo must show

- [x] **Auth (API)** — email+password signup/login, own JWT. Email verification stubbed.
- [x] **Auth (UI)** — signup/login screens wired to `/api/v1/auth`, Pinia store, route
      guards, HTTP client with localized errors.
- [x] **Landing page** (marketing) — i18n FR/EN, with interactive commission calculator.
- [x] **Legal docs** — mentions légales, CGU/CGV, politique de confidentialité (real
      FR/EN content, shared LegalLayout, data-driven LegalDocPage).
- [x] **Create referral deal (API)** — `POST/GET /api/v1/referrals`, owner-scoped,
      computes monthly/total commission. Persisted (SQLAlchemy + Alembic).
- [x] **Create referral deal (UI)** — dashboard lists deals, create form with live
      commission preview, deal detail page with the full schedule.
- [x] **Two-sided acceptance + invitation + signature** — referrer signs with a typed
      name; the placed person signs via a public invitation link (`/invitation/:token`,
      no account) with consent. Both signatures seal the SHA-256 attribution hash.
      Public endpoints `GET/POST /api/v1/invitations/{token}`. Verified end-to-end.
- [x] **Agreement generation (API)** — HTML contract behind an `AgreementRenderer` port
      (FR/EN, parties + terms + attribution hash), `GET /referrals/{id}/agreement`,
      available once signed.
- [x] **Commission schedule** — generated on signing and **persisted**
      (`commission_installments` table); `GET /referrals/{id}` returns it with
      due/overdue status refreshed.
- [x] **Dashboard + deal detail** — KPI stats row (pipeline, collected, outstanding +
      overdue, monthly run-rate) backed by `GET /api/v1/referrals/stats`; lists deals;
      detail page drives the full lifecycle (qualify / sign / invite / activate / pay)
      and opens the generated contract.
- [x] **Mark commission paid (API)** — `POST /referrals/{id}/installments/{seq}/pay`,
      idempotent guard (409 if already paid).
- [x] **Monthly commission invoice** — HTML invoice per installment behind an
      `InvoiceRenderer` port (FR/EN), `GET /referrals/{id}/installments/{seq}/invoice`;
      "Facture" button per row. The document that makes the commission a clean,
      justifiable expense (system-of-record model, money stays peer to peer).
- [x] **SEO / GEO foundation** — full `<head>` + JSON-LD (Organization, WebSite,
      SoftwareApplication, FAQPage), branded OG image, robots.txt, sitemap.xml, llms.txt,
      per-route `useSeo`. Placeholders ready for Search Console + analytics pixels.

Deal pipeline status: `SENT → IN_DISCUSSION → QUALIFIED → SIGNED → ACTIVE → COMPLETED`
(plus `CANCELLED`, `DISPUTED`).

## Differentiators — more than a handshake + invoice

- [x] **Immutable attribution record** — who introduced whom, both parties signed
      (typed name + consent), sealed as a SHA-256 fingerprint over the immutable facts.
- [x] **Audit trail** per deal — `GET /referrals/{id}/timeline` synthesizes the history
      (created, acceptances with signer, sealed, activated, payments) from stored
      timestamps; shown as a "Historique" timeline on the deal detail.
- [x] **Dispute mode** — either party flags a sealed deal with a reason, which freezes it
      (no lifecycle moves, no payments) until resolved. The freeze records the prior status
      and lifts back to it on resolution. A downloadable **evidence pack** (HTML, behind an
      `EvidenceRenderer` port, FR/EN) bundles parties, terms, the sealed attribution hash,
      both signatures, the dispute reason, and the full timeline. The dispute shows on the
      audit trail. `POST /referrals/{id}/dispute`, `POST /referrals/{id}/dispute/resolve`,
      `GET /referrals/{id}/evidence`.

## Network address book (contacts)

A private, owner-scoped CRM for the user's own network (not a shared directory, not
matchmaking). General by design: a contact is a person or a company (freelancer, coach,
agency, anyone).

- [x] **Contacts CRUD** — full_name, headline, company, location, email, phone,
      LinkedIn URL, tags, notes; `/api/v1/contacts` owner-scoped; list + create/edit/
      delete UI with a Deals/Contacts nav.
- [x] **PDF import** — upload a LinkedIn profile export or a CV; `POST /contacts/import`
      extracts a suggested contact (pypdf) that pre-fills the form for the user to
      confirm.
- [x] Link a contact to a referral deal — the create-deal form has a "From your network"
      picker listing contacts that have an email (the ones you can actually invite);
      selecting one prefills the placed person's email and the client reference.
- [x] Search / filter by tag — the contacts list has a text search (name, company,
      headline, email) plus one-click tag chips derived from the contacts themselves.

## Collection model (decision)

- **Now (Model A, in place):** Plugcut is the **system of record**. It generates the
  contract + invoices, tracks the schedule, and the money flows **peer to peer** between
  the placed person and the referrer. No regulatory burden. Strengthen with reminders
  and a payment-proof upload.
- **Later (Model B):** managed collection + redistribution via a marketplace PSP
  (Mangopay / Lemonway / Stripe Connect). Plugcut debits, takes its cut, pays out. This
  is the regulated build; do it once demand for the rail is proven.

## Later — modeled now, built later

- [ ] Real recurring collection (Model B, marketplace PSP) behind the payment port.
- [ ] Email reminders for due commissions + payment-proof upload.
- [ ] Real e-signature integration (qualified signature).
- [ ] Multi-currency.
- [ ] Accounting / CSV exports.

## Quality bar (non-negotiable from day one)

- DDD / hexagonal layering; pure domain with no framework imports.
- Unit tests on domain, integration tests on API.
- Full i18n FR/EN — front, API error messages, and emails.
- Typed end-to-end (mypy strict, vue-tsc); ruff + eslint clean.
- OpenAPI docs always working at `/docs`.
