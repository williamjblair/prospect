# Gladstone pilot design

Status: `evidence_attached`. Trust boundary: proposal only. This is bench planning, not accepted biological state.

## Sample plan

- Sample: primary human CD4+ T cells
- Donor replicates: 3
- Conditions: Rest, Stim8hr, Stim48hr
- Candidate rows: 5
- Culture arms: 90 culture arms
- Batching: one donor preparation per batch, all conditions and controls matched within donor

## Controls

- Negative: non-targeting guide, safe-harbor guide, unstimulated matched culture
- Positive: VAV1, LAT, CD3E

## Candidate decisions

| rank | gene | queue | primary question | promote if | reject if |
|---:|---|---|---|---|---|
| 1 | PGGT1B | primary_assay_queue | Does PGGT1B reproduce a stimulated CD4+ program shift under Stim8hr after orthogonal knockdown? | PGGT1B orthogonal knockdown reproduces a stimulated program shift in Stim8hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 2 | RCC1L | secondary_assay_queue | Does RCC1L reproduce a stimulated CD4+ program shift under Stim48hr after orthogonal knockdown? | RCC1L orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 3 | MCAT | capacity_assay_queue | Does MCAT reproduce a stimulated CD4+ program shift under Stim48hr after orthogonal knockdown? | MCAT orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 4 | CCDC22 | capacity_assay_queue | Does CCDC22 reproduce a stimulated CD4+ program shift under Stim48hr after orthogonal knockdown? | CCDC22 orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 5 | CYB5RL | capacity_assay_queue | Does CYB5RL reproduce a stimulated CD4+ program shift under Stim48hr after orthogonal knockdown? | CYB5RL orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |

## Gates

- knockdown gate passes before interpretation
- stimulated signal is stronger than matched Rest signal
- non-immune transfer context does not explain the CD4+ signal
- follow-up evidence is replayed before any status change
- human signature is required before accepted state changes

Rebuild:

```bash
./prospect pilot-design
```
