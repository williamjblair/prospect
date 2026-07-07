# Wet-lab validation shortlist

These are hypotheses to test, derived from frozen Prospect lookups. The status is `evidence_attached`, not an established biological result.

| rank | gene | stim max DE | Rest DE | K562 DE | CollecTRI targets | assay note |
|---:|---|---:|---:|---:|---:|---|
| 1 | PGGT1B | 3014 | 175 | 1 | 0 | stimulated CD4+ perturbation follow-up |
| 2 | RCC1L | 1167 | 58 | 5 | 0 | stimulated CD4+ perturbation follow-up |
| 3 | MCAT | 780 | 113 | 20 | 0 | stimulated CD4+ perturbation follow-up |
| 4 | RWDD2B | 720 | 190 | 1 | 0 | stimulated CD4+ perturbation follow-up |
| 5 | CCDC22 | 619 | 116 | 13 | 0 | stimulated CD4+ perturbation follow-up |

Selection filters: non-canonical T-cell gene, condition-specific regulator, not an activation-module gene, not an essentiality artifact, Rest DE at or below 250, stimulated DE at or above 500, and no major effect in non-immune Replogle cells where measured.

Rebuild:

```bash
python frontier/validation_sheet.py
```
