# RWDD2B defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Defended-discovery status: `not_cleared_full_bar`.
Plain-language status: not cleared full bar.
Honest ceiling: computation over released data, not wet-lab or clinical truth.

## Frozen evidence

| source | status | summary |
|---|---|---|
| `marson_frontier` | `computationally_reproduced` | 720 stimulated DE genes, 190 Rest DE genes |
| `replogle_specificity` | `evidence_attached` | K562 1; RPE1 None |
| `primary_t_cell_screen_support` | `evidence_attached` | no supporting Shifrut or Schmidt primary T-cell hit in the frozen cross-validation packet |
| `schmidt_2022_orcs_2427` | `orthogonal_phenotype` | cytokine-production non-hit, not a comparable activation-transcriptome contradiction |
| `string_network` | `evidence_attached` | no STRING partners attached in frozen packet |
| `dice_expression` | `evidence_attached` | activated CD4 mean TPM 7.941 |
| `open_targets_overlay` | `evidence_attached` | no_immune_or_hematologic_context |

## Clearance failures

| rung | reason |
|---|---|
| `independent_primary_t_cell_support` | RWDD2B has no supporting hit in Shifrut 2018 and Schmidt remains an orthogonal cytokine-production phenotype |
| `real_world_hook` | the bounded Open Targets overlay has no selected immune or hematologic context for RWDD2B |
| `specific_mechanism` | no STRING partners are attached, so the frozen packet does not state a specific stimulated CD4+ activation mechanism |

## Kill attempts

| kill | result | basis |
|---|---|---|
| `technical_confound` | `survives_current_frozen_evidence` | the frozen campaign row has on-target stimulated knockdown |
| `essentiality_or_proliferation_artifact` | `not_cleared` | Rest DE is 190, so the non-activation artifact kill remains open |
| `batch_or_dataset_specificity` | `not_cleared` | no supporting primary T-cell screen hit is attached |
| `alternative_mechanism` | `not_cleared` | no STRING network or disease hook supplies a specific activation mechanism |

Decision recommendation: `demote_and_advance`.
Next candidate: CCDC22 at rank 5.

Rebuild:

```bash
./prospect rwdd2b-defended-evidence
```
