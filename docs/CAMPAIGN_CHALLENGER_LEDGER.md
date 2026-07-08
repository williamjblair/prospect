# Campaign challenger ledger

Status: `evidence_attached`. Trust boundary: frozen join over committed packets.

No accepted state changes. The ledger challenges assay priority only.

## Replay

```bash
./prospect campaign-challenger
```

## Panel delta

- Current primary panel: PGGT1B, RCC1L, MCAT, RWDD2B, CCDC22
- Recommended primary panel: PGGT1B, RCC1L, MCAT, CCDC22, CYB5RL
- Remove: RWDD2B
- Add: CYB5RL

## Counts

- Campaign rows: 20
- Primary-panel challenges: 1
- Replacement candidates: 2
- Retain primary panel: 4
- Promote if capacity: 2
- Demote or control: 8

## Challenger rows

| rank | gene | current panel | donor | substrate | gate | action | change |
|---:|---|---|---|---|---|---|---|
| 1 | PGGT1B | yes | donor_supported | t_cell_specific_activation | none | retain_primary_panel | keep_in_primary_panel |
| 2 | RCC1L | yes | donor_supported | t_cell_specific_activation | gate_sufficient | retain_primary_panel | keep_in_primary_panel |
| 3 | MCAT | yes | donor_supported | t_cell_specific_activation | none | retain_primary_panel | keep_in_primary_panel |
| 4 | RWDD2B | yes | donor_fragile | t_cell_specific_activation | lower_priority | challenge_primary_panel | remove_from_primary_panel |
| 5 | CCDC22 | yes | donor_supported | t_cell_specific_activation | gate_sufficient | retain_primary_panel | keep_in_primary_panel |
| 6 | GAS2L1 | no | donor_supported | t_cell_specific_activation | none | hold_for_review | none |
| 7 | SNAP29 | no | guide_limited | t_cell_specific_activation | none | demote_or_control | none |
| 8 | CYB5RL | no | donor_supported | t_cell_specific_activation | gate_sufficient | promote_if_capacity | add_to_primary_panel |
| 9 | LETM2 | no | donor_intermediate | ambiguous_or_not_tested | none | demote_or_control | none |
| 10 | DAPK2 | no | donor_supported | ambiguous_or_not_tested | none | demote_or_control | none |
| 11 | SCO2 | no | donor_supported | t_cell_specific_activation | add_control | contextual_priority | none |
| 12 | CCDC136 | no | donor_supported | t_cell_specific_activation | add_control | hold_for_review | none |
| 13 | MITD1 | no | donor_supported | t_cell_specific_activation | gate_sufficient | promote_if_capacity | add_to_primary_panel |
| 14 | GZMB | no | donor_fragile | ambiguous_or_not_tested | add_control | demote_or_control | none |
| 15 | FANCL | no | donor_intermediate | t_cell_specific_activation | gate_sufficient | hold_for_review | none |
| 16 | TNNC1 | no | donor_fragile | ambiguous_or_not_tested | none | demote_or_control | none |
| 17 | BCKDHA | no | donor_supported | ambiguous_or_not_tested | gate_sufficient | demote_or_control | none |
| 18 | ZC3H12A | no | donor_supported | t_cell_specific_activation | add_control | hold_for_review | none |
| 19 | IRF4 | no | donor_fragile | ambiguous_or_not_tested | none | demote_or_control | none |
| 20 | RXRB | no | donor_supported | ambiguous_or_not_tested | none | demote_or_control | none |

This ledger reconciles shipped proposal and replay packets for assay prioritization. It does not move accepted state or prove a wet-lab result.
