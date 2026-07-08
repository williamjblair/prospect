# PGGT1B defended evidence

Status: `evidence_attached`. Trust boundary: proposal only.

Defended-discovery status: `not_cleared_full_bar`.
Plain-language status: not cleared full bar.
Honest ceiling: computation over released data, not wet-lab or clinical truth.

This packet does not accept PGGT1B as settled biology. It records the current frozen evidence for the rank-1 candidate and the exact gaps that keep it below the full pre-registered bar.

## Novelty downgrade

PGGT1B is not a first report in T-cell biology. Prior work already links PGGT1B or geranylgeranyl transferase I to T-cell localization, colitis, and effector Treg programs.

Kept claim: Prospect contributes independent released-data support that PGGT1B is a testable activation-transcriptome hypothesis in primary human CD4+ cells.

| PMID | role | title |
|---|---|---|
| 31302143 | direct PGGT1B and T-cell localization prior art | Inhibiting PGGT1B Disrupts Function of RHOA, Resulting in T-cell Expression of Integrin α4β7 and Development of Colitis in Mice. |
| 33207246 | Pggt1b and protein prenylation in effector Treg programs | Protein Prenylation Drives Discrete Signaling Programs for the Differentiation and Maintenance of Effector T(reg) Cells. |
| 30449619 | primary human T-cell CRISPR screen comparator | Genome-wide CRISPR Screens in Primary Human T Cells Reveal Key Regulators of Immune Function. |
| 36002574 | primary T-cell proliferation ORCS comparator | RASA2 ablation in T cells boosts antigen sensitivity and long-term function. |

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
| `depmap_achilles_19q2` | `evidence_attached` | 563 cancer cell lines, median gene effect -0.1009, 0 lines below -1 |
| `carnevale_2022_orcs_1905` | `orthogonal_phenotype` | primary T-cell proliferation screen, PGGT1B non-hit rank 19027 of 19362 |

## Unscored or blocked sources

No unscored public source remains in this packet.

## Kill attempts

| kill | result | missing |
|---|---|---|
| `technical_confound` | `survives_current_frozen_evidence` | guide-level off-target audit would strengthen this kill |
| `essentiality_or_proliferation_artifact` | `survives_current_frozen_evidence` | none |
| `batch_or_dataset_specificity` | `not_cleared` | activation-transcriptome or activation-marker primary T-cell screen |
| `alternative_mechanism` | `survives_current_frozen_evidence` | direct substrate-level assay remains wet-lab work |

## Mechanism dossier

What the data shows:

- 3014 stimulated DE genes after PGGT1B knockdown in the Marson CD4+ Perturb-seq table
- 175 Rest DE genes and K562 1 DE genes in frozen specificity comparators
- Shifrut 2018 ORCS row supports a primary T-cell perturbation context

What is inferred:

- The mechanistic hypothesis is prenylation-dependent small-GTPase and immune-synapse traffic, inferred from PGGT1B function and STRING partners.
- The released data do not directly measure prenylation, RHOA/RAC1/CDC42 localization, or immune-synapse assembly.

STRING partners: FNTA, HEYL, RABGGTA, CCDC112, WTIP, AMMECR1L, FNTB, RAP1A, CDC42, HRAS

## Druggability

Target: `CHEMBL4135`. Caveat: existing compounds and activity rows, not a validated therapy.

| compound | assay | value | document |
|---|---|---|---|
| `CHEMBL41454` | IC50 | 10.0 nM | `CHEMBL1136432` |
| `CHEMBL290161` | IC50 | 10.0 nM | `CHEMBL1136432` |
| `CHEMBL41540` | IC50 | 10.0 nM | `CHEMBL1136432` |
| `CHEMBL287729` | IC50 | 10.0 nM | `CHEMBL1136432` |
| `CHEMBL432477` | IC50 | 10.0 nM | `CHEMBL1136432` |

## Whole-signature driver/passenger summary

52 genes: 12 `evidence_attached`, 22 `associative_only`, 3 `contradicted`, 15 `not_assayed` in the primary Marson substrate.
Frozen ORCS primary T-cell context reduces uncovered genes to 5.

## Wet-lab protocol

System: stimulated primary human CD4+ T cells. Minimum donors: 3. Timepoints: 8h, 48h.

Arms: non_targeting_control, PGGT1B_CRISPRi, FNTA_or_FNTB_pathway_control, viability_control.

Readouts: PGGT1B_knockdown, activation_transcriptome, viability, prenylation_or_small_GTPase_localization.

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
