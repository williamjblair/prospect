# Substrate coverage report

Prospect now routes external claims to a contextually appropriate frozen substrate.
The route is still proposal only: `accepted=false`, `human_signature_required`.

Ceiling: computation over released data, not wet-lab or clinical truth.

## Sade-Feldman signature coverage

- Before ORCS primary T-cell context: 15 of 52 genes were `not_assayed` in the primary Marson CD4+ substrate.
- After frozen ORCS primary T-cell context: 5 of 52 genes remain uncovered by primary T-cell perturbation context.
- ORCS primary T-cell covered genes: CLIC1, FOXP1, GZMK, HLA-DPA1, HLA-DPB1, HLA-DRA, HLA-DRB1, LEF1, RGPD5, TIGIT.

The ORCS rows shrink uncovered biology. They do not silently accept state, and they stay orthogonal context unless the submitted claim is about that phenotype.

## Route examples

- T-cell or immunotherapy claim: `marson_cd4_activation`.
- K562 claim: `replogle_k562`.
- RPE1 claim: `replogle_rpe1`.

## Reproduce

```bash
./prospect substrate-coverage
```
