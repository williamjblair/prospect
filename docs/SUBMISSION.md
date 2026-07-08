# Prospect · Built with Claude: Life Sciences

**A computationally reproduced regulatory frontier of human CD4+ T-cell biology.**

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app) ·
Repo: [github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

## The problem

AI generates biology faster than anyone can check it. A model asserts that a gene is a key
regulator or a promising target in a sentence; confirming that against the data takes longer than
most people spend. So overstated claims walk into slides, grants, and papers. On the Marson lab's
own CD4+ T-cell screen, four frontier models overstate "major regulator" claims 48% of the time,
and 64% of the time on the genes the field targets most.

The deeper idea is a boundary: `Activity < Receipt < Proposal < Review < Verification < Accepted <
State`. Generation is cheap; replayable, human-accepted state is the scarce thing. The
full reasoning is in [docs/PROTOCOL.md](PROTOCOL.md).

## What we built

Prospect is a linked, content-addressed graph of gene regulation where every node and edge
re-derives from released CRISPRi Perturb-seq data and carries a human signature. No model enters
the graph on its own word. On top of it:

- **Five signed findings** mined deterministically from the released table: the TCR activation
  module recovered from perturbation alone; the field's most-targeted genes shown to be effectors
  rather than drivers, each cited to PubMed; the essentiality artifact a naive ranking mistakes for
  immunology; a cross-cell-type transfer confirming the split against two non-immune cell types; and
  recovery of known TF regulons (CollecTRI) from perturbation alone, at 4x enrichment (p≈1e-26).
- **An overclaiming benchmark** across Haiku, Sonnet, Opus, and Fable on one frozen corpus.
- **A scannable findings index** over the five signed finding objects, so a judge can see the arc
  before reading evidence tables: recover known biology, catch overclaiming, resist the artifact,
  transfer the checker, recover regulons.
- **A judge packet**: `prospect judge-pack` emits one manifest with the live URL, signed root,
  replay commands, public data endpoints, artifact counts, and trust-boundary summary.
- **A closed loop and an autonomous agent**: `prospect propose` (Claude proposes, the verifier
  decides, a human signs) and `prospect agent` (a real tool-use loop where Claude searches and
  verifies against frozen data, converging on a novel hypothesis).
- **Portable receipts and MCP bridge**: `prospect receipt` emits the activity-to-state bridge object,
  and `prospect mcp` lets an external workbench discover, validate, and submit receipts as proposals.
  Submission never moves accepted state on its own.
- **Wet-lab validation shortlist**: a conservative sheet of evidence-attached follow-up hypotheses,
  headed by PGGT1B, formatted for stimulated CD4+ perturbation validation.
- **Wet-lab assay packet**: `prospect lab-pack` translates the top follow-ups into intervention,
  control, readout, exclusion, and replay fields for a Gladstone-facing assay handoff.
- **PGGT1B deep dive**: `prospect pggt1b` emits a lab-facing packet with exact frozen facts,
  a four-step evidence capsule, external literature context, caveats, and an assay readout while
  keeping the claim at `evidence_attached`.
- **Agent campaign leaderboard**: `prospect campaign` widens the single-agent result into 20
  proposal-only follow-ups, each ranked from frozen facts and held at `evidence_attached`.
- **Campaign review appendix**: `prospect campaign-review` adds deterministic audit questions,
  lane counts, per-row decisions, and stop rules for the 20-row campaign without accepting any row.
- **Campaign agent probes**: `prospect campaign-probe` has Claude cross-examine the top campaign
  rows with frozen tools, then compares its recommendations to deterministic review lanes. It
  remains proposal only.
- **Campaign disagreement triage**: `prospect campaign-triage` turns the more-aggressive Claude
  rows into assay gates, preserving the deterministic review decision and the proposal-only boundary.

## How it uses Claude

- **Measured**: the benchmark grades Claude and other frontier models against ground truth, turning
  overclaiming into a number the substrate catches deterministically.
- **In the loop**: `prospect propose` and `prospect agent` use Claude (Opus 4.8, adaptive thinking,
  the agent via real SDK tool-use) to propose and investigate. The frozen verifier gates every
  claim and a human key accepts. Claude is useful, and never in the trust path.
- **As a pressure test**: `prospect campaign-probe` asks Claude to challenge the campaign ranking
  using frozen lookups, then Prospect records where it aligns or pushes harder than the deterministic
  review.
- **As triage input**: model pressure becomes review work, not state. `prospect campaign-triage`
  records the assay gates required before disagreement rows earn more capacity.
- **For literature**: finding contradictions are grounded in real reviews resolved through PubMed.
- **To build**: the whole system was written in Claude Code during the event.

## Results

- 11,526 genes, 37,106 regulatory edges, five signed findings, one signed root, 0 drift on re-derivation.
- 48% of confident AI major-regulator claims contradicted (4 models); 64% on checkpoints and cytokines.
- Regulon recovery: known CollecTRI targets are 4x enriched among the genes each TF's knockdown moved
  (Fisher p≈1e-26); the Th1/Th2 masters TBX21 and GATA3 recovered from perturbation alone.
- Cross-cell transfer: essentiality artifacts move a median of 71 genes in K562, the activation
  module 4. MED19 moves 3,716; BCL10 moves 2.
- The agent made 12 frozen-data tool calls over 3 rounds and converged on PGGT1B, a stimulation-gated,
  cell-type-specific regulator with no annotated regulon; a human signed the hypothesis to test.
- PGGT1B has 3,014 DE genes at Stim8hr with on-target knockdown, 175 at Rest, 1 in K562, and 0
  CollecTRI targets. Literature context points to PGGT1B-linked T-cell prenylation, RHOA, RAC, and
  TCR-dependent programming. The evidence capsule adds the exact 17.22x Stim8hr-to-Rest ratio,
  the 3014x Stim8hr-to-K562 transfer check, and a released-matrix slice of 671 moved transcripts
  headed by KLF2, RHOB, IL5, and IL10. The Prospect claim remains a hypothesis to test.
- The campaign leaderboard ranks 20 non-canonical, cell-type-specific follow-ups with on-target
  stimulated evidence. It is proposal only; accepted state still requires the frozen gate and human key.
- The campaign review appendix turns that leaderboard into an auditable assay queue: one top
  assay-design row, six clean-specificity rows, six late-activation follow-ups, five ranked backups,
  and two regulon anchors, each with stop rules.
- The campaign agent probe ran 16 frozen-tool calls over the top five rows. Claude aligned on
  PGGT1B and MCAT, and pushed more aggressively on RCC1L, RWDD2B, and CCDC22. The comparison is
  visible, but state does not move.
- The disagreement triage turns those three more-aggressive rows into secondary or capacity assay
  queues with orthogonal knockdown and transfer gates.
- The receipt bridge is executable over MCP stdio: external activity can cross into a receipt
  proposal, but accepted state still requires the human signing path.
- The validation shortlist ranks five non-canonical, cell-type-specific, on-target stimulated
  follow-ups for a Gladstone-facing perturbation screen.
- The lab packet turns those five rows into assay-ready fields while keeping each row proposal only.
- The mutation-pack floor admits zero tampered claims; a parity test pins the Skill checker to the engine.

## Public artifacts

- `/data/frontier.json`
- `/data/judge_packet.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign_review.json`
- `/data/campaign_agent_probe.json`
- `/data/campaign_triage.json`
- `/data/lab_packet.json`

## Verify it yourself

```bash
./prospect verify                 # re-derive 53k objects from frozen data, 0 drift
./prospect agent                  # autonomous agent: search → verify → converge on a hypothesis
./prospect receipt                # emit the activity → state receipts
./prospect mcp                    # expose the receipt bridge over MCP stdio
./prospect campaign               # build the proposal-only campaign leaderboard
./prospect campaign-review        # build the campaign review appendix
./prospect campaign-probe         # run Claude probes against campaign rows
./prospect campaign-triage        # turn probe disagreements into assay gates
./prospect pggt1b                 # write the PGGT1B evidence packet
./prospect lab-pack               # build the wet-lab assay packet
./prospect findings-index         # build the scannable finding index
./prospect judge-pack             # build the judge packet manifest
python frontier/validation_sheet.py # write the wet-lab validation shortlist
python benchmark/mutation_pack.py # zero tampered claim is ever admitted
python tests/test_skill_parity.py # Skill checker matches the engine
```

## Stack

Python (deterministic engine, frozen-table checkers, Ed25519 signing, receipts), Next.js 16 +
Tailwind + sigma.js (the frontier viewer, a custom observatory design system), Anthropic SDK for the
benchmark, the propose loop, and the agent. Public data only. MIT-licensed. See `NEW_WORK.md`.
