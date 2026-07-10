# Activation-specificity sensitivity pre-registration

Status: `evidence_attached`
Accepted: `false`
Pre-registration: `prereg_2fd47506461840d1`

## Locked question

Does Marson `Stim48hr` transcriptomic reach retain positive association with independent day-eight
activated primary-CD4 knockout reach after controlling for Marson `Rest` reach and independent-study
batch?

This is a secondary sensitivity analysis. It does not replace or change the existing 79-target
cross-study calibration. It is computation over released data, not wet-lab or clinical truth.

## Frozen population

- Start from the 79 targets in `examples/data/gse271788/target_reach.csv` that overlap Marson.
- Use complete cases with both Marson `Rest` and `Stim48hr` values.
- Derive and assert the complete-case count. The expected count is 76.
- Never replace missing `Rest` values with zero.
- Keep `gse171737_il2ra_regulators` and `gse271788_iei_background` as fixed strata.

The pre-registration binds the SHA-256 hashes of the independent source manifest, target-reach
projection, metadata summary, frozen Marson table, frozen Replogle K562 table, and sealed primary
cross-study protocol.

## Locked statistic

1. Rank independent reach, `Stim48hr` reach, and `Rest` reach with average ranks for ties.
2. Encode batch as one binary fixed-effect column.
3. Regress ranked `Stim48hr` reach on an intercept, ranked `Rest` reach, and batch.
4. Regress ranked independent reach on the same design matrix.
5. Compute Pearson correlation between the residual vectors.
6. Report the result as partial Spearman rho.

No log transform, winsorization, trimming, or outcome-informed threshold change is allowed.

## Locked inference

- Seed: `271789`.
- Permutations: 10,000.
- Bootstrap samples: 10,000.
- Alternative: partial rho is greater than zero.
- Permutation: Freedman-Lane residual permutation within each batch.
- P value: `(permuted at least observed + 1) / 10001`.
- Bootstrap: sample targets with replacement within each batch while preserving batch sizes.
- Interval: percentile 95 percent interval.

## Status-determining kills

- `batch_direction`: the partial association is positive in each batch with enough complete cases.
- `general_machinery`: after excluding targets with Replogle K562 reach above 25, the partial
  association remains positive. K562 gaps remain `not_assayed`.
- `influential_target`: every leave-one-target-out partial association remains positive.
- `subset_instability`: at least 95 percent of 10,000 seeded leave-five-target-out associations are
  positive.
- `cell_count_confound`: the partial association remains positive after adding ranked median
  live-cell count to the fixed covariates.

Editing efficiency is systematically missing for the older batch. Its available subset is
descriptive only, is never imputed, and cannot determine status.

## Locked typing

The extension earns `evidence_attached` only if its one-sided permutation P value is at most `0.01`,
its lower bootstrap bound is above zero, and every status-determining kill passes. Otherwise it is
`orthogonal_phenotype`: broad reach replicates, but incremental activation-specific reach is not
established.

The independent day-eight context is not identical to a Marson condition, so this analysis cannot
earn `contradicted`. Every output remains `accepted=false` with
`human_signature_required`. Signed root `root_a8b0dcdd4024e12f` remains unchanged.

## Replay contract

After the frozen analysis implementation is committed, the result will replay with:

```bash
python frontier/gse271788_activation_specificity.py --check
```
