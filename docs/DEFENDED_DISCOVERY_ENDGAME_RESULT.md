# Defended discovery endgame result

Ledger id: `endgame_result_488f7edeb8be591c`

Pre-registration: `endgame_prereg_cc12f4edc74c23b1`

Outcome: `defended_lead`. accepted=false.

Ceiling: computation over released data, not wet-lab or clinical truth.

PGGT1B clears the fixed bar as rank 1, pending human key.

RPE1 non-coverage is retained as not_assayed context, not a failed rung.

## Candidate decisions

| rank | gene | decision | blockers or reason | primary T-cell support |
|---:|---|---|---|---|
| 1 | PGGT1B | `clears_fixed_bar_pending_human_key` | rank 1 PGGT1B clears the corrected fixed bar; accepted state still requires a human key and later wet-lab evidence | shifrut_2018_1107 |
| 2 | RCC1L | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 3 | MCAT | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 4 | RWDD2B | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook, no_specific_mechanism | none |
| 5 | CCDC22 | `not_selected_after_rank1_lead` | rank 1 PGGT1B cleared first in the locked order; CCDC22 remains a supported alternative proposal, not accepted state | shifrut_2018_1107 |
| 6 | GAS2L1 | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 7 | SNAP29 | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets | none |
| 8 | CYB5RL | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 9 | LETM2 | `not_cleared_full_bar` | k562_not_assayed, insufficient_covering_datasets | shifrut_2018_1109 |
| 10 | DAPK2 | `not_cleared_full_bar` | k562_not_assayed, no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 11 | SCO2 | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets | none |
| 12 | CCDC136 | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 13 | MITD1 | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 14 | GZMB | `not_cleared_full_bar` | k562_not_assayed, no_supporting_primary_t_cell_hit, insufficient_covering_datasets | none |
| 15 | FANCL | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets | none |
| 16 | TNNC1 | `not_cleared_full_bar` | k562_not_assayed, insufficient_covering_datasets, no_hook | shifrut_2018_1107 |
| 17 | BCKDHA | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets, no_hook | none |
| 18 | ZC3H12A | `not_cleared_full_bar` | no_supporting_primary_t_cell_hit, insufficient_covering_datasets | none |

## Not-assayed context

- `rpe1_not_assayed`: retained for all 18 candidates, never counted as a blocking failure.

## Reproduce

```bash
./prospect defended-discovery-endgame-result
```
