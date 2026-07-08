# Phase 1 discovery campaign

Status: `evidence_attached`. Trust boundary: proposal only. No model output enters accepted state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

Prospect scored 11,526 frozen frontier genes for a novel activation-regulator hypothesis set. The filter keeps genes with a strong stimulated CD4+ effect, low Rest effect, no broad K562 or RPE1 transfer where measured, zero CollecTRI targets, and no standard T-cell regulator annotation.

## Filter counts

| rung | survivors | refused at rung |
|---|---:|---:|
| frontier genes | 11,526 |  |
| condition-specific regulator | 3,463 | 8,063 |
| non-standard T-cell annotation | 3,440 | 23 |
| not artifact or activation module | 3,302 | 138 |
| on-target stimulated knockdown | 3,175 | 127 |
| strong stimulated effect | 60 | 3,115 |
| Rest ceiling | 44 | 16 |
| CollecTRI absent | 40 | 4 |
| Replogle specificity | 18 | 22 |

## Ranked survivors

| rank | gene | stim max DE | Rest DE | K562 DE | RPE1 DE | score |
|---:|---|---:|---:|---:|---:|---:|
| 1 | PGGT1B | 3014 | 175 | 1 |  | 3389 |
| 2 | RCC1L | 1167 | 58 | 5 |  | 1659 |
| 3 | MCAT | 780 | 113 | 20 |  | 1217 |
| 4 | RWDD2B | 720 | 190 | 1 |  | 1080 |
| 5 | CCDC22 | 619 | 116 | 13 |  | 1053 |
| 6 | GAS2L1 | 457 | 20 | 1 |  | 987 |
| 7 | SNAP29 | 407 | 19 | 1 |  | 938 |
| 8 | CYB5RL | 389 | 11 | 13 |  | 928 |
| 9 | LETM2 | 386 | 18 |  |  | 918 |
| 10 | DAPK2 | 350 | 11 |  |  | 889 |
| 11 | SCO2 | 369 | 53 | 0 |  | 866 |
| 12 | CCDC136 | 263 | 17 | 0 |  | 796 |
| 13 | MITD1 | 250 | 11 | 1 |  | 789 |
| 14 | GZMB | 496 | 261 |  |  | 785 |
| 15 | FANCL | 329 | 110 | 0 |  | 769 |
| 16 | TNNC1 | 260 | 104 |  |  | 706 |
| 17 | BCKDHA | 374 | 291 | 1 |  | 633 |
| 18 | ZC3H12A | 261 | 181 | 5 |  | 630 |

## Current lead

PGGT1B is the Phase 1 lead because it has the largest stimulated footprint among the survivor set and remains proposal-only until independent evidence is attached.

Rebuild:

```bash
./prospect discovery-campaign
```
