# CCDC22 defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Plain-language status: computational bar cleared, pending human key.
Defended-discovery status: `computational_bar_cleared_pending_human_key`.
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
| `chembl_target_and_activity` | `evidence_attached` | CHEMBL6066516 with 4 activity rows for coiled-coil domain-containing protein 22 |
| `ensembl_homology` | `evidence_attached` | 195 orthology rows from Ensembl homology |
| `gwas_catalog_gene_lookup` | `evidence_attached` | GWAS Catalog gene endpoint returned no CCDC22 object |
| `depmap_24q2_crispr_gene_effect` | `evidence_attached` | 1150 cancer cell lines, median gene effect -0.2020, 6 lines below -1 |

## Support audit

| source | role | counts for full bar | reason |
|---|---|---|---|
| `replogle_specificity` | `cell_type_specificity` | yes | independent K562 and RPE1 transfer row argues against general-cell-line essentiality |
| `primary_t_cell_screen_support` | `comparable_primary_t_cell_support` | yes | Shifrut primary T-cell row supplies an independent hit for the same broad activation biology |
| `string_network` | `mechanistic_network` | yes | STRING places CCDC22 with CCC, COMMD, and retromer-associated trafficking partners |
| `dice_expression` | `immune_subset_expression` | yes | DICE records CCDC22 expression in activated CD4 T-cell context |
| `open_targets_overlay` | `real_world_hook` | yes | Open Targets supplies immune-dysregulation genetic context |
| `ensembl_homology` | `evolutionary_conservation` | yes | Ensembl homology supplies orthology rows for conservation context |
| `depmap_24q2_crispr_gene_effect` | `essentiality_context` | yes | DepMap supplies broad cancer-cell dependency context for the artifact kill |
| `schmidt_2022_orcs_2427` | `orthogonal_phenotype` | no | cytokine-production non-hit is not a comparable activation-transcriptome contradiction |
| `gwas_catalog_gene_lookup` | `no_support` | no | GWAS Catalog gene endpoint returned no CCDC22 object |
| `chembl_target_and_activity` | `targetability_context` | no | ChEMBL target/activity rows are retained as context, not as proof of an existing compound hook |

## Bar clearance

| rung | status | basis |
|---|---|---|
| `novelty` | `evidence_attached` | rank-5 novelty survivor, absent from CollecTRI and the standard T-cell annotation set |
| `frozen_replay` | `evidence_attached` | 619 stimulated DE genes re-derived from the frozen Marson frontier packet |
| `cell_type_specificity` | `evidence_attached` | K562 13 and RPE1 None in the frozen Replogle specificity row |
| `orthogonal_public_datasets` | `evidence_attached` | Shifrut, Replogle, STRING, DICE, Open Targets, Ensembl homology, and DepMap 24Q2 count toward the full bar; Schmidt, GWAS no-object, and ChEMBL activity rows are retained as non-counted context |
| `mechanism` | `evidence_attached` | STRING places CCDC22 with CCDC93, VPS35L, and COMMD-complex trafficking partners |
| `real_world_hook` | `evidence_attached` | Open Targets supplies immune-dysregulation genetic context and ChEMBL supplies target/activity rows |
| `adversarial_refutation` | `evidence_attached` | technical, artifact, batch, and alternative-mechanism kills survive current frozen evidence |
| `falsifiable_test` | `evidence_attached` | specific CCDC22 CRISPRi activation-marker and RNA-seq experiment is specified |

## Open gates

| gate | reason |
|---|---|
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
Falsifiable experiment: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h.
Refutes if: adequate CCDC22 knockdown produces no reproducible stimulated activation-program shift, or the same shift appears at Rest or under viability loss.
Decision recommendation: `hold_and_deepen`.

Rebuild:

```bash
./prospect ccdc22-defended-evidence
```

Refresh public snapshots before a new scoring pass:

```bash
./prospect ccdc22-defended-evidence --fetch
```
