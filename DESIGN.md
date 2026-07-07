# Prospect design system: the Observatory

Scientific cartography through restraint. A cool paper canvas, indigo ink, one borrowed-gold accent
kept as the soul. Tokens live in `web/app/globals.css`; use them, never raw hex.

## Color (OKLCH, no pure black/white)

- **Canvas:** `--paper` (cool first-light ivory, oklch 97.2% 0.008 248), `--paper-raised`,
  `--paper-recessed`, `--paper-sumi` (the shell frame). Every step holds a whisper of indigo, never
  warm grey or cream.
- **Ink:** `--ink` (indigo body), `--ink-2` (metadata), `--ink-3` (quiet, the text floor at ~4.5:1),
  `--ink-4` (non-text: dividers, placeholders).
- **Accent (kintsugi):** `--brass-gold` / `--gold-ink`. Reserved for the seam where provenance
  changes: the signed root, focus rings, the "Receipt" step. Never decoration, never a CTA glow.
- **Semantic state hues** (diagrams and status badges only, not brand color): `--moss`
  (computationally reproduced), `--brass` (open / evidence-attached), `--field-blue` (in-review / transfer),
  `--cinnabar` (refuted / contradicted), `--stone` (deprecated / neutral). Each has `-tint` (~10%)
  and `-line` (~35%) derivations.
- **Dark mode = Hasui night-band:** `--twilight-indigo` grounds, `--lantern` washes sealed content,
  `--vermilion-bright` marks refutation on dark. Old reads as temperature (`--snow`), not greyout.

## Type

- **Display:** Spectral (serif) for section titles and the hero. Restraint, editorial.
- **Sans:** Space Grotesk for headings, labels, UI. `--font-mono` JetBrains Mono for genes, ids,
  hashes, numbers.
- Classes: `.h1-display` / `.t-display` (Spectral), `.h2-app`, `.t-lede`, `.t-body` / `.t-body-sm`,
  `.t-label` (uppercase, tracked), `.t-caption`, `.t-mono`. Fixed rem scale, not fluid.

## Space and rule (ma)

- Spacing ladder `--space-1..12`; the largest interval marks the boundary between a reading zone and
  an instrument zone (the ma). Vary rhythm, do not pad everything equally.
- **Rules, not borders:** `--rule-faint` inside a component, `--rule` at its edge, `--rule-strong` at
  panel boundaries. Gold hairlines only at provenance thresholds. Cards earn separation from a
  hairline plus a faint cast, never from glow or blur.

## Components

- `.card-paper` (the primary surface, hairline + faint lift), `.chip` (state token, `--tone` var),
  `.btn` (`.btn-secondary` / `.btn-ghost` / `.btn-sm`), `.stat-figure` (the number), state-row.
- Shell: shadcn inset Sidebar on `--paper-sumi` with a `SidebarInset` content card; sticky header
  with a breadcrumb and one search action.
- Genes, ids, hashes, and DE counts are always mono. Status is always a typed chip in its state hue.

## Laws for this project

- Cards are not free. Group with rules and negative space before reaching for another `.card-paper`.
- One accent. Gold is the only non-semantic color, and it is scarce.
- Numbers carry weight; chrome does not. No gradients, no glows, no glass, no gradient text.
