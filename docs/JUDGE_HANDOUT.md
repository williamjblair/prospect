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
- 15 public data artifacts
- 52 real Claude Science signature genes typed by Prospect: 12 drivers, 22 passengers, 3 contradicted driver claims, 15 not assayed
- Defended-discovery endgame: 18 locked candidates, 0 cleared the pre-registered bar, 4 retained independent primary T-cell support, 18 blocked by missing RPE1 assay coverage

## Trust boundary

- Model role: `propose, search, pressure-test`
- Model in trust path: `no`
- Accepted state: `human_signed_replayable_root`
- Model accepted-state mutations: 0

## Five-minute judge path

1. Overview: the real Claude Science export enters through Prospect and returns typed causal verdicts.
2. Overview: paste any signature, DE table, ranked marker list, or gene list into the Prospect submitter and share the state page.
3. Overview: the defended-discovery endgame, 18 locked candidates tested and 0 cleared the full pre-registered bar.
4. Overview: the A1BG refusal and the overclaiming number.
5. Findings: signed CD4+ T-cell findings that recover known biology and catch overclaims.
6. Findings: the scannable finding index.
7. Agent: the campaign leaderboard, every row a proposal, none accepted state.
8. Agent: the PGGT1B evidence packet and the disease-genetics overlay.
9. Agent: the wet-lab assay packet, proposal-only, ready for a lab.
10. Frontier: the receipt boundary and the MCP bridge, which returns a proposal, never accepted state.

## Public artifacts to open

- `/data/frontier.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/defended_discovery_endgame_preregistration.json`
- `/data/pggt1b_endgame_decision.json`
- `/data/defended_discovery_endgame_exhaustion.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign.json`
- `/data/disease_genetics_overlay.json`
- `/data/lab_packet.json`
- `/data/lab_writeback_receipt.json`

## Replay commands

- `./prospect verify`
- `./prospect submit-pack`
- `./prospect claude-science`
- `./prospect defended-discovery-endgame-preregister`
- `./prospect pggt1b-endgame-decision`
- `./prospect defended-discovery-endgame-exhaustion`
- `./prospect serve-acceptance --port 8130`
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
