# Prospect, Built with Claude: Life Sciences

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## One Sentence

Prospect tells biologists which genes in an AI-generated prediction list behave as causal drivers,
which are passengers, and which driver claims the perturbation data contradicts.

## Why It Matters

Reproducible is not verified. Claude Science and similar tools can preserve an artifact, its code,
environment, and review trail. That makes the activity reproducible. Prospect asks the next question:
does the claim survive an independent frozen perturbation gate, and should it become an accepted record?

## What We Built

- A paste-and-connector acceptance layer for gene lists, signatures, ranked markers, and DE tables.
- A real Claude Science artifact flow using a Sade-Feldman melanoma ICB scRNA-seq signature.
- A frozen causal gate over the released Marson primary human CD4+ CRISPRi Perturb-seq screen.
- Typed driver, passenger, contradicted, and not_assayed verdicts, always `accepted=false`.
- A signed CD4+ evidence graph and MCP receipt bridge.
- One honest PGGT1B hypothesis worth testing, with mechanism, prior-art caveats, and a refutation experiment.

## Results

- Real Claude Science export: 52 genes typed by Prospect.
- Associative-signature split: 12 `evidence_attached`, 25 `associative_only`, 0 `contradicted`, 15 `not_assayed`.
- Overclaiming benchmark: 48% of confident AI major-regulator claims contradicted by the measured data,
  64% on famous checkpoints and cytokines.
- PGGT1B: 3,014 Stim8hr DE genes, 175 Rest DE genes, 1 K562 DE gene, Shifrut primary T-cell ORCS
  support, STRING partners including FNTA and RABGGTA, ChEMBL target `CHEMBL4135`, and a primary
  CD4+ CRISPRi protocol with at least 3 donors.
- Signed evidence graph: 11,526 genes, 37,106 regulatory edges, five signed CD4+ findings, root
  `root_a8b0dcdd4024e12f`.
- Corrective comparison: GSE278572 qualifies the MED12 interpretation. High Rest reach weakens
  activation specificity, but does not alone establish housekeeping or essentiality.

Ceiling: computation over released data, not wet-lab or clinical truth.

## Judge Path

1. Open Check. The first screen is the real Claude Science artifact and Prospect's causal verdicts.
2. Paste `IL7R`, `CCR7`, `PD-1`, `ENSG00000121410`, and `NOTGENE` into the check-your-claim box.
3. Inspect the shareable result link: receipt, typed verdicts, `accepted=false`, `human_signature_required`.
4. Read the 48 and 64 percent overclaiming benchmark.
5. Open Lead for the PGGT1B mechanism and CRISPRi refutation experiment.
6. Open Receipts for the audit trail and MCP bridge.

## Public Artifacts

- `/data/check.json`
- `/data/frontier.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/gse278572_comparator.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/finding_index.json`
- `/data/overclaim_counter.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`

## Commands

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
cd web && npm run typecheck && npm run build
./prospect demo-mode --reset
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json
python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json
python receipt/replay_proposal.py <proposal.json-or-url>
python examples/receipt_bridge_client.py --json
python examples/claude_science_connector_client.py --json
```

## Trust Boundary

Claude proposes, searches, and produces reproducible activity. Prospect's acceptance layer is frozen
code over frozen released data plus a human signing key. A model can submit a receipt; it cannot move
accepted records.
