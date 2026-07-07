# Agent campaign leaderboard

Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from this campaign.

The campaign widens the single-agent result into a ranked bench of follow-up hypotheses. Every row is a frozen Prospect lookup: non-canonical, condition-specific, not housekeeping, on-target under stimulation, and inert in non-immune cells where measured.

| rank | gene | stim max DE | Rest DE | K562 DE | CollecTRI targets | score |
|---:|---|---:|---:|---:|---:|---:|
| 1 | PGGT1B | 3014 | 175 | 1 | 0 | 3389 |
| 2 | RCC1L | 1167 | 58 | 5 | 0 | 1659 |
| 3 | MCAT | 780 | 113 | 20 | 0 | 1217 |
| 4 | RWDD2B | 720 | 190 | 1 | 0 | 1080 |
| 5 | CCDC22 | 619 | 116 | 13 | 0 | 1053 |
| 6 | GAS2L1 | 457 | 20 | 1 | 0 | 987 |
| 7 | SNAP29 | 407 | 19 | 1 | 0 | 938 |
| 8 | CYB5RL | 389 | 11 | 13 | 0 | 928 |
| 9 | LETM2 | 386 | 18 |  | 0 | 918 |
| 10 | DAPK2 | 350 | 11 |  | 0 | 889 |
| 11 | SCO2 | 369 | 53 | 0 | 0 | 866 |
| 12 | CCDC136 | 263 | 17 | 0 | 0 | 796 |
| 13 | MITD1 | 250 | 11 | 1 | 0 | 789 |
| 14 | GZMB | 496 | 261 |  | 0 | 785 |
| 15 | FANCL | 329 | 110 | 0 | 0 | 769 |
| 16 | TNNC1 | 260 | 104 |  | 0 | 706 |
| 17 | BCKDHA | 374 | 291 | 1 | 0 | 633 |
| 18 | ZC3H12A | 261 | 181 | 5 | 0 | 630 |
| 19 | IRF4 | 567 | 325 | 0 | 59 | 553 |
| 20 | RXRB | 422 | 308 | 2 | 15 | 469 |

## Review lane

| rank | gene | lane | why it is interesting | What would weaken it | primary readout |
|---:|---|---|---|---|---|
| 1 | PGGT1B | top wet-lab bet | PGGT1B has the largest stimulated footprint in the campaign, 3014 DE genes at Stim8hr, with K562 DE 1. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim8hr transcriptional program |
| 2 | RCC1L | late activation follow-up | RCC1L passes the non-canonical, on-target, CD4-specific filter with 1167 DE genes at Stim48hr. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |
| 3 | MCAT | late activation follow-up | MCAT passes the non-canonical, on-target, CD4-specific filter with 780 DE genes at Stim48hr. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |
| 4 | RWDD2B | bench follow-up | RWDD2B passes the non-canonical, on-target, CD4-specific filter with 720 DE genes at Stim8hr. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim8hr transcriptional program |
| 5 | CCDC22 | late activation follow-up | CCDC22 passes the non-canonical, on-target, CD4-specific filter with 619 DE genes at Stim48hr. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |
| 6 | GAS2L1 | clean specificity | GAS2L1 is nearly silent at Rest but crosses the campaign threshold after stimulation, with K562 DE 1. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |
| 7 | SNAP29 | clean specificity | SNAP29 is nearly silent at Rest but crosses the campaign threshold after stimulation, with K562 DE 1. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim8hr transcriptional program |
| 8 | CYB5RL | late activation follow-up | CYB5RL is nearly silent at Rest but crosses the campaign threshold after stimulation, with K562 DE 13. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |
| 9 | LETM2 | clean specificity | LETM2 is nearly silent at Rest but crosses the campaign threshold after stimulation, with no K562 measurement. | A broad non-immune effect in a follow-up transfer assay would lower priority. | Stim48hr transcriptional program |
| 10 | DAPK2 | clean specificity | DAPK2 is nearly silent at Rest but crosses the campaign threshold after stimulation, with no K562 measurement. | A broad non-immune effect in a follow-up transfer assay would lower priority. | Stim48hr transcriptional program |
| 11 | SCO2 | bench follow-up | SCO2 passes the non-canonical, on-target, CD4-specific filter with 369 DE genes at Stim8hr. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim8hr transcriptional program |
| 12 | CCDC136 | clean specificity | CCDC136 is nearly silent at Rest but crosses the campaign threshold after stimulation, with K562 DE 0. | Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. | Stim48hr transcriptional program |

Rebuild:

```bash
python frontier/agent_campaign.py
```
