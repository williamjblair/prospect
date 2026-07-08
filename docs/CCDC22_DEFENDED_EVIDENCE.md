# CCDC22 defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Plain-language status: needs external freeze.
Defended-discovery status: `needs_external_freeze`.
Honest ceiling: computation over released data, not wet-lab or clinical truth.

## Frozen evidence

| source | status | summary |
|---|---|---|
| `marson_frontier` | `computationally_reproduced` | 619 stimulated DE genes, 116 Rest DE genes |
| `replogle_specificity` | `evidence_attached` | K562 13; RPE1 None |
| `primary_t_cell_screen_support` | `evidence_attached` | supporting hit: shifrut_2018_1107 |
| `schmidt_2022_orcs_2427` | `orthogonal_phenotype` | cytokine-production non-hit, not a comparable activation-transcriptome contradiction |
| `string_network` | `evidence_attached` | top partners: CCDC93, VPS35L, COMMD1, COMMD8, COMMD2 |
| `dice_expression` | `evidence_attached` | activated CD4 mean TPM 30.218 |
| `open_targets_overlay` | `evidence_attached` | immune dysregulation-polyendocrinopathy-enteropathy-X-linked syndrome, genetic association score 0.1945 |

## Open gates

| gate | reason |
|---|---|
| `expanded_external_freeze` | the expanded hackathon bar still needs new frozen GWAS Catalog, DepMap, conservation, or additional primary-T-cell comparator evidence |
| `shifrut_replication_depth` | one Shifrut row supports CCDC22, while the second Shifrut row is missing from the frozen packet |
| `human_acceptance` | no human key has accepted a CCDC22 state transition |

## Kill attempts

| kill | result | basis |
|---|---|---|
| `technical_confound` | `survives_current_frozen_evidence` | the frozen campaign row has on-target stimulated knockdown |
| `essentiality_or_proliferation_artifact` | `survives_current_frozen_evidence` | Rest DE is 116 and K562 DE is 13, below the pre-registered artifact ceilings |
| `batch_or_dataset_specificity` | `survives_current_frozen_evidence` | Shifrut 2018 row 1107 supports the candidate in an independent primary T-cell screen |
| `alternative_mechanism` | `survives_current_frozen_evidence` | STRING centers CCDC22 in the CCC and COMMD retromer-associated trafficking complex |

Mechanism: CCDC22 may connect stimulated CD4+ activation state to CCC and COMMD retromer-associated endosomal trafficking.
Real-world hook: immune dysregulation-polyendocrinopathy-enteropathy-X-linked syndrome, genetic association score 0.1945.
Decision recommendation: `hold_and_deepen`.

Rebuild:

```bash
./prospect ccdc22-defended-evidence
```
