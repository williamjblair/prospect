# Campaign disagreement triage

Status: `evidence_attached`. Trust boundary: proposal only. Model disagreement can prioritize review; it cannot accept state.

Probe: `campaign_probe_0890c20aed2180b0`. Campaign: `campaign_07a2bdd5697274c9`.

## Summary

- `more_aggressive`: 4
- `secondary_assay_queue`: 1
- `capacity_assay_queue`: 3

## Triage rows

| rank | gene | deterministic decision | Claude probe | triage decision | assay gate |
|---:|---|---|---|---|---|
| 2 | RCC1L | hold_as_ranked_backup | advance_to_assay_design | secondary_assay_queue | orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion |
| 3 | MCAT | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 4 | RWDD2B | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |
| 5 | CCDC22 | hold_as_ranked_backup | advance_if_capacity_allows | capacity_assay_queue | orthogonal knockdown and non-immune transfer check before spending primary assay capacity |

Rebuild:

```bash
python frontier/campaign_triage.py
```
