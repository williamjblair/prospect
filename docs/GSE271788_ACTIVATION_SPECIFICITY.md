# Activation-specificity sensitivity audit

Status: `orthogonal_phenotype`
Accepted: `false`
Proposal: `proposal_bd7167ea0cbbb182`
Receipt: `rcpt_7ed7d05f121995c9`
Pre-registration: `prereg_2fd47506461840d1`

## Result

Across 76 complete-case perturbation targets, the partial Spearman association between
Marson `Stim48hr` reach and independent day-eight activated primary-CD4 knockout reach is
0.045808 after controlling for Marson `Rest` reach and study batch.
The one-sided 10,000-permutation P value is 0.35246475. The
within-batch bootstrap 95 percent interval is [-0.166003,
0.260058].

This sensitivity is typed `orthogonal_phenotype` under pre-registration
`prereg_2fd47506461840d1`. Broad cross-study perturbation reach remains reproduced, but incremental activation-specific reach is not established under the locked sensitivity rule. This is computation over
released data, not wet-lab or clinical truth. The independent day-eight context is not identical to
a Marson condition, so this analysis cannot earn `contradicted`.

## Adversarial kills

| Kill | Result | Detail |
| --- | --- | --- |
| Batch direction | fail | GSE171737 n=21, partial rho=0.107485; GSE271788 n=55, partial rho=-0.023537. |
| General machinery | fail | n=58, partial rho=-0.072090; 18 targets above 25 excluded; 2 K562 gaps retained and typed `not_assayed`. |
| Influential target | fail | Minimum leave-one-out partial rho=-0.010307 after excluding RBCK1. |
| Subset instability | fail | 9362 of 10000 leave-five-out runs positive; minimum=-0.092327. |
| Cell-count confound | pass | n=76, partial rho=0.055116 after adding ranked median live-cell count. |

## Missingness and descriptive sensitivity

- Starting overlap: 79 targets.
- Complete cases: 76 targets.
- Missing condition rows: [{"gene": "BCL11B", "missing_conditions": ["Rest"]}, {"gene": "KMT2A", "missing_conditions": ["Rest"]}, {"gene": "SREBF1", "missing_conditions": ["Rest"]}].
- Editing-efficiency subset: n=55, available batches=gse271788_iei_background.
- Editing-efficiency partial rho changes from
  -0.023537 to
  -0.016593 when ranked editing efficiency is
  added. This is descriptive only and cannot determine status.

No output changes accepted state. The signed root remains `root_a8b0dcdd4024e12f`.

## Replay

```bash
python frontier/gse271788_activation_specificity.py --check
```
