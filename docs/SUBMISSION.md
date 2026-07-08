# Prospect, Built with Claude: Life Sciences

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## One-paragraph positioning

Prospect is the acceptance layer for AI-generated biology. A Claude Science session can make a reproducible signature or table, but reproducible activity is not accepted scientific state. Prospect turns that activity into a receipt, replays it against frozen released perturbation data, returns typed driver, passenger, contradicted, or not_assayed verdicts, and keeps every submission at `accepted=false` until a frozen replay and a human key accept state.

## What we built

- A signed, content-addressed CD4+ T-cell regulatory frontier from the released Marson CRISPRi Perturb-seq screen.
- A production acceptance service: paste a gene list, signature JSON, ranked markers, or DE table, get a receipt, typed verdicts, a state page, and a public ledger.
- An MCP-shaped connector with tools to discover the schema, submit an artifact, and fetch a verdict.
- A real Claude Science artifact flow: the Sade-Feldman melanoma ICB scRNA-seq signature enters Prospect and receives causal driver/passenger verdicts.
- A context-aware substrate router: T-cell claims route first to Marson CD4+, K562 claims to Replogle K562, RPE1 claims to Replogle RPE1, and frozen ORCS primary T-cell rows shrink uncovered Sade-Feldman genes from 15 to 5.
- A defended PGGT1B dossier that is honest about prior art: PGGT1B is not novel as a T-cell biology axis, but remains a testable CD4 activation-transcriptome hypothesis in released data.

## Results

- 11,526 genes, 37,106 regulatory edges, five signed findings, one signed root.
- 48% of confident AI major-regulator claims contradicted by the measured data, 64% on famous checkpoints and cytokines.
- Real Claude Science signature: 52 genes, 12 `evidence_attached`, 22 `associative_only`, 3 `contradicted`, 15 `not_assayed` in Marson; 5 remain uncovered after ORCS primary T-cell context.
- PGGT1B packet: 3,014 Stim8hr DE genes, 175 Rest DE genes, 1 K562 DE gene, Shifrut primary T-cell ORCS support, STRING partners including FNTA and RABGGTA, ChEMBL target `CHEMBL4135`, and a primary CD4+ CRISPRi protocol with at least 3 donors.
- Novelty downgrade: PMIDs 31302143 and 33207246 already link PGGT1B, GGTase-I, or protein prenylation to T-cell biology. The kept claim is narrower and falsifiable.

## Why Claude matters

Claude is valuable at proposing, searching, and producing reproducible activity. Prospect keeps Claude out of the trust path. The decision to type a claim comes from frozen code over frozen released data. The decision to accept state remains a human key-custody step.

## Judge path

1. Open Overview. Read the first-screen arc: overclaiming, real Claude Science artifact, typed verdicts, PGGT1B payload, run your own claim.
2. Scroll to the Claude Science panel. Compare the internal artifact lane with Prospect's causal lane.
3. Paste a small claim into the run-your-own panel and copy the shareable state link.
4. Open Agent. Inspect the PGGT1B dossier, novelty downgrade, ChEMBL hook, and wet-lab protocol.
5. Open Frontier. Inspect the receipt bridge and MCP boundary.

## Commands

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
cd web && npm run build
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
```

## Public artifacts

- `/data/frontier.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/substrate_coverage_report.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/defended_discovery_endgame_result.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`

Ceiling: computation over released data, not wet-lab or clinical truth.
