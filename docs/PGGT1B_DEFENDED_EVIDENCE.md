# PGGT1B defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Defended-discovery status: `not_cleared_full_bar`.
Plain-language status: not cleared full bar.
Honest ceiling: computation over released data, not wet-lab or clinical truth.

This packet does not accept PGGT1B as settled biology. It records the current frozen evidence for the rank-1 candidate and the exact gaps that keep it below the full pre-registered bar.

## Frozen evidence

| source | status | summary |
|---|---|---|
| `marson_frontier` | `computationally_reproduced` | 3014 stimulated DE genes, 175 Rest DE genes, K562 1 |
| `shifrut_2018_orcs_1107` | `evidence_attached` | ORCS hit row with rank 1095 |
| `schmidt_2022_orcs_2427` | `orthogonal_phenotype` | cytokine-production non-hit, not a comparable activation-transcriptome contradiction |
| `string_interaction_partners` | `evidence_attached` | top partners: FNTA, HEYL, RABGGTA, CCDC112, WTIP |
| `dice_expression` | `evidence_attached` | activated CD4 mean TPM 16.101 |
| `open_targets_overlay` | `evidence_attached` | immune_or_hematologic_non_genetic_context |
| `chembl_target_and_activity` | `evidence_attached` | CHEMBL4135 with 25 activity rows against geranylgeranyl transferase type-1 subunit beta |
| `ensembl_homology` | `evidence_attached` | 201 orthology rows from Ensembl homology |
| `gwas_catalog_gene_lookup` | `evidence_attached` | GWAS Catalog gene object at 5:115204012-115262882 |

## Unscored or blocked sources

| source | reason | next step |
|---|---|---|
| `depmap_dependency` | the public portal route returned a browser challenge, so no dependency score is frozen | freeze a public DepMap dependency table or a bounded PGGT1B extract |

## Kill attempts

| kill | result | missing |
|---|---|---|
| `technical_confound` | `survives_current_frozen_evidence` | guide-level off-target audit would strengthen this kill |
| `essentiality_or_proliferation_artifact` | `not_cleared` | DepMap dependency score |
| `batch_or_dataset_specificity` | `not_cleared` | additional comparable primary T-cell screen |
| `alternative_mechanism` | `survives_current_frozen_evidence` | direct substrate-level assay remains wet-lab work |

Mechanism: PGGT1B encodes the beta subunit of geranylgeranyl transferase I. The current hypothesis is that perturbing this enzyme changes stimulated CD4+ activation by altering prenylation-dependent small-GTPase and immune-synapse traffic.

Real-world hook: ChEMBL has target and activity rows for geranylgeranyl transferase type-1 subunit beta. This is a druggability hook, not a therapeutic claim.

Falsifiable experiment: adequate PGGT1B knockdown produces no candidate-specific activation-program shift at 8h or 48h, or the same effect appears in non-immune controls

Rebuild:

```bash
./prospect pggt1b-defended-evidence
```

Refresh public snapshots before a new scoring pass:

```bash
./prospect pggt1b-defended-evidence --fetch
```
