# Prospect handoff

Everything a fresh agent needs to continue and win the hackathon. Read [AGENTS.md](../AGENTS.md)
first for the mission and the golden rules; this is the deep context.

## 1. Mission and current status

**Goal: win "Built with Claude: Life Sciences"** (Anthropic + Gladstone + Cerebral Valley, Builder
Track, event window Jul 7-13 2026, New Work Only). Gladstone is judging, and the dataset Prospect is
built on is Gladstone's own (the Marson lab's screen). Credibility with domain experts is the whole
game, plus a sharp "Built with Claude" story.

Status: fully built, verified, committed, and live. Nothing is mid-flight.

- Live: https://prospect-sepia-six.vercel.app
- Repo: github.com/williamjblair/prospect, branch `master`, HEAD `ea0c552`
- Deployed via Vercel CLI to the Constellate team: `cd web && vercel --prod --yes --scope constellate-dc388081`
- Signed frontier root: `root_a8b0dcdd4024e12f` (re-derives, 0 drift)
- The gate is green: `verify` 0 drift, `mutation_pack` 0 false admissions, `test_skill_parity` 112/0.

## 2. The thesis (why this wins)

Generation got cheap; adjudication did not. On the Marson screen, four frontier models overstate
"major regulator" claims 48% of the time (64% on the genes the field targets most). The bottleneck is
deciding what the field should hold as knowledge. Prospect is the answer: **activity is not state**,
and a **receipt** is the portable object that carries an AI's activity across the boundary
`Activity < Receipt < Proposal < Review < Verification < Accepted < State`, with a frozen verifier and a
human key as the gate. Prospect proves the boundary is real, portable, and survives messy biology.
Reasoning in [PROTOCOL.md](PROTOCOL.md). This is Prospect's own framing, written for the event.

## 3. What shipped (the arc, by phase)

Every finding is a signed, content-addressed object that re-derives from frozen released data.

- **Findings (5), signed into the frontier** ([FINDINGS.md](FINDINGS.md)):
  1. `activation_module` (245 genes): the TCR cascade is silent at Rest, fires on stimulation. The
     screen recovers a textbook pathway from knockout effects alone.
  2. `regulator_vs_effector` (18 genes, contested): PD-1, TIM-3, CTLA-4, LAG-3, IL-2, IFN-y produce
     near-zero DE on confirmed knockdown; they are outputs, not drivers. Each cited to a real PubMed
     review (in `examples/data/literature_citations.json`).
  3. `essentiality_artifact` (139 genes): reach at Rest separates housekeeping (SAGA/Mediator) from
     immune-specific regulation. Reach is not regulation.
  4. `cross_cell_type_transfer`: the same claim through `get_checker("marson")` and
     `get_checker("replogle")`. Essentiality artifacts replicate in non-immune K562 (median 71 DE) and
     RPE1 (~500); the activation module stays inert (K562 median 4). MED19 moves 3,716 genes in K562,
     BCL10 moves 2. The moat, shown.
  5. `regulon_recovery`: known CollecTRI TF targets are 4.03x enriched among the genes each TF's
     knockdown moved (Fisher combined p ~ 1e-26); 63% directional sign agreement; the Th1/Th2 masters
     TBX21 (20x) and GATA3 (8x) recovered; 82 edges where the data overrules the literature's sign.
- **Overclaiming benchmark**: one frozen 220-gene corpus graded across Haiku 4.5, Sonnet 5, Opus 4.8,
  Fable 5. 48% core contradicted (pooled), 64% effector overclaim. `loop/make_corpus.py` +
  `loop/run.py --corpus` + `loop/bench_summary.py`.
- **Claude propose loop** (`loop/propose.py`): Claude proposes regulators, the frozen verifier decides,
  a human signs. First run admitted 6 of 15, rejected FOXP3.
- **Autonomous agent** (`loop/agent.py`): a real Anthropic tool-use loop. Claude calls frozen-data
  tools (search_regulators, check_regulator, cross_cell_type, known_regulon), grounds every fact in a
  lookup, converges on a novel hypothesis, a human signs it. First run: 12 tool calls, 3 rounds, ->
  **PGGT1B** (a stimulation-gated, cell-type-specific regulator with no annotated regulon;
  `evidence_attached`, a hypothesis to test).
- **Receipts** (`receipt/`): 6 portable receipts binding claim + artifact hashes + evidence atoms +
  verifier replay + typed status + human signature. Surfaced in the Frontier tab with the boundary chain.
- **The floor**: `benchmark/mutation_pack.py` admits zero tampered claims; `tests/test_skill_parity.py`
  pins the stdlib Skill checker to the engine.
- **UI**: 6-tab Next.js app on the Observatory design system, ran through an impeccable critique +
  polish pass (Overview rebuilt into an argument, KPI-grid removed, mid-tier headings, skeleton +
  error states, all em dashes swept).

## 4. Architecture and file map

Pure-Python engine (laptop-runnable, no GPU) + a Next.js viewer. The tracked unit is a change to
verified state, not a document.

- **`engine/`** — the deterministic checker.
  - `schema.py`: `Claim`, `Verdict`, the 5 statuses (supported/refuted/unsupported/needs_qualification/asserted).
  - `registry.py`: `get_checker(dataset, path)`; `_CHECKERS = {marson, replogle}`. Adding a dataset is one line.
  - `checkers/marson_perturbseq.py`: reads the frozen released DE CSV (never re-runs a DE test).
  - `checkers/replogle_perturbseq.py`: same interface, K562 DE counts. `MAJOR_DE=25`.
- **`frontier/`** — the signed state layer.
  - `model.py`: `Node/Edge/Contradiction/OpenQuestion/Finding`, `content_id()`, `.freeze()`.
  - `predicates.py`: the 3 finding predicates and their frozen thresholds. Reach-at-Rest is the discriminator.
  - `findings.py`: mints the findings + literature contradictions.
  - `graph_edges.py`: slices gene->gene edges from the 16.8GB Marson matrix over S3 byte-range (no download).
  - `regulon_slice.py`: slices each CollecTRI TF's target set from S3 -> `marson_regulons.json` (~4 min).
  - `regulon_recover.py`: hypergeometric enrichment + directional sign check -> the regulon finding.
  - `transfer.py`: cross-cell-type transfer via both checkers -> the transfer finding.
  - `replogle_extract.py`: turns a Replogle pseudobulk h5ad into a small DE-count CSV.
  - `build.py`: assembles the frontier (nodes/edges/contradictions/open/findings). Loads `regulon.jsonl`.
  - `verify.py`: re-derives every object's content id (the EXACT lane, 0 drift = pass).
  - `sign.py`: the Ed25519 ceremony over the root hash. `--yes` for non-interactive/demo.
- **`loop/`** — the AI overlay and agents (need `ANTHROPIC_API_KEY`).
  - `backbone.py` (classify 11,526 genes), `find_surprises.py`, `run.py`/`make_corpus.py`/`bench_summary.py`
    (benchmark), `propose.py` (propose loop), `agent.py` (autonomous agent). `compare.py`/`score.py` are legacy.
- **`receipt/`** — `schema.py` (Receipt), `emit.py` (from findings + agent). Output in `receipts/`.
- **`cli/`** — `__main__.py` dispatches `build|verify|sign|check|propose|agent|receipt`. `./prospect` wraps it.
- **`benchmark/mutation_pack.py`**, **`skill/`** (Agent Skill + stdlib checker), **`tests/`**.
- **`web/`** — `app/page.tsx` (the entire app, ~950 lines), `app/globals.css` (Observatory tokens),
  `gen_data.py` (assembles `public/data/frontier.json`), `components/graph-view.tsx` (sigma.js).
- **`docs/`** — FINDINGS, PROTOCOL, DEMO, SUBMISSION, HANDOFF. Root: README, NEW_WORK, PRODUCT, DESIGN, AGENTS.

### The web app (`web/app/page.tsx`)

One client component. Fetches `/data/frontier.json`, renders a shadcn inset Sidebar shell with 6 tabs:
Overview, Atlas, Network (sigma graph), Frontier (state + receipts + contradictions), Findings (the 5,
each with evidence tables), Agent (the tool-use transcript + signed hypothesis). Peek is the per-gene
slide-over. Regenerate data with `web/gen_data.py`; it reads `frontier/*.jsonl`, the signature, the
benchmark JSONs, `agent_run.json`, `proposal_run.json`, and `receipts/receipts.jsonl`.

## 5. Data sources (all public)

- **Marson CD4+ T-cell CRISPRi Perturb-seq** (Zhu, Dann, ... Marson 2025), MIT. The classified DE table
  is `examples/data/atlas_backbone.json` (gitignored, derived from the released CSV). The full matrix
  `GWCD4i.DE_stats.h5ad` (16.8 GB) is read over S3 byte-range at
  `s3://genome-scale-tcell-perturb-seq/marson2025_data/` (anon), never downloaded whole.
- **Replogle genome-scale Perturb-seq** K562 + RPE1 (Cell 2022, PMID 35688146), figshare article
  20029387. K562 gwps 374 MB (file 35773217), RPE1 91 MB (file 35775512). Reduced to
  `examples/data/replogle_{k562,rpe1}_de.csv` (committed, small). The big h5ad files live in the
  session scratchpad, gitignored, NOT in the repo; re-download from figshare if you need to re-extract.
- **CollecTRI** human TF->target regulons, pulled live from the OmniPath API ->
  `examples/data/collectri_human.csv` (committed).
- **PubMed** for the literature citations in `examples/data/literature_citations.json`.

Committed derived data (the demo artifacts): `web/public/data/frontier.json`, `frontier/*.jsonl`,
`frontier.sig.json`, `bench_*`, `model_comparison.json`, `replogle_*_de.csv`, `collectri_human.csv`,
`marson_regulons.json`, `benchmark_corpus.json`, `literature_citations.json`, `proposal_run*.json`,
`agent_run*.json`, `receipts/`. Gitignored (regenerable): `atlas_backbone.json`, `marson_de_full.csv`,
`phantom_summary.json`, `.env`, `frontier/.prospect_signing_key`, `*.h5ad`.

## 6. Gotchas

- **Regenerating the frontier**: `frontier/build.py` needs `atlas_backbone.json` (gitignored; produced
  by `loop/backbone.py` from the full Marson CSV). The transfer finding needs `replogle_k562_de.csv`
  (committed). The regulon finding loads `frontier/regulon.jsonl` (committed); regenerating it from
  scratch needs the S3 Marson matrix (`regulon_slice.py`, ~4 min) then `regulon_recover.py`.
- **The signing key** (`frontier/.prospect_signing_key`) is Prospect's own demo Ed25519 key, gitignored,
  auto-generated on first sign. It is not real key custody; it demonstrates the human-signs-the-root
  mechanism. `sign.py --yes` signs non-interactively for the build.
- **Vercel** deploys the working directory, not git; uncommitted changes deploy. The stable alias is
  `prospect-sepia-six.vercel.app`; each `--prod` also mints a random deployment URL and repoints the alias
  (can lag a few seconds).
- **Preview-browser quirk**: `useIsMobile` initializing at width 0 flips the sidebar to a mobile sheet
  during automated screenshots; a real-device non-issue. Reload at a fixed viewport for testing.
- **Costs**: the benchmark + propose + agent hit the Anthropic API (a few dollars total to date; each
  agent run ~ $0.13). Default `claude-opus-4-8`. Fable runs include the server-side refusal fallback to
  Opus (life-sciences prompts can trip safety classifiers).

## 7. Remaining work and opportunities

Nothing is required; the entry is complete and strong. Prioritized options if continuing:

**Polish follow-ups (small, safe):**
- The Findings tab stacks five dense evidence tables; add rhythm / a scannable index between them.
- About 55% of `web/app/globals.css` is dead tokens ported from a prior project (ledger, almanac,
  event-ruler, star, provenance-thread, etc.); safe to prune, lowers the "scaffolding drift" tell.
- Purposeful 150-250ms transitions on tab and hover (currently near-static).

**Bigger swings (higher ceiling, in rough priority):**
- **Receipt export / MCP bridge**: make a receipt emittable by an external workbench (a small MCP or a
  documented JSON contract), so "Claude activity -> receipt -> gated state" is executable, not argued.
  This is the strongest "it's a protocol" move.
- **Agent campaign**: let `loop/agent.py` run many hypotheses, ranked, into a leaderboard of novel
  candidate regulators (with per-candidate verified evidence), instead of one hypothesis.
- **Wet-lab-ready output**: format the top-N testable predictions (the open frontier + agent
  candidates) as a validation-screen-ready sheet a Gladstone lab could act on.
- **A second frontier**: a different organism or disease dataset behind the same checker interface, to
  prove the substrate generalizes beyond T cells.
- **PGGT1B deep-dive**: pull every line of literature + data evidence and write it up publication-grade.

## 8. Demo and submission

- **Demo script**: [DEMO.md](DEMO.md), a 2-minute beat-by-beat (refusal -> reveal -> number -> moat ->
  loop), runs entirely off the live site. Will records the video.
- **Submission text**: [SUBMISSION.md](SUBMISSION.md).
- The winning arc: open on a model being wrong (the A1BG refusal), reveal the 48%/64% number, show the
  findings recovering known biology (TBX21/GATA3) and catching the field's mislabels (PD-1/TIM-3), show
  the cross-dataset moat, then the autonomous agent producing a novel signed hypothesis, and close on
  the receipt boundary: the AI does the work, the frozen gate and the human key decide what becomes state.

## 9. Deeper strategic context (on Will's machine, not in this repo)

For background only. The strategic frame ("Claude Science makes activity cheap; the state layer decides
what becomes state") comes from Will's own memos under `~/Desktop/Constellate/Memos/`, especially
`claude-science-vela-state-layer-memo.md`. Prospect is a fresh, standalone instance of that idea, built
for this event. Do not import or brand anything as Vela/Constellate in this repo.
