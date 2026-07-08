# Demo recording runbook

Use this while recording the Built with Claude: Life Sciences submission video.

Teleprompter script: [DEMO_TELEPROMPTER.md](DEMO_TELEPROMPTER.md)

Primary target: https://prospect-sepia-six.vercel.app

Local fallback, if production is unavailable:

```bash
cd web && npm run dev
```

Open http://localhost:8124. Do not use port 3000.

## Preflight

Run this before recording:

```bash
./prospect final-check
./prospect submit-smoke
./prospect submit-pack
./prospect demo-pack
./prospect judge-handout
./prospect release-manifest
./prospect rendered-qa
python examples/receipt_bridge_client.py --json
```

Optional operator confidence check, after local web starts on `8124`:

```bash
cd web && npm run start
./prospect browser-qa --target both
```

Confirm:

- `./prospect final-check` ends with `FINAL CHECK PASS`.
- `./prospect submit-smoke` ends with `SUBMIT SMOKE PASS`.
- `./prospect submit-pack` prints the live URL, repo URL, signed root, and source docs.
- `./prospect demo-pack` prints the six timed recording beats and "Do not say" guardrails.
- `./prospect judge-handout` writes `docs/JUDGE_HANDOUT.md`.
- `./prospect release-manifest` writes `/data/release_manifest.json`.
- `./prospect rendered-qa` writes `/data/rendered_qa_packet.json`.
- `./prospect browser-qa --target both` writes local browser evidence under ignored
  `output/playwright/` if local web is running on `8124`.
- The receipt bridge client returns `accepted=false`.
- The receipt bridge client returns `next=human_signature_required`.
- `/data/judge_packet.json` reports root `root_a8b0dcdd4024e12f`.
- `/data/campaign_pressure_summary.json` accounts for eight Claude probe rows and zero accepted-state mutations.
- `/data/transfer_replay_packet.json` reports 377 compared T-cell regulators and no accepted-state mutation.
- `/data/substrate_replay_packet.json` reports 377 replayed rows across three frozen substrates.

## Recording Beats

### 0:00, Refusal

Open on the Overview tab, not the graph.

Show the A1BG claim card:

> CRISPRi of A1BG drives a broad activation program in stimulated CD4 T cells, a promising target.

Say: the checker marks this unsupported because A1BG was not knocked down. A model can assert this
in a second. Checking it is the scarce part.

### 0:20, The Number

Show the 48% overclaiming number.

Say: on a frozen Marson-screen sample, four frontier models made confident major-regulator claims,
and 48% were contradicted by the measured data. On famous checkpoint and cytokine genes, the
overclaim rate is 64%.

### 0:40, Findings

Click Findings.

Show the five-row findings index. Say the arc in one sentence: recover known biology, catch famous
overclaims, resist the essentiality artifact, transfer the checker, recover regulons.

Show Finding 01 and Finding 02:

- CD3E is quiet at Rest and broad after stimulation.
- PD-1, TIM-3, CTLA-4, and IL-2 are outputs here, not broad transcriptional drivers.

### 1:05, The Moat

Stay in Findings and show Finding 04.

Say: the same major-regulator claim runs through Marson and Replogle checkers. MED19 moves 3,716
genes in K562. BCL10 moves 2. The transfer replay packet keeps this at
`computationally_reproduced` and changes no accepted state.

### 1:30, The Loop

Open Agent.

Show the campaign pressure summary.

Say: Claude proposed fifteen transcription factors, then pressure-tested the campaign rows. Claude
pressure became review work: twenty probed rows, eleven more-aggressive calls converted to assay
gates, and all eleven gates returned proposal-only review evidence. Zero accepted-state mutations.
Claude proposes; frozen code decides; a human key accepts.

### 1:50, Close

Click Frontier.

Show the receipt bridge and the "Try the boundary" strip:

```bash
python examples/receipt_bridge_client.py --json
```

Say: external work can submit a receipt, but the expected result is `accepted=false`,
`next=human_signature_required`. No model moves accepted state.

Click Agent.

Show PGGT1B, the lab packet, the assay operations bundle, the pilot design, and campaign gates:

- PGGT1B remains `evidence_attached`.
- The packet names missing wet-lab evidence before acceptance.
- The lab packet gives five assay-ready rows.
- The assay operations bundle names expected positive, weakening, and rejection evidence.
- The pilot design names 90 proposal-only culture arms across three donor replicates.
- The campaign gate probe turns Claude pressure into `gate_sufficient`, `add_control`, or
  `lower_priority`.

Close with: generation is cheap. Accepted state is scarce, replayable, and signed.

## Do Not Say

- Do not claim wet-lab or clinical truth.
- Do not call PGGT1B an accepted regulator.
- Do not say Prospect proves therapeutic action.
- Do not imply Claude can move accepted state.
- Do not call `evidence_attached` rows reproduced findings.

## Submission Fields

- Live URL: https://prospect-sepia-six.vercel.app
- Repo URL: https://github.com/williamjblair/prospect
- Submission form packet: `docs/SUBMISSION_FORM_PACKET.md`
- Submission text: `docs/SUBMISSION.md`
- Demo script: `docs/DEMO.md`
- Final checklist: `docs/FINAL_SUBMISSION_CHECKLIST.md`
