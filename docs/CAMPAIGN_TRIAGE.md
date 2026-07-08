# Campaign disagreement triage

Status: `evidence_attached`. Trust boundary: proposal only. Model disagreement can prioritize review; it cannot accept state.

Probe: `campaign_probe_0c252cc895887e61`. Campaign: `campaign_07a2bdd5697274c9`.

## Summary

- `more_aggressive`: 11
- `secondary_assay_queue`: 5
- `capacity_assay_queue`: 6

## Triage rows

| rank | gene | deterministic decision | Claude probe | triage decision | assay gate |
|---:|---|---|---|---|---|
| 2 | RCC1L | hold_as_ranked_backup | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 4 | RWDD2B | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 5 | CCDC22 | hold_as_ranked_backup | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 8 | CYB5RL | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 11 | SCO2 | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 12 | CCDC136 | advance_if_capacity_allows | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 13 | MITD1 | advance_if_capacity_allows | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 14 | GZMB | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 15 | FANCL | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 17 | BCKDHA | hold_as_ranked_backup | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 18 | ZC3H12A | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |

Rebuild:

```bash
python frontier/campaign_triage.py
```
