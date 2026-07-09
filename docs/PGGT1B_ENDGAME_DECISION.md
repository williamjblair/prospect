# PGGT1B endgame decision

Decision id: `pggt1b_endgame_7950a9837c2f7120`

Pre-registration: `endgame_prereg_cc12f4edc74c23b1`

PGGT1B is retained as the rank-1 proposal-only lead under the endgame pre-registration.

It remains an `evidence_attached` hypothesis. accepted=false. The ceiling is computation over released data, not wet-lab or clinical truth.

## Why it is not accepted state

- No human key has accepted PGGT1B into frontier state.
- This is computation over released data, not wet-lab or clinical truth.

## Bar rungs

| rung | status | basis |
|---|---|---|
| `novel_driver` | `evidence_attached` | rank-1 novelty survivor, 3014 stimulated DE genes, zero CollecTRI targets, absent from the standard T-cell annotation set |
| `zero_drift_reproducibility` | `computationally_reproduced` | frontier replays at 0 drift against root_a8b0dcdd4024e12f |
| `cell_type_specificity` | `evidence_attached` | K562 DE is 1, arguing against a general-cell-line artifact. RPE1 is not_assayed context, not a failed rung, because the frozen RPE1 gwps comparator is sparse. |
| `five_frozen_orthogonal_public_datasets` | `evidence_attached` | frozen PGGT1B snapshots include Shifrut, Schmidt, ORCS T-cell rows, STRING, DICE, GWAS Catalog, ChEMBL, Ensembl homology, and DepMap 19Q2 |
| `readout_comparability` | `evidence_attached` | Shifrut 1107 supplies independent primary T-cell perturbation support. Schmidt cytokine output and Carnevale proliferation are retained as orthogonal_phenotype, not contradictions to a broad activation-transcriptome hypothesis. |
| `mechanistic_coherence` | `evidence_attached` | PGGT1B encodes the beta subunit of geranylgeranyl transferase I. The current hypothesis is that perturbing this enzyme changes stimulated CD4+ activation by altering prenylation-dependent small-GTPase and immune-synapse traffic. |
| `real_world_hook` | `evidence_attached` | ChEMBL has target and activity rows for geranylgeranyl transferase type-1 subunit beta. This is a druggability hook, not a therapeutic claim. |
| `falsifiable_experiment` | `evidence_attached` | adequate PGGT1B knockdown produces no candidate-specific activation-program shift at 8h or 48h, or the same effect appears in non-immune controls |

## Kills

- `technical_confound`: `survives_current_frozen_evidence`. Marson records on-target stimulated knockdown and a large stimulated effect, but guide-level audit remains a strengthening item.
- `essentiality_or_proliferation_artifact`: `survives_current_frozen_evidence`. K562 DE is 1 and DepMap Achilles 19Q2 has median gene effect -0.1009 with 0 of 563 lines below -1.
- `batch_or_donor_effect`: `survives_current_frozen_evidence`. Shifrut 1107 independently supports PGGT1B in primary T-cell perturbation context; Schmidt remains orthogonal_phenotype, not a contradiction.
- `reverse_causality_or_passenger_marker`: `survives_current_frozen_evidence`. The Marson perturbation effect is causal in this assay, and DICE expression does not by itself explain the signal as only a marker.
- `better_alternative_mechanism`: `survives_current_frozen_evidence`. STRING and ChEMBL support the geranylgeranylation mechanism rather than an unrelated pathway node, while direct substrate-level biology remains wet-lab work.

Next candidate: `none`.

## Reproduce

```bash
./prospect pggt1b-endgame-decision
```
