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

- **Direction:** Billet / ticket-office, **light-first**. A calm, uncluttered light
  canvas with white cards that float on soft neutral shadows, warm ticket paper for
  the signature stub, near-black reserved for a few high-emphasis actions, and one
  confident spot color (emerald) for "the cut".
- **Why light and not the ink look:** a dark navy canvas read heavy and closed for a
  product about honest, discreet money between two people. A light surface feels
  open, effortless, and trustworthy (clean modern fintech), and it lets the ticket
  paper and the emerald spot do the talking. Reference feel: simple, airy, clean;
  white cards, generous radius, soft shadows, bold black headings.
- **Decoration level:** intentional. Light surfaces, paper warmth, perforation,
  monospace serials, one spot color. No gradients-as-decoration, no glowing dot
  badges, no icon-grid filler.
- **Mood:** discreet, exact, trustworthy. A printed receipt you would keep, on a
  clean desk, not a flashy dark dashboard.

## Color

- **Approach:** restrained and light. The canvas is near-white; cards are white and
  float on soft shadows. One spot color (emerald) carries meaning (the cut, money,
  success). Near-black is only for high-emphasis actions.
- **Canvas (the light surface family, historically named `--ink*`):** page/section
  `--ink #f4f3ef`, raised white cards `--ink-2 #ffffff`, recessed / hover / chips
  `--ink-3 #ecebe4`. (The `--ink*` names are kept so a single token edit still
  recolors every screen; the values are now light.)
- **Paper (warm ticket stock, the signature stub):** `--paper #f3eee2`, recessed
  `--paper-2 #ece5d5`. Reserved for the ticket/stub and the pillar cards, so the
  motif stays distinct from plain white surfaces.
- **Solid dark (near-black, never navy):** `--solid #17191c`, hover `--solid-2
  #24272b`, text on it `--text-on-solid #f5f5f3`. Only for high-emphasis buttons and
  the occasional grounding surface, never as a full-page background.
- **Spot, the cut / money:** `--accent #1f8f63` (emerald), for fills, focus rings,
  and large text. Pressed / accent-text: `--accent-deep #166f4c`. Accent text and
  labels on the light canvas (eyebrows, chips, status): `--accent-on-ink #166f4c`
  (dark emerald, legible on light). Text sitting on the accent fill: `--accent-ink
  #ffffff`.
- **Danger:** `--danger #c53a26` (warm brick, tuned to read on the light canvas).
- **Text on the canvas:** `--text-on-ink #191b1e` (near-black), muted
  `--muted-on-ink`, hairline `--line-on-ink`.
- **Text on paper:** `--text-on-paper #15130e`, muted `--muted-on-paper`, hairline
  `--line-on-paper`.
- **Buttons:** primary action = emerald fill (`accent`); high-emphasis / on-accent
  action = near-black (`dark`); tertiary = hairline outline (`ghost`).
- **Shadows:** soft and neutral so white cards read as floating, not boxed:
  `--shadow-card` for resting cards, `--shadow-lift` on hover, `--shadow-sm` for
  subtle elevation.

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
| 2026-07-01 | Go **light-first**: flip the canvas from navy ink to a near-white surface with white floating cards, soft neutral shadows, near-black for high-emphasis actions; keep warm paper for the stub and emerald as the spot. | The dark navy canvas read heavy/closed; a clean, airy light surface feels more open and trustworthy for honest person-to-person money and matches the reference feel (simple, épuré, propre). Implemented by repurposing the `--ink*` token family to light values (single-edit recolor), adding a `--solid` near-black for buttons, and softening shadows. Kept the bespoke token/design-system architecture (no Tailwind/shadcn needed to achieve the look). |
