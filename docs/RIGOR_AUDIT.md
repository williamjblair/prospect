# Prospect anti-overclaim rigor audit

Passed: `yes`

Ceiling: computation over released data, not wet-lab or clinical truth.

## Public surfaces scanned

- `README.md`
- `docs/SUBMISSION.md`
- `docs/DEMO.md`
- `docs/DEMO_RECORDING_RUNBOOK.md`
- `docs/JUDGE_HANDOUT.md`
- `docs/JUDGE_TECHNICAL_NOTE.md`
- `docs/DEPLOY_READINESS.md`
- `docs/PUBLIC_ROBUSTNESS.md`
- `docs/OVERNIGHT_PREREGISTRATION.md`
- `docs/OVERNIGHT_COMPUTE_REPORT.md`
- `docs/RECEIPT_BRIDGE.md`
- `docs/RUN_YOUR_OWN_CLAIM.md`
- `docs/DEFENDED_DISCOVERY_ENDGAME_RESULT.md`
- `docs/PGGT1B_ENDGAME_DECISION.md`
- `docs/PGGT1B_DEFENDED_EVIDENCE.md`
- `docs/FINDINGS.md`
- `web/app/page.tsx`

## Downgrades made

- `web/app/page.tsx`: `generic wrongness language` became `claims were contradicted by the frozen table`
- `web/app/page.tsx and docs`: `fixed-bar completion language for PGGT1B` became `PGGT1B is retained as a proposal-only lead worth testing`
- `docs/FINDINGS.md`: `validation language for a computational comparison` became `independently corroborated computation`

## Traceable headline claims

- 48-64% overclaim pressure: artifact `/data/overclaim_counter.json`, command `./prospect overclaim-counter`
- real Claude Science export typed as drivers, passengers, contradicted driver claims, and not_assayed: artifact `/data/claude_science_acceptance_demo.json`, command `python examples/claude_science_connector_client.py --json`
- PGGT1B proposal-only lead worth testing: artifact `/data/pggt1b_defended_evidence.json`, command `./prospect pggt1b-defended-evidence`
- 11,526 to 18 honest funnel: artifact `/data/discovery_campaign.json`, command `./prospect discovery-campaign`
- 118 public robustness fuzz cases with clean failure or honest typing: artifact `/data/public_robustness_fuzz.json`, command `./prospect robustness-fuzz`
- overnight compute typed 11,526 genes and audited the literature corpus: artifact `/data/overnight_literature_audit.json`, command `./prospect overnight-compute`

## Blocked phrase hits

- none

## Framing guards

- claude_science: driver-versus-passenger, not signature-is-wrong
- pggt1b: proposal-only lead worth testing, not accepted biology
- acceptance: accepted=false until human_signature_required
- ceiling: Computation over released data, not wet-lab or clinical truth.
