# Defended discovery endgame exhaustion

Ledger id: `endgame_exhaustion_f2c2b1a55dcb58a1`

Pre-registration: `endgame_prereg_eb5b25712a2a0355`

0 candidates cleared the full endgame bar. accepted=false.

Ceiling: computation over released data, not wet-lab or clinical truth.

RPE1 specificity is not_assayed for 18 of 18 candidates, which blocks the pre-registered cell-type-specificity rung.

## Candidate decisions

| rank | gene | decision | main blockers | primary T-cell support |
|---:|---|---|---|---|
| 1 | PGGT1B | `not_cleared_full_bar` | rpe1_not_assayed, no_activation_transcriptome_replay | shifrut_2018_1107 |
| 2 | RCC1L | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 3 | MCAT | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 4 | RWDD2B | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook, no_specific_mechanism | none |
| 5 | CCDC22 | `not_cleared_full_bar` | rpe1_not_assayed, no_activation_transcriptome_replay | shifrut_2018_1107 |
| 6 | GAS2L1 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 7 | SNAP29 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 8 | CYB5RL | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 9 | LETM2 | `not_cleared_full_bar` | rpe1_not_assayed, no_activation_transcriptome_replay, no_hook | shifrut_2018_1109 |
| 10 | DAPK2 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 11 | SCO2 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit | none |
| 12 | CCDC136 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 13 | MITD1 | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 14 | GZMB | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit | none |
| 15 | FANCL | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 16 | TNNC1 | `not_cleared_full_bar` | rpe1_not_assayed, no_activation_transcriptome_replay, no_hook | shifrut_2018_1107 |
| 17 | BCKDHA | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |
| 18 | ZC3H12A | `not_cleared_full_bar` | rpe1_not_assayed, no_supporting_primary_t_cell_hit, no_hook | none |

## Common blocker

- `cell_type_specificity`: `rpe1_not_assayed` for all 18 locked candidates.

## Reproduce

```bash
./prospect defended-discovery-endgame-exhaustion
```
