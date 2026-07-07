# Campaign review appendix

Status: `evidence_attached`. Trust boundary: proposal only. The appendix ranks assay follow-up work; it does not move accepted state.

Campaign: `campaign_07a2bdd5697274c9`. Candidates: 20. Top gene: `PGGT1B`.

## Audit questions

- Is there an on-target stimulated footprint? Field: `stimulated_signal`. Rule: stimulated DE is above the campaign floor and strongest knockdown is on-target.
- Is the signal activation-skewed rather than housekeeping? Field: `specificity`. Rule: Rest DE remains below the campaign ceiling and non-immune transfer is small where measured.
- What would make the proposal weaker? Field: `stop_rules`. Rule: each row carries explicit reasons to stop or lower priority.

## Lane counts

| lane | rows |
|---|---:|
| bench follow-up | 5 |
| clean specificity | 6 |
| known-regulon anchor | 2 |
| late activation follow-up | 6 |
| top wet-lab bet | 1 |

## Review rows

| rank | gene | lane | decision | stimulated signal | specificity | stop rules |
|---:|---|---|---|---|---|---|
| 1 | PGGT1B | top wet-lab bet | advance_to_assay_design | 3014 DE at Stim8hr | Rest 175 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 2 | RCC1L | late activation follow-up | hold_as_ranked_backup | 1167 DE at Stim48hr | Rest 58 DE, K562 5 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 3 | MCAT | late activation follow-up | hold_as_ranked_backup | 780 DE at Stim48hr | Rest 113 DE, K562 20 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 4 | RWDD2B | bench follow-up | hold_as_ranked_backup | 720 DE at Stim8hr | Rest 190 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 5 | CCDC22 | late activation follow-up | hold_as_ranked_backup | 619 DE at Stim48hr | Rest 116 DE, K562 13 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 6 | GAS2L1 | clean specificity | advance_if_capacity_allows | 457 DE at Stim48hr | Rest 20 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 7 | SNAP29 | clean specificity | advance_if_capacity_allows | 407 DE at Stim8hr | Rest 19 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 8 | CYB5RL | late activation follow-up | hold_as_ranked_backup | 389 DE at Stim48hr | Rest 11 DE, K562 13 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 9 | LETM2 | clean specificity | advance_if_capacity_allows | 386 DE at Stim48hr | Rest 18 DE, K562 not measured, RPE1 not measured | failed on-target knockdown in the stimulated condition; A broad non-immune effect in a follow-up transfer assay would lower priority.; broad non-immune effect appears in a transfer assay |
| 10 | DAPK2 | clean specificity | advance_if_capacity_allows | 350 DE at Stim48hr | Rest 11 DE, K562 not measured, RPE1 not measured | failed on-target knockdown in the stimulated condition; A broad non-immune effect in a follow-up transfer assay would lower priority.; broad non-immune effect appears in a transfer assay |
| 11 | SCO2 | bench follow-up | hold_as_ranked_backup | 369 DE at Stim8hr | Rest 53 DE, K562 0 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 12 | CCDC136 | clean specificity | advance_if_capacity_allows | 263 DE at Stim48hr | Rest 17 DE, K562 0 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 13 | MITD1 | clean specificity | advance_if_capacity_allows | 250 DE at Stim48hr | Rest 11 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 14 | GZMB | bench follow-up | hold_as_ranked_backup | 496 DE at Stim8hr | Rest 261 DE, K562 not measured, RPE1 not measured | failed on-target knockdown in the stimulated condition; A broad non-immune effect in a follow-up transfer assay would lower priority.; Rest effect grows on replicate; broad non-immune effect appears in a transfer assay |
| 15 | FANCL | late activation follow-up | hold_as_ranked_backup | 329 DE at Stim48hr | Rest 110 DE, K562 0 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 16 | TNNC1 | late activation follow-up | hold_as_ranked_backup | 260 DE at Stim48hr | Rest 104 DE, K562 not measured, RPE1 not measured | failed on-target knockdown in the stimulated condition; A broad non-immune effect in a follow-up transfer assay would lower priority.; broad non-immune effect appears in a transfer assay |
| 17 | BCKDHA | bench follow-up | hold_as_ranked_backup | 374 DE at Stim8hr | Rest 291 DE, K562 1 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; A larger Rest effect on replicate would make this look less activation-specific.; Rest effect grows on replicate |
| 18 | ZC3H12A | bench follow-up | hold_as_ranked_backup | 261 DE at Stim8hr | Rest 181 DE, K562 5 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; Loss of the stimulated DE footprint after orthogonal knockdown would lower priority. |
| 19 | IRF4 | known-regulon anchor | use_as_regulon_anchor | 567 DE at Stim8hr | Rest 325 DE, K562 0 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; A larger Rest effect on replicate would make this look less activation-specific.; Rest effect grows on replicate |
| 20 | RXRB | known-regulon anchor | use_as_regulon_anchor | 422 DE at Stim48hr | Rest 308 DE, K562 2 DE, RPE1 not measured | failed on-target knockdown in the stimulated condition; A larger Rest effect on replicate would make this look less activation-specific.; Rest effect grows on replicate |

Rebuild:

```bash
python frontier/campaign_review.py
```
