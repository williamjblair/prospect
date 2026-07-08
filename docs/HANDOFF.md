# Prospect handoff

Everything a fresh agent needs to continue and win the hackathon. Read [AGENTS.md](../AGENTS.md)
first for the mission and the golden rules; this is the deep context.

## 1. Mission and current status

**Goal: win "Built with Claude: Life Sciences"** (Anthropic + Gladstone + Cerebral Valley, Builder
Track, event window Jul 7-13 2026, New Work Only). Gladstone is judging, and the dataset Prospect is
built on is Gladstone's own (the Marson lab's screen). Credibility with domain experts is the whole
game, plus a sharp "Built with Claude" story.

Status: fully built, committed, deployed, and live. Nothing is mid-flight.

- Live: https://prospect-sepia-six.vercel.app
- Repo: github.com/williamjblair/prospect, branch `master`
- Deployed via Vercel CLI: `cd web && vercel --prod --yes --scope constellate-dc388081`
- Signed frontier root: `root_a8b0dcdd4024e12f` (re-derives, 0 drift)
- The gate is green: `final-check`, `verify` 0 drift, `mutation_pack` 0 false admissions,
  `test_skill_parity` 112/0.

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
- **Executable receipt bridge** (`./prospect mcp`): a pure-Python MCP stdio server exposing
  `prospect.receipt.schema`, `prospect.receipt.validate`, and `prospect.receipt.submit`. Submit
  returns a proposal only (`accepted: false`); accepted state still requires the human signing path.
  `python examples/receipt_bridge_client.py` runs the bridge as a tiny external client for judges.
- **Wet-lab validation shortlist** (`frontier/validation_sheet.py`): five evidence-attached,
  on-target, non-canonical, cell-type-specific follow-ups headed by PGGT1B, exported to
  `examples/data/validation_candidates.csv` and [WETLAB_VALIDATION.md](WETLAB_VALIDATION.md).
- **Wet-lab assay packet** (`frontier/lab_packet.py`, `./prospect lab-pack`): five proposal-only
  follow-ups translated into assay design fields: intervention, controls, readouts, exclusion rules,
  and public replay links. Exported to `examples/data/lab_packet.*` and [LAB_PACKET.md](LAB_PACKET.md).
- **Gladstone assay operations bundle** (`frontier/assay_operations.py`, `./prospect assay-ops`):
  deterministic operations layer over the lab packet. It names expected positive, weakening, and
  rejection evidence for each row, keeps all rows `evidence_attached`, and exports
  `examples/data/assay_operations_bundle.*` plus [ASSAY_OPERATIONS_BUNDLE.md](ASSAY_OPERATIONS_BUNDLE.md).
- **Gladstone assay handoff** ([GLADSTONE_ASSAY_HANDOFF.md](GLADSTONE_ASSAY_HANDOFF.md)): one-page
  wet-lab execution note for the top five assay rows, with controls, readouts, stop rules, and replay
  links. It stays proposal only.
- **PGGT1B deep dive** (`frontier/pggt1b_deep_dive.py`, `./prospect pggt1b`): a lab-facing packet for the top shortlist
  gene, exported to `examples/data/pggt1b_deep_dive.json` and [PGGT1B_DEEP_DIVE.md](PGGT1B_DEEP_DIVE.md).
  It keeps status at `evidence_attached`, binds exact local facts, adds an evidence capsule with
  exact stimulation and transfer ratios, adds literature context, names missing evidence before
  acceptance, includes a released-matrix moved-transcript slice, and gives a stimulated CD4+ assay readout.
- **Agent campaign leaderboard** (`frontier/agent_campaign.py`, `./prospect campaign`): 20
  proposal-only follow-ups ranked by frozen Prospect facts, with deterministic review lanes,
  primary readouts, and "what would weaken it" triage fields, exported to
  `examples/data/agent_campaign.*` and [AGENT_CAMPAIGN.md](AGENT_CAMPAIGN.md). It widens the
  single-agent result without moving accepted state.
- **Campaign review appendix** (`frontier/campaign_review.py`, `./prospect campaign-review`):
  deterministic audit questions, lane counts, per-row decisions, and stop rules for all 20 campaign
  hypotheses, exported to `examples/data/agent_campaign_review.*` and
  [AGENT_CAMPAIGN_REVIEW.md](AGENT_CAMPAIGN_REVIEW.md). It helps judges inspect the leaderboard
  without upgrading any row beyond `evidence_attached`.
- **Campaign agent probes** (`loop/campaign_probe.py`, `./prospect campaign-probe`): Claude
  cross-examines the top campaign rows with frozen lookup tools, then Prospect compares the model's
  recommendations to deterministic review lanes. Current run: 8 rows, 25 tool calls, 3 aligned
  recommendations, 4 more-aggressive recommendations, and 1 more-cautious recommendation. Exported to
  `examples/data/campaign_agent_probe.json` and [CAMPAIGN_AGENT_PROBE.md](CAMPAIGN_AGENT_PROBE.md).
  The artifact records exact requested, returned, and missing genes, remains proposal-only, and does
  not move accepted state. For larger experiments, run chunked probes to `/tmp` first:
  `./prospect campaign-probe --limit 20 --chunk-size 4 --out-json /tmp/probe.json --out-doc /tmp/probe.md`.
- **Campaign disagreement triage** (`frontier/campaign_triage.py`, `./prospect campaign-triage`):
  deterministic lab-facing response to the more-aggressive Claude probe rows. Current run: RCC1L,
  MCAT, RWDD2B, and CCDC22 get secondary or capacity assay gates, exported to
  `examples/data/campaign_triage.*` and [CAMPAIGN_TRIAGE.md](CAMPAIGN_TRIAGE.md). It converts model
  pressure into review work, not accepted state.
- **Campaign gate probe** (`loop/campaign_gate_probe.py`, `./prospect campaign-gate-probe`):
  proposal-only pressure test of the disagreement assay gates. It asks whether each gate is sufficient,
  needs another control, or should be lower priority, exported to `examples/data/campaign_gate_probe.json`
  and [CAMPAIGN_GATE_PROBE.md](CAMPAIGN_GATE_PROBE.md).
- **Campaign pressure summary** (`frontier/campaign_pressure_summary.py`, `./prospect campaign-pressure`):
  deterministic synthesis over the campaign, review, Claude probe, triage, and gate-probe artifacts.
  It accounts for what aligned, what became assay gates, what needed controls, and the zero accepted-state
  mutations, exported to `examples/data/campaign_pressure_summary.json` and
  [CAMPAIGN_PRESSURE_SUMMARY.md](CAMPAIGN_PRESSURE_SUMMARY.md).
- **Transfer replay packet** (`frontier/transfer_replay.py`, `./prospect transfer-replay`): compact
  replay object for the signed cross-cell-type finding. It summarizes the Marson + Replogle K562/RPE1
  checker replay as `computationally_reproduced`, reports 377 compared T-cell regulators, and changes
  no accepted state. Exported to `examples/data/transfer_replay_packet.json` and
  [TRANSFER_REPLAY_PACKET.md](TRANSFER_REPLAY_PACKET.md).
- **Substrate replay packet** (`frontier/substrate_replay.py`, `./prospect substrate-replay`):
  protocol-generalization artifact over Marson CD4+ T cells, Replogle K562, and Replogle RPE1.
  It keeps status at `computationally_reproduced`, changes no accepted state, and exports
  `examples/data/substrate_replay_packet.json` plus [SUBSTRATE_REPLAY_PACKET.md](SUBSTRATE_REPLAY_PACKET.md).
- **Scannable findings index** (`frontier/finding_index.py`, `./prospect findings-index`): a
  five-row reader map over the signed finding objects, exported to `examples/data/finding_index.json`
  and [FINDING_INDEX.md](FINDING_INDEX.md). It gives the Findings tab a judge-friendly entry point
  before the evidence tables.
- **Judge packet** (`frontier/judge_packet.py`, `./prospect judge-pack`): one replay manifest with
  the live URL, signed root, gate commands, public data endpoints, artifact counts, and trust-boundary
  summary, exported to `examples/data/judge_packet.json` and [JUDGE_PACKET.md](JUDGE_PACKET.md).
- **One-page judge handout** (`cli/judge_handout.py`, `./prospect judge-handout`): a print-ready
  final-production handout with the live URL, signed root, five-minute path, trust boundary, public
  artifacts to open, replay commands, and human-only actions, exported to [JUDGE_HANDOUT.md](JUDGE_HANDOUT.md).
- **Final submission audit** (`cli/final_submission_audit.py`, `./prospect submission-audit`):
  deterministic upload-readiness packet. It names shipped workstreams, required gates, public
  artifacts, trust boundary, and human-only actions, exported to
  `examples/data/final_submission_audit.json` and [FINAL_SUBMISSION_AUDIT.md](FINAL_SUBMISSION_AUDIT.md).
- **Public release manifest** (`frontier/release_manifest.py`, `./prospect release-manifest`):
  deterministic SHA-256 manifest over the public data artifact surface. It excludes its own hash to
  avoid a circular artifact, exports `examples/data/release_manifest.json`,
  `web/public/data/release_manifest.json`, and [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md), and
  `submit-smoke` recomputes live production hashes against it.
- **Rendered QA packet** (`cli/rendered_qa.py`, `./prospect rendered-qa`): deterministic manual
  browser checklist for the final judge path. It records the production URL, local `8124` fallback,
  desktop and mobile viewport targets, and the required Overview, Findings, Frontier, and Agent tab
  evidence. Exported to `examples/data/rendered_qa_packet.json` and [RENDERED_QA_PACKET.md](RENDERED_QA_PACKET.md).
- **The floor**: `benchmark/mutation_pack.py` admits zero tampered claims; `tests/test_skill_parity.py`
  pins the stdlib Skill checker to the engine.
- **UI**: 6-tab Next.js app on the Observatory design system, ran through an impeccable critique +
  polish pass (Overview rebuilt into an argument, KPI-grid removed, mid-tier headings, skeleton +
  error states, all em dashes swept). The Findings evidence tables now share a responsive evidence
  panel rhythm, with metric strips and mobile-safe rows for the dense scientific tables. The CSS
  vocabulary was pruned back to Prospect/Observatory primitives, and tab or hover feedback now uses
  restrained 180-220ms paint-only transitions.

## 4. Architecture and file map

Pure-Python engine (laptop-runnable, no GPU) + a Next.js viewer. The tracked unit is a change to
accepted state, not a document.

- **`engine/`**: the deterministic checker.
  - `schema.py`: `Claim`, `Verdict`, the 5 statuses (supported/refuted/unsupported/needs_qualification/asserted).
  - `registry.py`: `get_checker(dataset, path)`; `_CHECKERS = {marson, replogle}`. Adding a dataset is one line.
  - `checkers/marson_perturbseq.py`: reads the frozen released DE CSV (never re-runs a DE test).
  - `checkers/replogle_perturbseq.py`: same interface, K562 DE counts. `MAJOR_DE=25`.
- **`frontier/`**: the signed state layer.
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
- **`loop/`**: the AI overlay and agents (need `ANTHROPIC_API_KEY`).
  - `backbone.py` (classify 11,526 genes), `find_surprises.py`, `run.py`/`make_corpus.py`/`bench_summary.py`
    (benchmark), `propose.py` (propose loop), `agent.py` (autonomous agent). `compare.py`/`score.py` are legacy.
- **`receipt/`**: `schema.py` (Receipt), `emit.py` (from findings + agent), `bridge.py`
  (static contract/export), `mcp_server.py` (MCP stdio bridge). Output in `receipts/`.
- **`examples/receipt_bridge_client.py`**: external MCP client demo that discovers the receipt
  contract, validates a committed receipt, and submits it as proposal-only state.
- **`cli/`**: `__main__.py` dispatches `build|verify|sign|check|propose|agent|campaign|campaign-review|campaign-probe|campaign-triage|campaign-gate-probe|campaign-pressure|transfer-replay|substrate-replay|pggt1b|lab-pack|assay-ops|findings-index|demo-pack|judge-handout|submission-audit|release-manifest|rendered-qa|judge-pack|final-check|submit-smoke|submit-pack|receipt`. `./prospect` wraps it.
- **`benchmark/mutation_pack.py`**, **`skill/`** (Agent Skill + stdlib checker), **`tests/`**.
- **`web/`**: `app/page.tsx` (the entire app), `app/globals.css` (Observatory tokens),
  `gen_data.py` (assembles `public/data/frontier.json`, the judge packet, the finding index, the PGGT1B packet, the campaign leaderboard, review appendix, agent probes, disagreement triage, campaign pressure summary, transfer replay packet, substrate replay packet, lab assay packet, assay operations bundle, and static receipt-bridge files),
  `components/graph-view.tsx` (sigma.js).
- **`docs/`**: FINDINGS, PROTOCOL, DEMO, DEMO_RECORDING_RUNBOOK, SUBMISSION, SUBMISSION_FORM_PACKET, HANDOFF, GLADSTONE_ASSAY_HANDOFF. Root: README,
  NEW_WORK, PRODUCT, DESIGN, AGENTS.

### The web app (`web/app/page.tsx`)

One client component. Fetches `/data/frontier.json`, renders a shadcn inset Sidebar shell with 6 tabs:
Overview, Atlas, Network (sigma graph), Frontier (state + receipts + contradictions), Findings (the 5,
each with evidence tables), Agent (the tool-use transcript + signed hypothesis). Peek is the per-gene
slide-over. Regenerate data with `web/gen_data.py`; it reads `frontier/*.jsonl`, the signature, the
benchmark JSONs, `agent_run.json`, `proposal_run.json`, `receipts/receipts.jsonl`, and the validation
shortlist and lab packet. The Frontier tab links the receipt bridge contract, manifest, and bundle;
the Agent tab shows the wet-lab validation shortlist and assay packet.

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
`agent_run*.json`, `receipts/`, `pggt1b_deep_dive.json`, `agent_campaign.*`,
`agent_campaign_review.*`, `campaign_agent_probe.json`, `campaign_triage.*`, `lab_packet.*`,
`finding_index.json`, `judge_packet.json`, `pggt1b_matrix_slice.json`.
`campaign_gate_probe.json`, `campaign_pressure_summary.json`, `assay_operations_bundle.*`,
`transfer_replay_packet.json`, `substrate_replay_packet.json`, `rendered_qa_packet.json`.
Gitignored (regenerable):
`atlas_backbone.json`, `marson_de_full.csv`, `phantom_summary.json`, `.env`,
`frontier/.prospect_signing_key`, `*.h5ad`.

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

Nothing is required; the entry is complete and strong. The small polish follow-ups are shipped:
`web/app/globals.css` no longer carries the retired record-map vocabulary, and tab or hover feedback
uses restrained paint-only transitions in the 180-220ms band.

**Bigger swings (higher ceiling, in rough priority):**
- **Receipt bridge client demo**: shipped as `python examples/receipt_bridge_client.py`.
- **Gladstone assay handoff**: shipped as [GLADSTONE_ASSAY_HANDOFF.md](GLADSTONE_ASSAY_HANDOFF.md).
- **Gladstone assay operations bundle**: shipped as `./prospect assay-ops`.
- **Final submission gate**: shipped as `./prospect final-check`.
- **Campaign gate probe**: shipped as `./prospect campaign-gate-probe`.
- **Campaign pressure summary**: shipped as `./prospect campaign-pressure`.
- **Agent campaign next pass**: shipped for the top eight campaign rows as `./prospect campaign-probe`.
  Disagreement triage is now shipped as `./prospect campaign-triage`. Larger model passes are useful
  only if their requested versus returned coverage is explicit, rationales survive frozen-fact review,
  and downstream triage artifacts are regenerated together.
- **A second frontier**: a different organism or disease dataset behind the same checker interface, to
  prove the substrate generalizes beyond T cells.
- **PGGT1B matrix slice**: shipped. The deep dive now includes a bounded released-matrix slice around
  the gene's strongest moved transcripts.

## 8. Demo and submission

- **Judge quickstart**: [JUDGE_QUICKSTART.md](JUDGE_QUICKSTART.md), a five-minute judge path through
  the live app, replay commands, trust boundary, typed statuses, and public artifacts.
- **Judge handout**: [JUDGE_HANDOUT.md](JUDGE_HANDOUT.md), a one-page path through the live URL,
  signed root, public artifacts to open, replay commands, and human-only actions.
- **Demo script**: [DEMO.md](DEMO.md), a 2-minute beat-by-beat (refusal -> reveal -> number -> moat ->
  loop), runs entirely off the live site. [DEMO_RECORDING_RUNBOOK.md](DEMO_RECORDING_RUNBOOK.md)
  adds exact preflight commands and click beats. [DEMO_TELEPROMPTER.md](DEMO_TELEPROMPTER.md) and
  `./prospect demo-pack` provide the final spoken script and phrases to avoid. Will records the video.
- **Submission text**: [SUBMISSION.md](SUBMISSION.md).
- **Submission form packet**: [SUBMISSION_FORM_PACKET.md](SUBMISSION_FORM_PACKET.md), copy-paste
  fields for title, short description, long description, URLs, demo, verification commands, and
  limitation language.
- **Production smoke**: `./prospect submit-smoke` checks the live alias, judge packet command
  surface, exact public-data parity with the shared `submit-pack` manifest, all public artifact
  endpoints, campaign gate probe, transfer replay packet, lab packet, assay operations bundle,
  receipt bridge manifest, rendered QA packet, and release manifest hashes
  before upload.
- **Submission packet**: `./prospect submit-pack` prints the copy-safe live URL, repo URL, signed
  root, source docs, verification commands, and public artifact links for the final upload.
- The winning arc: open on a model being wrong (the A1BG refusal), reveal the 48%/64% number, show the
  findings recovering known biology (TBX21/GATA3) and catching the field's mislabels (PD-1/TIM-3), show
  the cross-dataset moat, then the autonomous agent producing a novel signed hypothesis, and close on
  the executable receipt boundary, PGGT1B lab-facing packet, and 20-row campaign leaderboard: the AI
  does the work, the receipt crosses as a proposal, the frozen gate and the human key decide what
  becomes state.

## 9. Deeper strategic context (on Will's machine, not in this repo)

For background only. The strategic frame ("Claude Science makes activity cheap; the state layer decides
what becomes state") comes from Will's private memos. Prospect is a fresh, standalone instance of
that idea, built for this event. Keep it standalone.
