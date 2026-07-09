# Prospect one-page judge handout

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## What Prospect proves

Claude makes scientific activity cheap; Prospect decides what becomes replayable, human-accepted state.

Prospect proves computation over released data, not wet-lab or clinical truth.

## Numbers to inspect

- 5 signed findings
- 6 portable receipts
- 5 rows in the scannable finding index
- 20 proposal-only campaign rows
- 20 campaign rows overlaid with external disease context
- 10 rows with selected immune or hematologic context
- 5 proposal-only wet-lab assay rows
- 23 public data artifacts
- 52 real Claude Science signature genes typed by Prospect: 12 drivers, 22 passengers, 3 contradicted driver claims, 15 not assayed
- Frozen ORCS primary T-cell context reduces uncovered Sade-Feldman genes to 5
- PGGT1B novelty downgraded against prior art: yes, wet-lab protocol minimum donors 3
- Defended-discovery fixed bar: 18 locked candidates, 1 proposal-only lead worth testing (PGGT1B), 4 retained independent primary T-cell support, 18 retain RPE1 as not_assayed context
- Overnight compute: 11526 genes typed, 51 of 229 literature claims contradicted, 1 of 100 leaderboard rows cleared the compute bar

## Trust boundary

- Model role: `propose, search, pressure-test`
- Model in trust path: `no`
- Accepted state: `human_signed_replayable_root`
- Model accepted-state mutations: 0

## Five-minute judge path

1. Overview: acceptance layer first, the real Claude Science export enters Prospect and receives typed causal verdicts.
2. Overview: substrate coverage, frozen ORCS primary T-cell context shrinks uncovered genes while staying proposal-only.
3. Overview: PGGT1B is the caveated hypothesis worth testing, with prior-art novelty downgraded.
4. Overview: paste any signature, DE table, ranked marker list, or gene list into the submitter and share the state page.
5. Overview: the overclaiming counter, 48% overall and 64% on canonical effectors.
6. Findings: signed CD4+ T-cell findings that recover known biology and catch overclaims.
7. Agent: the campaign leaderboard, every row a proposal, none accepted state.
8. Agent: the PGGT1B evidence packet, ChEMBL hook, disease context, and wet-lab protocol.
9. Agent: the wet-lab assay packet, proposal-only, ready for a lab.
10. Frontier: the receipt boundary and the MCP bridge, which returns a proposal, never accepted state.

## Public artifacts to open

- `/data/frontier.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/substrate_coverage_report.json`
- `/data/defended_discovery_endgame_preregistration.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/pggt1b_endgame_decision.json`
- `/data/defended_discovery_endgame_result.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign.json`
- `/data/disease_genetics_overlay.json`
- `/data/lab_packet.json`
- `/data/lab_writeback_receipt.json`
- `/data/public_robustness_fuzz.json`
- `/data/overnight_preregistration.json`
- `/data/overnight_genome_wide_atlas.json`
- `/data/overnight_literature_claims.json`
- `/data/overnight_literature_audit.json`
- `/data/overnight_defended_leaderboard.json`

## Replay commands

- `./prospect verify`
- `./prospect submit-pack`
- `./prospect demo-mode --reset`
- `./prospect claude-science`
- `./prospect defended-discovery-endgame-preregister`
- `./prospect pggt1b-endgame-decision`
- `./prospect defended-discovery-endgame-result`
- `./prospect overnight-compute`
- `./prospect substrate-coverage`
- `./prospect pggt1b-defended-evidence`
- `./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service`
- `python benchmark/mutation_pack.py`
- `python examples/receipt_bridge_client.py --json`
- `python examples/claude_science_connector_client.py --json`
- `python examples/prospect_connector_client.py --case openresearch --json`

## What remains human-only

- sign the frontier root
- accept a submitted receipt
- sign an agent or campaign hypothesis
- wet-lab execution

Rebuild:

```bash
./prospect judge-handout
```
