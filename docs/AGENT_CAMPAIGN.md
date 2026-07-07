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

Rebuild:

```bash
python frontier/agent_campaign.py
```
