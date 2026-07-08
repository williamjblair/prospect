# Campaign pressure summary

Status: `evidence_attached`. Trust boundary: proposal only.

Claude pressure became review work: aligned rows stayed aligned, more-aggressive rows became assay gates, gate probes added controls or lowered priority, gate coverage stayed explicit, and no accepted state changed.

## Replay

```bash
./prospect campaign-pressure
```

## Counts

- Campaign candidates: 20
- Deterministic review rows: 20
- Claude probe rows: 20
- Aligned rows: 6
- More-aggressive rows converted to assay gates: 11
- More-cautious rows: 3
- Gate probe rows: 11

## Gate coverage

- Requested gates: 11
- Returned gate decisions: 11
- Coverage status: `complete`
- Missing decisions: 0

## Gate recommendations

- `add_control`: 4
- `gate_sufficient`: 6
- `lower_priority`: 1

## Pressure accounting

| rank | gene | Claude pressure | Prospect result | gate recommendation |
|---:|---|---|---|---|
| 1 | PGGT1B | advance_to_assay_design | aligned_with_deterministic_review | none |
| 2 | RCC1L | advance_to_assay_design | converted_to_assay_gate | gate_sufficient |
| 3 | MCAT | hold_as_ranked_backup | aligned_with_deterministic_review | none |
| 4 | RWDD2B | advance_if_capacity_allows | converted_to_assay_gate | lower_priority |
| 5 | CCDC22 | advance_to_assay_design | converted_to_assay_gate | gate_sufficient |
| 6 | GAS2L1 | advance_if_capacity_allows | aligned_with_deterministic_review | none |
| 7 | SNAP29 | hold_as_ranked_backup | model_more_cautious | none |
| 8 | CYB5RL | advance_if_capacity_allows | converted_to_assay_gate | gate_sufficient |
| 9 | LETM2 | advance_if_capacity_allows | aligned_with_deterministic_review | none |
| 10 | DAPK2 | hold_as_ranked_backup | model_more_cautious | none |
| 11 | SCO2 | advance_if_capacity_allows | converted_to_assay_gate | add_control |
| 12 | CCDC136 | advance_to_assay_design | converted_to_assay_gate | add_control |
| 13 | MITD1 | advance_to_assay_design | converted_to_assay_gate | gate_sufficient |
| 14 | GZMB | advance_if_capacity_allows | converted_to_assay_gate | add_control |
| 15 | FANCL | advance_if_capacity_allows | converted_to_assay_gate | gate_sufficient |
| 16 | TNNC1 | hold_as_ranked_backup | aligned_with_deterministic_review | none |
| 17 | BCKDHA | advance_to_assay_design | converted_to_assay_gate | gate_sufficient |
| 18 | ZC3H12A | advance_if_capacity_allows | converted_to_assay_gate | add_control |
| 19 | IRF4 | use_as_regulon_anchor | aligned_with_deterministic_review | none |
| 20 | RXRB | hold_as_ranked_backup | model_more_cautious | none |

No model output in this packet changes accepted state.
