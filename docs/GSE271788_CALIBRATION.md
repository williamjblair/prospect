# Independent primary-CD4 calibration

Status: `evidence_attached`  
Accepted: `false`  
Proposal: `proposal_e32e34a8d41b10ab`  
Receipt: `rcpt_72606a3d666b2d0a`

## Result

Across 79 perturbation targets shared by the released Marson table and the combined
GSE171737/GSE271788 study, Marson `Stim48hr` transcriptomic reach has Spearman rho
0.373895 with the authors' published day-eight activated-CD4 knockout reach.
The one-sided 10,000-permutation P value is 0.00039996; the
bootstrap 95 percent interval is [0.169361,
0.547610].

This earns `evidence_attached` under pre-registration `prereg_3c8226ccc9c0773d`. It is
computation over released data, not wet-lab or clinical truth. The studies use different activation
times and perturbation modalities, so the result attaches evidence for broad activated-CD4 reach.
It does not establish condition-level equivalence and cannot earn `contradicted`.

## Adversarial kills

| Kill | Result | Detail |
| --- | --- | --- |
| Batch specificity | pass | GSE171737 n=22, rho=0.233267; GSE271788 n=57, rho=0.132866. |
| General machinery | pass | After excluding K562 reach above 25 and K562 gaps, n=59, rho=0.282219. |
| Influential target | pass | Minimum leave-one-target-out rho=0.352218 after excluding MED12. |

The descriptive sensitivity restricted to 60 Marson targets with
on-target knockdown at Stim48hr has rho 0.528999. It is
reported as a sensitivity analysis and did not determine the status.

## Coverage and limits

- Published independent targets: 84.
- Marson overlap: 79.
- Marson `not_assayed`: JAK3, POU2F1, SON, ZNF217, ZNF341.
- MED12 remains an inspected calibration control, not a newly selected discovery.
- No claim in this packet changes the signed frontier.

## Replay

```bash
python frontier/gse271788_preregistration.py --check
python frontier/gse271788_calibration.py --check
```
