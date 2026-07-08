# PGGT1B endgame decision

Decision id: `pggt1b_endgame_ae7f491295dfc892`

Pre-registration: `endgame_prereg_eb5b25712a2a0355`

PGGT1B is not cleared full bar under the endgame pre-registration.

It remains an `evidence_attached` hypothesis. accepted=false. The ceiling is computation over released data, not wet-lab or clinical truth.

## Why it does not clear

- RPE1 specificity is not_assayed in the frozen Replogle comparator.
- The strongest independent primary T-cell hit is Shifrut proliferation or stimulation-response support, not an activation-transcriptome replay.

## Bar rungs

| rung | status | basis |
|---|---|---|
| `novel_driver` | `evidence_attached` | rank-1 novelty survivor, 3014 stimulated DE genes, zero CollecTRI targets, absent from the standard T-cell annotation set |
| `zero_drift_reproducibility` | `computationally_reproduced` | frontier replays at 0 drift against root_a8b0dcdd4024e12f |
| `cell_type_specificity` | `not_cleared` | K562 DE is 1, but RPE1 is not_assayed in the locked candidate row. |
| `five_frozen_orthogonal_public_datasets` | `evidence_attached` | frozen PGGT1B snapshots include Shifrut, Schmidt, ORCS T-cell rows, STRING, DICE, GWAS Catalog, ChEMBL, Ensembl homology, and DepMap 19Q2 |
| `readout_comparability` | `not_cleared` | Shifrut supports primary T-cell proliferation or stimulation-response behavior, but no frozen comparator replays the Marson activation-transcriptome breadth for PGGT1B. Schmidt cytokine output remains orthogonal_phenotype. |
| `mechanistic_coherence` | `evidence_attached` | PGGT1B encodes the beta subunit of geranylgeranyl transferase I. The current hypothesis is that perturbing this enzyme changes stimulated CD4+ activation by altering prenylation-dependent small-GTPase and immune-synapse traffic. |
| `real_world_hook` | `evidence_attached` | ChEMBL has target and activity rows for geranylgeranyl transferase type-1 subunit beta. This is a druggability hook, not a therapeutic claim. |
| `falsifiable_experiment` | `evidence_attached` | adequate PGGT1B knockdown produces no candidate-specific activation-program shift at 8h or 48h, or the same effect appears in non-immune controls |

## Kills

- `technical_confound`: `survives_current_frozen_evidence`. Marson records on-target stimulated knockdown and a large stimulated effect, but guide-level audit remains a strengthening item.
- `essentiality_or_proliferation_artifact`: `survives_current_frozen_evidence`. K562 DE is 1 and DepMap Achilles 19Q2 has median gene effect -0.1009 with 0 of 563 lines below -1.
- `batch_or_donor_effect`: `not_cleared`. Shifrut is supportive but not an activation-transcriptome replay; Schmidt cytokine-output non-hit is an orthogonal phenotype, not a contradiction.
- `reverse_causality_or_passenger_marker`: `survives_current_frozen_evidence`. The Marson perturbation effect is causal in this assay, and DICE expression does not by itself explain the signal as only a marker.
- `better_alternative_mechanism`: `survives_current_frozen_evidence`. STRING and ChEMBL support the geranylgeranylation mechanism rather than an unrelated pathway node, while direct substrate-level biology remains wet-lab work.

Next candidate: `RCC1L`.

## Reproduce

```bash
./prospect pggt1b-endgame-decision
```
