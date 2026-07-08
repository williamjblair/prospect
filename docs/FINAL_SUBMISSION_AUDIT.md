# Prospect final submission audit

Readiness: `submission_ready_for_human_upload`.

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

Public artifacts: 19

## Trust boundary

- Model role: `propose_search_pressure_test`
- Model in trust path: `no`
- Accepted-state gate: `frozen_replay_plus_human_ed25519_signature`
- Model accepted-state mutations: 0

## Required gates before upload

- `./prospect final-check`
- `./prospect submit-smoke`
- `./prospect submit-pack`
- `./prospect demo-pack`
- `./prospect judge-handout`
- `./prospect verify`
- `python benchmark/mutation_pack.py`
- `python tests/test_skill_parity.py`
- `python examples/receipt_bridge_client.py --json`

## Source docs

- `docs/JUDGE_QUICKSTART.md`
- `docs/SUBMISSION_FORM_PACKET.md`
- `docs/SUBMISSION.md`
- `docs/DEMO_RECORDING_RUNBOOK.md`
- `docs/DEMO_TELEPROMPTER.md`
- `docs/JUDGE_HANDOUT.md`
- `docs/FINAL_SUBMISSION_CHECKLIST.md`
- `docs/FINAL_SUBMISSION_AUDIT.md`
- `docs/JUDGE_PACKET.md`

## Shipped workstreams

| workstream | state | evidence |
|---|---|---|
| submission_floor | shipped | `./prospect final-check`, `./prospect submit-smoke`, `root_a8b0dcdd4024e12f` |
| second_substrate_replay | shipped | `./prospect substrate-replay`, `/data/substrate_replay_packet.json` |
| claude_campaign_pressure | shipped | `./prospect campaign-pressure`, `/data/campaign_pressure_summary.json` |
| gladstone_assay_operations | shipped | `./prospect assay-ops`, `/data/assay_operations_bundle.json` |
| demo_and_submission_packets | shipped | `./prospect demo-pack`, `./prospect submit-pack`, `docs/FINAL_SUBMISSION_CHECKLIST.md` |

## Public artifacts

- `/data/frontier.json`
- `/data/judge_packet.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign.json`
- `/data/agent_campaign_review.json`
- `/data/campaign_agent_probe.json`
- `/data/campaign_triage.json`
- `/data/campaign_gate_probe.json`
- `/data/campaign_pressure_summary.json`
- `/data/transfer_replay_packet.json`
- `/data/substrate_replay_packet.json`
- `/data/lab_packet.json`
- `/data/assay_operations_bundle.json`
- `/data/final_submission_audit.json`

## Human-only actions

- `record_demo_video`
- `submit_project_form`
- `wet_lab_execution`

Prospect proves computation over released data, not wet-lab or clinical truth.

Rebuild:

```bash
./prospect submission-audit
```
