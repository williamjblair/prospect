# Defended discovery pre-registration

Status: `evidence_attached`. Trust boundary: proposal only. This is a content-sealed plan, not accepted frontier state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

Frontier root: `root_a8b0dcdd4024e12f`.
Candidate set: `discovery_35a9129da0c18f80`.
Pre-registration id: `prereg_9f31fbf1e6c1cf10`.
Content seal: `prereg_sig_2c4a16cbb8bbeec5`.

## Fixed bar

A candidate must clear every rung below and at least 5 frozen public comparator datasets.

- `novelty`: strong stimulated Marson CD4+ activation effect, absent from CollecTRI and standard T-cell regulator annotations
- `frozen_replay`: re-derives from frozen Prospect packets at zero drift
- `cell_type_specificity`: not a broad Replogle K562 or RPE1 effect under the registered ceiling
- `five_orthogonal_public_datasets`: at least five frozen public comparator datasets support the candidate or establish the honest limit of the claim
- `phenotype_comparability`: agreement or contradiction can be assigned only after readout comparability is documented
- `mechanism`: a specific mechanism names pathway, molecule class, and expected activation readout
- `real_world_hook`: drug target, disease-genetics link, or named consensus correction
- `falsifiable_experiment`: one CRISPRi experiment in stimulated primary human CD4+ cells would refute the hypothesis

## Ranked candidate order

| rank | gene | stim max DE | Rest DE | K562 DE | RPE1 DE | score | current context |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | PGGT1B | 3014 | 175 | 1 |  | 3389 | screen_hit_plus_context |
| 2 | RCC1L | 1167 | 58 | 5 |  | 1659 | context_only |
| 3 | MCAT | 780 | 113 | 20 |  | 1217 | context_only |
| 4 | RWDD2B | 720 | 190 | 1 |  | 1080 | context_only |
| 5 | CCDC22 | 619 | 116 | 13 |  | 1053 | screen_hit_plus_context |
| 6 | GAS2L1 | 457 | 20 | 1 |  | 987 | context_only |
| 7 | SNAP29 | 407 | 19 | 1 |  | 938 | context_only |
| 8 | CYB5RL | 389 | 11 | 13 |  | 928 | context_only |
| 9 | LETM2 | 386 | 18 |  |  | 918 | screen_hit_plus_context |
| 10 | DAPK2 | 350 | 11 |  |  | 889 | context_only |
| 11 | SCO2 | 369 | 53 | 0 |  | 866 | context_only |
| 12 | CCDC136 | 263 | 17 | 0 |  | 796 | context_only |
| 13 | MITD1 | 250 | 11 | 1 |  | 789 | context_only |
| 14 | GZMB | 496 | 261 |  |  | 785 | context_only |
| 15 | FANCL | 329 | 110 | 0 |  | 769 | context_only |
| 16 | TNNC1 | 260 | 104 |  |  | 706 | screen_hit_plus_context |
| 17 | BCKDHA | 374 | 291 | 1 |  | 633 | context_only |
| 18 | ZC3H12A | 261 | 181 | 5 |  | 630 | context_only |

## Public dataset slots

| slot | role | freeze rule |
|---|---|---|
| `additional_primary_t_cell_crispr_screen` | comparable activation or immune-function perturbation screen | content-address before scoring |
| `gwas_catalog_immune_traits` | immune-trait disease-genetics hook | content-address before scoring |
| `depmap_dependency` | broad dependency or proliferation artifact kill | content-address before scoring |
| `protein_interaction_network` | mechanistic coherence or alternative-mechanism kill | content-address before scoring |
| `immune_subset_expression_atlas` | immune-subset expression support or cell-context kill | content-address before scoring |
| `evolutionary_conservation` | orthology or conservation context, not acceptance by itself | content-address before scoring |
| `drugbank_or_chembl_target_hook` | druggability hook or absence of targetable chemistry | content-address before scoring |

## Comparability rule

Agreement or contradiction can be assigned only when the perturbed gene, cell context, readout, direction, and timepoint are comparable to the Marson stimulated activation-transcriptome claim. Non-comparable screens stay `orthogonal_phenotype`.

Locked example: Schmidt 2022 cytokine-production non-hit stays `orthogonal_phenotype` for the broader Marson activation-transcriptome claim.

## Kill attempts

- `technical_confound`: the Marson effect is driven by failed knockdown calls, one unstable guide, off-target behavior, or a missing on-target stimulated perturbation
- `essentiality_or_proliferation_artifact`: Replogle, DepMap, or another frozen dependency source shows broad growth or housekeeping behavior that explains the activation signature better than immune regulation
- `batch_or_dataset_specificity`: a comparable primary T-cell screen or donor-aware public dataset directly tests the activation-regulator claim and shows no compatible effect
- `alternative_mechanism`: network, expression, disease, or chemistry evidence supports a better explanation, such as downstream effector labeling, activation-state marker behavior, or another pathway node

Failure policy: a candidate is removed from the defended-discovery lane if any pre-registered kill criterion is met.

Falsifiable experiment: CRISPRi knockdown in stimulated primary human CD4+ T cells with activation-marker, transcriptome, viability, and proliferation readouts.

Rebuild:

```bash
./prospect defended-discovery-preregister
```
