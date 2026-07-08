# Judge quickstart

This is the fastest path through Prospect for a hackathon judge.

Live: https://prospect-sepia-six.vercel.app

Repo: https://github.com/williamjblair/prospect

Signed root: `root_a8b0dcdd4024e12f`

## Five-minute path

1. Open the live site.
2. Start on the Overview tab. Read the A1BG refusal first, not the graph.
3. Check the headline number: four frontier models overstate confident major-regulator claims 48%
   of the time on the Marson CD4+ screen, and 64% of the time on checkpoint and cytokine genes.
4. Open Findings. Read the arc: recover known TCR biology, catch effector overclaims, resist
   essentiality artifacts, replay the checker across cell types, recover known regulons.
5. Open Frontier. Check the receipt bridge. External activity can submit a receipt, but the result
   is `accepted=false` and `next=human_signature_required`.
6. Open Agent. Check PGGT1B, the lab packet, and the assay operations bundle. PGGT1B remains
   `evidence_attached`, not an accepted regulator.

## What to verify

```bash
./prospect final-check
./prospect submit-smoke
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python examples/receipt_bridge_client.py --json
```

Expected results:

- `./prospect verify`: 53,485 objects, 0 drift, root `root_a8b0dcdd4024e12f`.
- Mutation pack: zero false admissions.
- Skill parity: 112 claims, 0 mismatches.
- Receipt bridge client: `accepted=false`, `next=human_signature_required`.
- Production smoke: all public artifacts reachable.

## Trust boundary

No model in the trust path. Claude proposes, searches, and pressure-tests. Frozen code over frozen
released tables decides what replays. A human Ed25519 key accepts state.

Typed statuses:

- `computationally_reproduced`: re-derived from frozen released inputs.
- `evidence_attached`: reproduced facts support a hypothesis to test.
- `contradicted`: the data disagrees with the claim.

Prospect proves computation over released data, not wet-lab or clinical truth.

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
- `/data/release_manifest.json`
- `/data/rendered_qa_packet.json`

## Why this is a Build Track project

Prospect is working software for a named user: a skeptical immunologist or computational biologist
reading the Marson lab screen. It ships a live app, a replayable CLI, a public judge packet, an MCP
receipt bridge, and a wet-lab handoff. Claude is useful in the loop, but accepted state remains
replayable and human accepted.

## What outlasts the week

The durable user is a skeptical immunologist or computational biologist reading the Marson lab screen.
The durable artifact is working software, not a notebook or a one-off transcript:

- live app at the production URL above
- replayable CLI with `./prospect final-check`, `./prospect verify`, and `./prospect submit-smoke`
- public data endpoints listed in this quickstart and checked by production smoke
- receipt bridge that lets external activity submit a proposal while preserving `accepted=false`
- wet-lab handoff that names controls, readouts, exclusion rules, and missing evidence before acceptance
- human signature over the signed root that separates accepted state from model activity
