# Prospect one-page judge handout

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## What Prospect proves

Prospect tells a biologist which genes in an AI-generated prediction list behave as causal drivers, which are passengers, and which driver claims the perturbation data contradicts. The first-screen output is a driver/passenger/contradicted split.

Reproducible is not verified.

Prospect proves computation over released data, not wet-lab or clinical truth.

## Numbers To Inspect

- Real Claude Science signature: 52 genes, 12 drivers, 22 passengers, 3 contradicted driver claims, 15 not assayed
- ORCS primary T-cell context reduces uncovered Sade-Feldman genes to 5
- PGGT1B carries 10 orthogonal public evidence sources
- PGGT1B novelty downgraded against prior art: yes, wet-lab protocol minimum donors 3
- 5 signed CD4+ findings and 6 receipts
- 10 public data artifacts

## Five-minute judge path

1. Overview: real Claude Science signature enters Prospect and receives typed causal verdicts.
2. Overview: paste a gene list, DE table, or signature and copy the shareable state link.
3. Overview: inspect the 48 and 64 percent overclaiming benchmark.
4. Agent: PGGT1B is the caveated mechanism-first hypothesis worth testing.
5. Findings: signed CD4+ T-cell records show the frozen frontier.
6. Frontier: receipts and MCP bridge show accepted=false until a human key signs.

## Trust Boundary

- Model role: propose, search, draft
- Model in trust path: no
- Accepted state: human_signed_replayable_root
- Model accepted state mutations: 0

## Public Artifacts

- `/data/frontier.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/substrate_coverage_report.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/pggt1b_deep_dive.json`
- `/data/overclaim_counter.json`

## Commands

- `./prospect verify`
- `python benchmark/mutation_pack.py`
- `python tests/test_skill_parity.py`
- `python tests/test_marson.py`
- `./prospect demo-mode --reset`
- `./prospect claude-science`
- `./prospect substrate-coverage`
- `./prospect pggt1b-defended-evidence`
- `./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service`
- `python examples/receipt_bridge_client.py --json`
- `python examples/claude_science_connector_client.py --json`

## What remains human-only

- sign the frontier root
- accept a submitted receipt
- accept a PGGT1B state change
- wet-lab execution
