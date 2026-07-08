# Judge packet

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## No model in the trust path

A model proposes, searches, and drafts. Frozen code over a frozen released table gates the result. A human Ed25519 key accepts. Receipt submission is proposal only.

## Replay gate

```bash
./prospect final-check
./prospect submit-smoke
./prospect submit-pack
./prospect demo-pack
./prospect release-manifest
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
cd web && npm run build
```

## Artifact counts

- Genes mapped: 11526
- Regulatory edges: 37106
- Findings: 5
- Receipts: 6
- Campaign candidates: 20
- Campaign review rows: 20
- Campaign probe rows: 20
- Campaign probe audit issues: 0
- Campaign triage rows: 11
- Campaign gate probe rows: 11
- Campaign pressure rows: 20
- Transfer replay rows: 377
- Substrate replay rows: 377
- Cross-substrate discovery rows: 11526
- Cross-substrate campaign rows: 20
- Donor-condition replay rows: 20
- Donor-supported campaign rows: 13
- Validation candidates: 5
- Lab packet candidates: 5
- Assay operations candidates: 5
- Pilot design candidates: 5
- Pilot design culture arms: 90
- Final submission public artifacts: 25
- PGGT1B evidence ladder steps: 5
- PGGT1B matrix-slice transcripts: 671

## PGGT1B evidence capsule

The top agent hypothesis has an evidence capsule with exact ratios, a released-matrix moved-transcript slice, assay gates, and missing evidence. Status remains `evidence_attached`.

## Gladstone assay operations bundle

The operations bundle turns the top five proposal-only assay rows into explicit expected positive, weakening, and rejection evidence before any accepted state can move.

## Gladstone pilot design

The pilot design turns those rows into donor, condition, control, and culture-arm accounting for a proposal-only bench plan.

## Final submission audit

The final audit names shipped workstreams, required gates, public artifacts, trust boundary, and the human-only upload actions.

## Campaign gate probe

The gate probe pressure-tests the disagreement triage rows with closed recommendations: `gate_sufficient`, `add_control`, or `lower_priority`. It stays proposal only.

## Campaign pressure summary

The pressure summary accounts for what Claude changed, what Prospect refused to change, and which assay gates remain before any accepted state can move.

## Transfer replay packet

The transfer packet replays the signed cross-cell-type finding through the Marson and Replogle checkers, without changing accepted state.

## Substrate replay packet

The substrate packet makes the protocol-generalization claim explicit: one checker contract, three frozen substrates, typed status, and no accepted-state mutation.

## Cross-substrate discovery packet

The discovery packet classifies every frozen Marson row against K562 and RPE1 count tables, then intersects the result with the proposal-only campaign leaderboard.

## Donor-condition replay packet

The donor packet replays released donor-correlation and guide-support fields for all 20 campaign strongest-condition rows.

## Receipt bridge demo

Run the external MCP client:

```bash
python examples/receipt_bridge_client.py
```

It starts `./prospect mcp`, discovers the receipt tools, validates a receipt, and submits it as a proposal. The expected result includes `accepted=false` and `next=human_signature_required`.

## Public data

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
- `/data/campaign_probe_audit.json`
- `/data/campaign_triage.json`
- `/data/campaign_gate_probe.json`
- `/data/campaign_pressure_summary.json`
- `/data/transfer_replay_packet.json`
- `/data/substrate_replay_packet.json`
- `/data/cross_substrate_discovery.json`
- `/data/donor_condition_replay.json`
- `/data/lab_packet.json`
- `/data/assay_operations_bundle.json`
- `/data/gladstone_pilot_design.json`
- `/data/final_submission_audit.json`
- `/data/release_manifest.json`
- `/data/rendered_qa_packet.json`

## Demo path

- Overview: AI claim refusal and 48 percent overclaim rate
- Findings: five-row index, then evidence tables
- Frontier: signed root, contradictions, receipts, MCP bridge
- Agent: PGGT1B packet, campaign leaderboard, lab assay packet
- Agent: PGGT1B evidence capsule shows exact ratios, matrix slice, and missing acceptance evidence
- Agent: Gladstone assay operations bundle names promotion, weakening, and rejection evidence
- Agent: Claude probe compared with deterministic review lanes
- Agent: disagreement triage turns model pressure into assay gates
- Agent: gate probe checks whether gates are sufficient, need controls, or should be lower priority

Rebuild:

```bash
python frontier/judge_packet.py
```
