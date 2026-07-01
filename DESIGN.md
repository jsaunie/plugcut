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

- **Direction:** Billet / ticket-office, **light + monochrome**. A calm,
  uncluttered light canvas with white cards that float on soft neutral shadows,
  warm ticket paper for the signature stub, and **near-black for every action and
  emphasis** (no brand hue). Reference: a clean black-on-white app concept, simple
  and airy.
- **Why monochrome:** black-on-white with warm paper reads honest, exact, and
  timeless, which is what money between two people needs. Removing the color spot
  keeps attention on content and form. Reference feel: simple, airy, clean; white
  cards, generous radius, soft shadows, bold black headings, black rounded-rect
  buttons.
- **"The cut" without color:** the cut is carried by **form**, the perforation and
  the tear-off stub, not by a spot color.
- **Decoration level:** intentional. Light surfaces, paper warmth, perforation,
  monospace serials. No gradients-as-decoration, no glowing dot badges, no
  icon-grid filler, no brand hue.
- **Mood:** discreet, exact, trustworthy. A printed receipt you would keep, on a
  clean desk, not a flashy dark dashboard.

## Color

- **Approach:** restrained, light, monochrome. The canvas is near-white; cards are
  white and float on soft shadows. There is no brand hue: every action and emphasis
  is near-black. The only non-neutral is a muted red kept strictly for error states.
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
- **Accent (monochrome, not a hue):** `--accent #17191c` (near-black), for fills,
  focus rings, and emphasis text. Pressed / darkest: `--accent-deep #0b0c0e`. Accent
  text and labels on the light canvas (eyebrows, chips, status): `--accent-on-ink
  #17191c`. Text sitting on the accent fill: `--accent-ink #ffffff`. Note: `--accent`
  and `--solid` are both near-black by design, so every button and emphasis reads as
  one consistent black.
- **Danger:** `--danger #c53a26` (warm brick, the only non-neutral, error states
  only).
- **Text on the canvas:** `--text-on-ink #191b1e` (near-black), muted
  `--muted-on-ink`, hairline `--line-on-ink`.
- **Text on paper:** `--text-on-paper #15130e`, muted `--muted-on-paper`, hairline
  `--line-on-paper`.
- **Buttons:** rounded-rect, `--radius-btn 14px` (not full pill). Primary = near-black
  fill (`accent`/`dark`, both black); tertiary = hairline outline (`ghost`); on a
  dark surface, use the inverted white button (`light`).
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
- **Radii:** `--radius-sm 10px`, `--radius-btn 14px` (buttons), `--radius 20px`
  (cards), `--radius-pill 999px` (chips/toggles).
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
| 2026-07-01 | Go **monochrome**: drop emerald entirely, make `--accent` near-black so every action/emphasis is black; buttons become rounded-rect (`--radius-btn 14px`), added a `light` inverted button for dark surfaces (CTA band goes near-black). Kept a muted red for error states only. | Requested reference palette is pure black/white/gray with black rounded-rect buttons. Setting the `--accent` family to near-black removed the hue everywhere in one edit. "The cut" is now carried by form (perforation/stub), not color. |
