# Final Submission Checklist

Use this when uploading Prospect to Built with Claude: Life Sciences.

## Submitter Fields

Live URL: https://prospect-sepia-six.vercel.app

Repo URL: https://github.com/williamjblair/prospect

Submission text: `docs/SUBMISSION.md`

Submission form packet: `docs/SUBMISSION_FORM_PACKET.md`

Demo script: `docs/DEMO.md`

Recording runbook: `docs/DEMO_RECORDING_RUNBOOK.md`

Replay gate:

```bash
./prospect final-check
```

Signed root to name if asked: `root_a8b0dcdd4024e12f`

## Final Smoke

Final smoke:

Run this before submitting:

```bash
./prospect final-check
```

Then open:

- https://prospect-sepia-six.vercel.app
- https://prospect-sepia-six.vercel.app/data/judge_packet.json
- https://prospect-sepia-six.vercel.app/data/campaign_gate_probe.json
- https://prospect-sepia-six.vercel.app/data/transfer_replay_packet.json
- https://prospect-sepia-six.vercel.app/data/lab_packet.json
- https://prospect-sepia-six.vercel.app/data/receipt_bridge/receipt_manifest.json

Confirm:

- `/data/judge_packet.json` reports root `root_a8b0dcdd4024e12f`.
- `/data/judge_packet.json` lists `./prospect final-check`.
- `/data/campaign_gate_probe.json` has four rows and stays proposal only.
- `/data/transfer_replay_packet.json` reports 377 compared T-cell regulators and no accepted-state mutation.
- The receipt bridge demo returns `accepted=false`.

## Record The Demo Video

Record the demo video from `docs/DEMO.md` and `docs/DEMO_RECORDING_RUNBOOK.md`.

Keep the first 20 seconds on the refusal and overclaiming number. Do not open on the graph.

Close on:

- receipt bridge: external work can submit a receipt, but accepted state still requires the human signing path
- PGGT1B deep dive: `evidence_attached`, missing wet-lab evidence named
- lab packet and Gladstone assay handoff: five assay-ready rows
- campaign gate probe: Claude pressure-tests gates with `gate_sufficient`, `add_control`, or `lower_priority`
- transfer replay packet: second and third frozen Perturb-seq tables exercise the same checker interface

## Submit The Project

Submit the project with:

- live URL: https://prospect-sepia-six.vercel.app
- repo URL: https://github.com/williamjblair/prospect
- project text from `docs/SUBMISSION_FORM_PACKET.md` or `docs/SUBMISSION.md`
- demo video recorded from `docs/DEMO.md`

Do not paste secrets. Do not mention internal deployment team names. Do not claim wet-lab or clinical
truth. No model in the trust path: Claude proposes and pressure-tests, frozen code replays, and a
human key accepts state.
