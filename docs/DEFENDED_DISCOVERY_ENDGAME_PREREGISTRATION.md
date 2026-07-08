# Defended discovery endgame pre-registration

Pre-registration id: `endgame_prereg_cc12f4edc74c23b1`

Frontier root: `root_a8b0dcdd4024e12f`

Status: `evidence_attached`. accepted=false. Trust boundary: `proposal_only`.

Ceiling: computation over released data, not wet-lab or clinical truth.

## Locked candidate order

Candidates must be evaluated in this order. A prior packet is evidence only under this new bar.

| rank | gene | Marson stimulated DE | strongest condition | K562 DE | current tier |
|---:|---|---:|---|---:|---|
| 1 | PGGT1B | 3014 | Stim8hr | 1 | screen_hit_plus_context |
| 2 | RCC1L | 1167 | Stim48hr | 5 | context_only |
| 3 | MCAT | 780 | Stim48hr | 20 | context_only |
| 4 | RWDD2B | 720 | Stim8hr | 1 | context_only |
| 5 | CCDC22 | 619 | Stim48hr | 13 | screen_hit_plus_context |
| 6 | GAS2L1 | 457 | Stim48hr | 1 | context_only |
| 7 | SNAP29 | 407 | Stim8hr | 1 | context_only |
| 8 | CYB5RL | 389 | Stim48hr | 13 | context_only |
| 9 | LETM2 | 386 | Stim48hr |  | screen_hit_plus_context |
| 10 | DAPK2 | 350 | Stim48hr |  | context_only |
| 11 | SCO2 | 369 | Stim8hr | 0 | context_only |
| 12 | CCDC136 | 263 | Stim48hr | 0 | context_only |
| 13 | MITD1 | 250 | Stim48hr | 1 | context_only |
| 14 | GZMB | 496 | Stim8hr |  | context_only |
| 15 | FANCL | 329 | Stim48hr | 0 | context_only |
| 16 | TNNC1 | 260 | Stim48hr |  | screen_hit_plus_context |
| 17 | BCKDHA | 374 | Stim8hr | 1 | context_only |
| 18 | ZC3H12A | 261 | Stim8hr | 5 | context_only |

## Bar

- `novel_driver`: strong causal Marson CD4+ activation driver, absent from CollecTRI and standard T-cell regulator annotations
- `zero_drift_reproducibility`: re-derives from frozen data with frontier drift equal to zero
- `cell_type_specificity`: inert or housekeeping in Replogle K562, with RPE1 only where covered; RPE1 non-coverage is not_assayed context, not a failed rung
- `five_frozen_orthogonal_public_datasets`: at least five public comparator datasets are frozen, content-addressed, and scored
- `readout_comparability`: agreement or contradiction is assigned only when the comparator tests a comparable phenotype
- `mechanistic_coherence`: specific pathway, molecular role, and expected activation readout are stated
- `real_world_hook`: druggable target, disease-genetics link, or decisive correction of a named consensus claim
- `falsifiable_experiment`: one stimulated primary human CD4+ CRISPRi experiment would refute the hypothesis

## Required frozen public dataset slots

- `primary_t_cell_crispr_or_perturbseq`: comparable perturbation support or an explicitly typed orthogonal phenotype
- `gwas_catalog_immune_traits`: disease-genetics hook or absence of hook
- `depmap_dependency`: broad dependency and proliferation-artifact kill
- `protein_interaction_network`: mechanistic coherence and alternative-mechanism kill
- `immune_subset_expression_atlas`: immune-cell expression context and cell-context kill
- `drugbank_or_chembl_target_hook`: druggability hook or evidence that no such hook is present

## Pre-registered kills

- `technical_confound`: fails if the apparent Marson effect is explained by failed knockdown, off-target labeling, missing on-target stimulated perturbation, or one unstable guide. Evidence: Marson perturbation-quality fields and any released guide-level evidence available for the candidate.
- `essentiality_or_proliferation_artifact`: fails if Replogle K562, DepMap, or another dependency source explains the signal as general growth, viability, or housekeeping biology; RPE1 can fail a covered gene but missing RPE1 does not fail it. Evidence: Replogle K562, Replogle RPE1 where covered, and frozen DepMap dependency evidence.
- `batch_or_donor_effect`: fails if a comparable public primary T-cell perturbation dataset directly tests the activation-driver claim and shows no compatible effect. Evidence: Shifrut, Schmidt if comparable, or another frozen primary T-cell perturbation screen.
- `reverse_causality_or_passenger_marker`: fails if expression, disease, or perturbation evidence supports the gene as a downstream activation marker or passenger rather than a driver. Evidence: DICE or equivalent expression, GWAS Catalog, and primary perturbation evidence.
- `better_alternative_mechanism`: fails if protein network, pathway, disease, or chemistry evidence points to a different gene or pathway node as the better causal explanation. Evidence: STRING or BioGRID, ChEMBL or DrugBank, GWAS Catalog, and pathway context.

## Comparability rule

Nonmatching readouts default to `orthogonal_phenotype`, not contradiction.

## Falsifiable experiment

System: stimulated primary human CD4+ T cells.

Refutes if: on-target knockdown does not shift the activation program relative to controls, or shifts only a broad viability or housekeeping signature.

## Reproduce

```bash
./prospect defended-discovery-endgame-preregister
```
