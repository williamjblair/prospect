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
- 25 public data artifacts
- 377 replayed T-cell regulators across three frozen substrates
- 11526 Marson rows classified against non-immune substrates
- 409 T-cell-specific activation candidates
- 20 campaign rows replayed against donor-correlation fields
- 13 donor-supported campaign rows
- 20 Claude probe rows in the pressure loop
- 11 of 11 gate-probe decisions returned, coverage `complete`
- 5 proposal-only assay operations rows
- 90 proposal-only pilot culture arms

## Trust boundary

- Model role: `propose_search_pressure_test`
- Model in trust path: `no`
- Accepted state: `human_signed_replayable_root`
- Model accepted-state mutations: 0

## Five-minute judge path

1. Overview: A1BG refusal and 48 percent overclaiming number.
2. Findings: signed CD4+ T-cell findings that recover known biology and catch overclaims.
3. Findings: substrate replay across Marson CD4+ T cells, Replogle K562, and Replogle RPE1.
4. Findings: cross-substrate discovery classifies shared machinery and T-cell-specific candidates.
5. Agent: donor replay separates donor-supported campaign rows from donor-fragile rows.
6. Frontier: receipt bridge returns proposal-only submission, not accepted state.
7. Agent: Claude pressure becomes assay gates, then PGGT1B, assay operations, and pilot design show the lab handoff.

## Public artifacts to open

- `/data/judge_packet.json`
- `/data/campaign_pressure_summary.json`
- `/data/substrate_replay_packet.json`
- `/data/cross_substrate_discovery.json`
- `/data/donor_condition_replay.json`
- `/data/assay_operations_bundle.json`
- `/data/gladstone_pilot_design.json`
- `/data/final_submission_audit.json`
- `/data/release_manifest.json`
- `/data/rendered_qa_packet.json`

## Replay commands

- `./prospect final-check`
- `./prospect submit-smoke`
- `./prospect submit-pack`
- `./prospect demo-pack`
- `python examples/receipt_bridge_client.py --json`

## What remains human-only

- `record_demo_video`
- `submit_project_form`
- `wet_lab_execution`

Rebuild:

```bash
./prospect judge-handout
```
