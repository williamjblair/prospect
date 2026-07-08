# Submission form packet

Copy from this file when filling out the Built with Claude: Life Sciences submission form.

## Project title

Prospect

## Short description

A computationally reproduced regulatory frontier of human CD4+ T-cell biology: Claude proposes and
pressure-tests hypotheses, frozen code replays the Marson screen, and a human signature accepts state.

## Long description

Prospect is a signed, content-addressed graph of gene regulation re-derived from the released Marson
lab CRISPRi Perturb-seq screen in primary human CD4+ T cells. It exists to solve a concrete problem:
AI can generate biological claims faster than scientists can check them. On this screen, four
frontier models overstate confident major-regulator claims 48% of the time, and 64% of the time on
the checkpoint and cytokine genes the field targets most.

The system separates activity from accepted state. Claude proposes, searches, and pressure-tests.
Frozen verifiers over frozen released tables decide what the data supports, contradicts, or cannot
grade. A human Ed25519 key accepts the signed frontier root. No model is in the trust path.

The app shows five signed findings: the TCR activation module recovered from perturbation alone,
famous checkpoint/cytokine overclaims contradicted by the measured data, the essentiality artifact a
naive ranking mistakes for immunology, cross-cell-type transfer through Replogle K562/RPE1 checkers,
and CollecTRI regulon recovery. The agent layer converts Claude pressure into proposal-only assay
gates, headed by PGGT1B and a five-row wet-lab handoff for stimulated CD4+ follow-up.

Statuses stay typed: `computationally_reproduced`, `evidence_attached`, and `contradicted`. Prospect
does not claim wet-lab or clinical truth. It proves replayable computation, names missing evidence,
and keeps weak evidence out of accepted state.

## Live URL

https://prospect-sepia-six.vercel.app

## Repo URL

https://github.com/williamjblair/prospect

## Demo video

Record from `docs/DEMO_RECORDING_RUNBOOK.md`.

Recommended opening: start on the A1BG refusal, not the graph.

Recommended close: receipt bridge, PGGT1B `evidence_attached` packet, lab handoff, campaign gates,
and signed replayable state.

Teleprompter: `docs/DEMO_TELEPROMPTER.md` or `./prospect demo-pack`.

Judge quickstart: `docs/JUDGE_QUICKSTART.md`.

## Built with Claude

Claude is used in three ways:

- Measured: the benchmark grades Claude and other frontier models against the frozen screen.
- In the loop: `./prospect propose` and `./prospect agent` use Claude to propose and investigate.
- As pressure test: campaign probes ask Claude to challenge deterministic assay gates.

The frozen verifier and human key remain the gate. No model in the trust path.

## What outlasts the week

Prospect is working software for a skeptical immunologist or computational biologist reading the
Marson lab screen. The durable pieces are the live app, replayable CLI, public data endpoints,
receipt bridge, wet-lab handoff, and signed root accepted by a human signature. The docs and public
JSON endpoints let a judge rerun the trust floor after the event window.

## Verification commands

```bash
./prospect final-check
./prospect submit-smoke
./prospect submit-pack
./prospect demo-pack
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python examples/receipt_bridge_client.py --json
```

Expected receipt bridge result includes `accepted=false` and `next=human_signature_required`.

Signed root: `root_a8b0dcdd4024e12f`

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
- `/data/transfer_replay_packet.json`
- `/data/lab_packet.json`

## Safety copy

Use this if the form asks about limitations:

Prospect proves computation over released data, not wet-lab or clinical truth. PGGT1B and all assay
rows remain `evidence_attached` hypotheses to test. Accepted state requires replay through frozen
code and a human signature.

Do not claim wet-lab or clinical truth.
