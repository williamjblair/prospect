# MCAT defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Defended-discovery status: `not_cleared_full_bar`.
Plain-language status: not cleared full bar.
Honest ceiling: computation over released data, not wet-lab or clinical truth.

## Frozen evidence

| source | status | summary |
|---|---|---|
| `marson_frontier` | `computationally_reproduced` | 780 stimulated DE genes, 113 Rest DE genes |
| `replogle_specificity` | `evidence_attached` | K562 20; RPE1 None |
| `primary_t_cell_screen_support` | `evidence_attached` | no supporting Shifrut or Schmidt primary T-cell hit in the frozen cross-validation packet |
| `schmidt_2022_orcs_2427` | `orthogonal_phenotype` | cytokine-production non-hit, not a comparable activation-transcriptome contradiction |
| `string_network` | `evidence_attached` | top partners: OXSM, NDUFAB1, FASN, ACACA, ACACB |
| `dice_expression` | `evidence_attached` | activated CD4 mean TPM 23.3 |
| `open_targets_overlay` | `evidence_attached` | no_immune_or_hematologic_context |

## Clearance failures

| rung | reason |
|---|---|
| `independent_primary_t_cell_support` | MCAT has no supporting hit in Shifrut 2018 and Schmidt remains an orthogonal cytokine-production phenotype |
| `real_world_hook` | the bounded Open Targets overlay has no selected immune or hematologic context for MCAT |
| `specific_mechanism` | STRING context points to fatty-acid and mitochondrial metabolism, but not a specific stimulated CD4+ activation mechanism |

## Kill attempts

| kill | result | basis |
|---|---|---|
| `technical_confound` | `survives_current_frozen_evidence` | the frozen campaign row has on-target stimulated knockdown |
| `essentiality_or_proliferation_artifact` | `survives_current_frozen_evidence` | Rest DE is 113 and K562 DE is 20, within the pre-registered ceiling |
| `batch_or_dataset_specificity` | `not_cleared` | no supporting primary T-cell screen hit is attached |
| `alternative_mechanism` | `not_cleared` | current STRING context does not establish a specific activation mechanism |

Decision recommendation: `demote_and_advance`.
Next candidate: RWDD2B at rank 4.

Rebuild:

```bash
./prospect mcat-defended-evidence
```
