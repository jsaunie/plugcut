# Design System, Plugcut

Single source of truth for Plugcut's art direction. The implementation lives in
`frontend/src/ui/tokens.css` (every value below is a CSS variable). Components
never hardcode colors or sizes; they reference the tokens, so editing
`tokens.css` recolors all pages at once.

## Product context

- **What this is:** a personal SaaS that formalizes and executes private referral
  commissions between individuals (the placed person privately pays the referrer a
  cut of their daily rate, over time). It sells the agreement, the attribution
  proof, recurring collection, and discretion. Not matchmaking.
- **Who it's for:** people who placed a freelancer or company and want to collect a
  fair, discreet, contractual cut, plus the placed person who agrees to pay it.
- **Space:** fintech-adjacent, contracts and recurring collection, person to person.
- **Project type:** marketing landing plus a logged-in app (dashboard, deal
  lifecycle, contacts CRM, public signing page).

## Memorable thing

> The deal is a billet. The detachable stub is the proof each side keeps.

Every screen leans on one idea: a referral is a ticket. It has a perforated edge
and a tear-off stub. Signing tears off the stub, which carries the
`attribution_hash`, the tamper-evident proof. This is the signature motif and it
should appear across dashboard, contract, invoice, and the public signing page.

## Aesthetic direction

- **Direction:** Billet / ticket-office. Softened ink-navy printing on warm ticket
  paper, with one confident spot color.
- **Why this and not the old look:** the previous black plus acid-lime read
  aggressive and crypto-hype. Money between two people needs to feel reassuring.
  Green ink on warm paper is banknote language: money, trust, calm. That maps
  exactly onto the ticket-with-stub the product already uses.
- **Decoration level:** intentional. Paper warmth, perforation, monospace serials,
  one spot color. No gradients-as-decoration, no glowing dot badges, no icon-grid
  filler.
- **Mood:** discreet, exact, trustworthy. A printed receipt you would keep, not a
  flashy dashboard.

## Color

- **Approach:** restrained. One spot color (emerald) carries meaning (the cut,
  money, success). Everything else is ink and paper.
- **Ink (deep navy print, never pure black):** `--ink #102438`, raised
  `--ink-2 #16314a`, hover `--ink-3 #1e3d59`.
- **Paper (warm ticket stock):** `--paper #f3eee2`, recessed `--paper-2 #ece5d5`.
- **Spot, the cut / money:** `--accent #1f8f63` (emerald), for fills and large
  text. Pressed and accent-text-on-paper: `--accent-deep #166f4c`. Accent
  text/labels on dark ink (eyebrows, chips, status): `--accent-on-ink #4fc78f`
  (light mint, so it stays legible on navy). Text sitting on the accent fill:
  `--accent-ink #ffffff`.
- **Danger:** `--danger #d4452f` (warm brick, tuned to the warm palette).
- **Text on ink:** `--text-on-ink #e9eef0`, muted `--muted-on-ink`, hairline
  `--line-on-ink`.
- **Text on paper:** `--text-on-paper #15130e`, muted `--muted-on-paper`, hairline
  `--line-on-paper`.
- **Surfaces, not a light/dark toggle:** Plugcut is a duotone system. Ink surfaces
  and paper surfaces alternate by section. Use `--accent` as a text color only on
  ink; on paper use it for fills, borders, and focus rings.

## Typography

- **Display / hero:** Bricolage Grotesque (700). Characterful but warm, avoids the
  generic-SaaS look. `--font-display`.
- **Body / UI:** Hanken Grotesk (400 to 700). Friendly, legible, trustworthy.
  `--font-body`.
- **Serial / proof:** Space Mono. Used for eyebrows, serials, hashes, the
  attribution stub. `--font-mono`.
- **Line heights:** display `1.06`, heading `1.12`, body `1.55`. Never crush
  multi-line display titles.
- **Scale:** fluid, `--fs-display-xl` down to `--fs-eyebrow` (see tokens).

## Spacing and layout

- **Base unit:** `0.25rem` steps, `--space-1` through `--space-8`.
- **Density:** comfortable. Generous section padding (`--section-pad`).
- **Max width:** `--maxw 1180px`, gutter `--gutter`.
- **Radii:** `--radius-sm 8px`, `--radius 18px`, `--radius-pill 999px`.
- **The ticket primitive:** cards that represent a deal use the perforation plus
  tear-off stub treatment (see `PerforatedDivider.vue` and the perforation styles
  in `base.css`). Punched notches sit on the perforation line; the stub holds the
  serial, hash, and amount in mono.

## Motion

- **Approach:** intentional, not decorative. Staggered entrance reveal (`.rise`),
  short transitions.
- **Easing:** `--ease-out`. **Duration:** `--dur-fast 0.16s`, `--dur 0.25s`.
- Respect `prefers-reduced-motion` (already handled in `base.css`).

## Hard rules (also in CLAUDE.md)

- No em dashes in user-facing copy.
- No "pastille" badges (no small glowing dot chips). Eyebrows are plain mono
  uppercase.
- No cramped titles on multi-line display text.
- All reusable UI lives in `frontend/src/ui/`. Landing and app compose those.
- All user-facing strings go through vue-i18n (FR plus EN).

## Decisions log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-01 | Adopt direction A "Billet Emeraude": navy ink + warm paper + emerald spot. Replaced black plus acid-lime. | Old palette read aggressive. Money between individuals needs reassurance. Green ink on paper is banknote language (money, trust, calm) and fits the existing ticket/stub motif. Chosen from a 3-way live comparison (A emerald, B cobalt, C coral). |
