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
- `docs/RECEIPT_BRIDGE.md`
- `docs/RUN_YOUR_OWN_CLAIM.md`
- `docs/PGGT1B_DEFENDED_EVIDENCE.md`
- `docs/FINDINGS.md`
- `docs/FINDING_INDEX.md`
- `frontier/finding_index.py`
- `examples/data/finding_index.json`
- `web/public/data/finding_index.json`
- `web/app/page.tsx`

## Downgrades made

- `web/app/page.tsx`: `generic wrongness language` became `claims were contradicted by the frozen table`
- `web/app/page.tsx and docs`: `fixed-bar completion language for PGGT1B` became `PGGT1B is retained as a proposal-only lead worth testing`
- `web/app/page.tsx and docs/FINDINGS.md`: `Rest reach proves housekeeping and cross-cell transfer validates the split` became `Rest reach limits activation specificity; cross-cell reach is orthogonal context`
- `web/app/page.tsx and docs/FINDINGS.md`: `assay sign overrules the literature` became `sign disagreements are context-sensitive review candidates`

## Traceable headline claims

- 48-64% overclaim pressure: artifact `/data/overclaim_counter.json`, command `./prospect overclaim-counter`
- real Claude Science export typed as drivers, passengers, and not_assayed: artifact `/data/claude_science_acceptance_demo.json`, command `python examples/claude_science_connector_client.py --json`
- PGGT1B proposal-only lead worth testing: artifact `/data/pggt1b_defended_evidence.json`, command `./prospect pggt1b-defended-evidence`
- five signed CD4+ findings: artifact `/data/finding_index.json`, command `./prospect findings-index`
- receipt bridge returns proposal-only state: artifact `/data/receipt_bridge/receipt_contract.json`, command `python examples/receipt_bridge_client.py --json`
- GSE278572 proposal qualifies the Rest-reach interpretation: artifact `/data/gse278572_comparator.json`, command `python frontier/gse278572_comparator.py --check`

## Blocked phrase hits

- none

## Framing guards

- claude_science: driver-versus-passenger, not signature-is-wrong
- pggt1b: proposal-only lead worth testing, not accepted biology
- acceptance: accepted=false until human_signature_required
- rest_reach: evidence against activation specificity, not a housekeeping or essentiality label
- cross_cell: orthogonal breadth evidence; missing coverage is not refutation
- regulon_sign: sign disagreement is a review candidate, not automatic literature refutation
- ceiling: Computation over released data, not wet-lab or clinical truth.
