# Prospect design system: Lab Console

Prospect should feel like a life-sciences instrument for checking AI gene predictions, not a protocol
ledger. The first read is operational: submit a signature, inspect causal-driver evidence, share a
typed result. Tokens live in `web/app/globals.css`; use them, never raw hex.

## Color

- **Canvas:** pale lab glass surfaces: `--paper`, `--paper-raised`, `--paper-recessed`,
  `--paper-sumi`. They stay cool and clinical, not parchment, cream, or night-sky.
- **Ink:** `--ink` for primary black-blue text, `--ink-2` and `--ink-3` for metadata, `--ink-4`
  for disabled glyphs and quiet dividers.
- **Action blue:** existing compatibility tokens `--brass-gold`, `--gold-ink`, `--gold-line`,
  and `--gold-soft` now resolve to the clinical-blue action family. They are used for focus,
  replay links, and active workflow states.
- **Typed statuses:** `--moss` for `evidence_attached`, `--stone` for `associative_only`,
  `--cinnabar` for `contradicted`, and `--ink-3` or dashed steel for `not_assayed`.

## Type

- Sans-first product typography. `--font-inter` carries headings, labels, buttons, and prose.
- Mono is reserved for genes, ids, counts, replay commands, and typed statuses.
- Display type stays compact. This is a working console, not an editorial landing page.

## Layout

- Top workflow, not a left rail: Check, Evidence, Lead, Receipts. Genes and Graph live behind Explorer.
- The first screen is an assay console: source artifact, Prospect lane, typed counts,
  perturbation matrix, and result sharing.
- Dense data belongs in grouped tables with row rules. Do not turn every row into a card.
- Cards frame major tools only: claim checker, Claude Science panel, evidence inspector.

## Components

- `.console-topbar`, `.console-nav`, `.console-main`, and `.console-context-strip` define the shell.
- `.perturbation-matrix` is the signature visual primitive: rows are genes, columns are conditions,
  final column is typed status.
- `.card-paper`, `.chip`, `.btn`, `.state-row`, and `.stat-figure` remain the reusable primitives,
  retuned to the Lab Console palette.

## Laws

- Lead with biology work: driver, passenger, contradicted, not_assayed.
- Keep receipt mechanics available, but never make them the first visual idea.
- Red is only for earned contradicted driver claims.
- No cosmic motifs, parchment, gold seams, decorative blobs, gradient heroes, or protocol cosplay.
- Every strong word traces to a frozen artifact and a replay command.
