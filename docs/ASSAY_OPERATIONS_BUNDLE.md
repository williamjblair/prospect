# Gladstone assay operations bundle

Status: `evidence_attached`. Trust boundary: proposal only. This is wet-lab planning, not accepted biological state.

## What this adds

The lab packet names interventions, controls, readouts, and stop rules. This operations bundle adds the bench decision frame for each row: expected positive result, weakening result, rejection result, and missing evidence before acceptance.

## Candidate operations

| rank | gene | queue | expected positive result | weakening result | rejection result |
|---:|---|---|---|---|---|
| 1 | PGGT1B | primary_assay_queue | PGGT1B orthogonal knockdown reproduces a stimulated program shift in Stim8hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, or a broad transfer signal stronger than the CD4+ Stim8hr footprint. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 2 | RCC1L | secondary_assay_queue | RCC1L orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, or a broad transfer signal stronger than the CD4+ Stim48hr footprint. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 3 | MCAT | capacity_assay_queue | MCAT orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, or a broad transfer signal stronger than the CD4+ Stim48hr footprint. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 4 | RWDD2B | capacity_assay_queue | RWDD2B orthogonal knockdown reproduces a stimulated program shift in Stim8hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, or a broad transfer signal stronger than the CD4+ Stim8hr footprint. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |
| 5 | CCDC22 | capacity_assay_queue | CCDC22 orthogonal knockdown reproduces a stimulated program shift in Stim48hr with activation-marker flow cytometry and targeted RNA-seq, without a matched Rest-only or broad non-immune signal. | Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, or a broad transfer signal stronger than the CD4+ Stim48hr footprint. | failed on-target knockdown, no stimulated activation-program shift after knockdown, or a broad non-immune effect that explains the signal better than CD4+ activation gating. |

## Required gates before any accepted state change

- knockdown gate: on-target knockdown passes before interpretation
- specificity gate: stimulated effect is stronger than matched Rest-only signal
- transfer gate: broad non-immune effect does not explain the CD4+ signal
- acceptance gate: new evidence is replayed and human-signed before accepted state changes

## Missing evidence before acceptance

- orthogonal knockdown
- matched donor replicate
- activation-marker flow cytometry
- targeted RNA-seq at 8h and 48h
- human signature over replayed follow-up evidence

## Replay links

- `/data/frontier.json`
- `/data/judge_packet.json`
- `/data/lab_packet.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/campaign_pressure_summary.json`

Rebuild:

```bash
./prospect assay-ops
```
