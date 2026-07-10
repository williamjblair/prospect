# GSE271788 and GSE171737 calibration pre-registration

Status: `evidence_attached`  
Accepted: `false`  
Pre-registration: `prereg_3c8226ccc9c0773d`

## Locked question

Perturbations with broader transcriptomic reach at Marson Stim48hr also have broader reach in the independent day-eight activated primary-CD4 knockout study.

This analysis is computation over released data, not wet-lab or clinical truth. The independent
day-eight activation context is not identical to any Marson condition. It can attach evidence about
broad activated-CD4 transcriptomic reach, but it cannot earn `contradicted` for a Marson claim.

## Frozen source contract

- Combined raw counts: `GSE271788_dedup_counts.txt.gz`.
- Expected SHA-256: `24f49fc8480a4b7b79fd2fd3ee03a2ca1429a6822f3b6d1ea6c30b13d02bf67c`.
- Expected shape: 311 count columns, 84 targets, three donors per target.
- Expected Marson overlap: 79 targets, with five targets typed `not_assayed`.
- Required published tables before scoring: S4, S5, S11, and S12.
- Missing rows are `not_assayed`, never zero.

If the LFSR table, batch labels, target mapping, or source hashes cannot be pinned exactly, the
analysis stops. No substitute scoring rule is allowed after outcomes are inspected.

## Locked analysis

The primary comparison is frozen Marson `Stim48hr` `n_total_de_genes` against the count of published
downstream effects with mashr LFSR below 0.005. The statistic is Spearman rho over the overlapping
targets. The permutation P value and bootstrap interval use 10,000 iterations and seed 271788.
Rest, Stim8hr, and strongest-condition results are descriptive only.

## Adversarial kills

- `batch_specificity`: Spearman rho must be positive in both the 24-target and 60-target batches.
- `general_machinery`: After excluding targets with Replogle K562 reach above 25, Spearman rho must remain positive.
- `influential_target`: Every leave-one-target-out Spearman rho must remain positive.

The result earns `evidence_attached` only when the primary permutation P value is at most 0.01 and
all three kills pass. Otherwise it is `orthogonal_phenotype`. MED12 remains an inspected calibration
control, not a newly selected discovery.

## Seal and replay

The content signature is `prereg_sig_3c8226ccc9c0773d7e9b165893eb4b0b0cac004e3afc94b7f708dfb12610e174`. It seals this pre-registration only and
does not change accepted state.

```bash
python frontier/gse271788_preregistration.py --check
```
