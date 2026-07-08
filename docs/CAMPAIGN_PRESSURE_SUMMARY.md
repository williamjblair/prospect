# Campaign pressure summary

Status: `evidence_attached`. Trust boundary: proposal only.

Claude pressure became review work: aligned rows stayed aligned, more-aggressive rows became assay gates, gate probes added controls or lowered priority, and no accepted state changed.

## Replay

```bash
./prospect campaign-pressure
```

## Counts

- Campaign candidates: 20
- Deterministic review rows: 20
- Claude probe rows: 8
- Aligned rows: 3
- More-aggressive rows converted to assay gates: 4
- More-cautious rows: 1
- Gate probe rows: 4

## Gate recommendations

- `add_control`: 1
- `gate_sufficient`: 2
- `lower_priority`: 1

## Pressure accounting

| rank | gene | Claude pressure | Prospect result | gate recommendation |
|---:|---|---|---|---|
| 1 | PGGT1B | advance_to_assay_design | aligned_with_deterministic_review | none |
| 2 | RCC1L | advance_to_assay_design | converted_to_assay_gate | gate_sufficient |
| 3 | MCAT | advance_if_capacity_allows | converted_to_assay_gate | add_control |
| 4 | RWDD2B | advance_if_capacity_allows | converted_to_assay_gate | lower_priority |
| 5 | CCDC22 | advance_if_capacity_allows | converted_to_assay_gate | gate_sufficient |
| 6 | GAS2L1 | advance_if_capacity_allows | aligned_with_deterministic_review | none |
| 7 | SNAP29 | hold_as_ranked_backup | model_more_cautious | none |
| 8 | CYB5RL | hold_as_ranked_backup | aligned_with_deterministic_review | none |

No model output in this packet changes accepted state.
