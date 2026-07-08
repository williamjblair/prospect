# Donor-condition replay packet

Status: `computationally_reproduced`.

No accepted state changes. This packet classifies campaign strongest-condition rows by released donor-correlation and guide-support fields.

Signed root: `root_a8b0dcdd4024e12f`

## Replay

```bash
./prospect donor-replay
```

Refresh source extract from the released h5ad:

```bash
./prospect donor-replay --refresh-source
```

## Counts

- Campaign rows: 20
- Donor supported: 13
- Donor intermediate: 2
- Donor fragile: 4
- Guide limited: 1
- Donor not estimated: 0
- Aggregate not actionable: 0

## Campaign Rows

| Rank | Gene | Condition | Class | DE genes | donor hits min | donor hits mean | guides |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | PGGT1B | Stim8hr | donor_supported | 3014 | 0.6045 | 0.7185 | 2 |
| 2 | RCC1L | Stim48hr | donor_supported | 1167 | 0.8301 | 0.838 | 2 |
| 3 | MCAT | Stim48hr | donor_supported | 780 | 0.7518 | 0.8064 | 2 |
| 4 | RWDD2B | Stim8hr | donor_fragile | 720 | 0.2946 | 0.3366 | 2 |
| 5 | CCDC22 | Stim48hr | donor_supported | 619 | 0.6594 | 0.6618 | 2 |
| 6 | GAS2L1 | Stim48hr | donor_supported | 457 | 0.7952 | 0.841 | 2 |
| 7 | SNAP29 | Stim8hr | guide_limited | 407 | 0.6918 | 0.7099 | 1 |
| 8 | CYB5RL | Stim48hr | donor_supported | 389 | 0.7619 | 0.7967 | 2 |
| 9 | LETM2 | Stim48hr | donor_intermediate | 386 | 0.5147 | 0.5358 | 2 |
| 10 | DAPK2 | Stim48hr | donor_supported | 350 | 0.6699 | 0.7337 | 2 |
| 11 | SCO2 | Stim8hr | donor_supported | 369 | 0.7672 | 0.8292 | 2 |
| 12 | CCDC136 | Stim48hr | donor_supported | 263 | 0.6016 | 0.6536 | 2 |
| 13 | MITD1 | Stim48hr | donor_supported | 250 | 0.578 | 0.6231 | 2 |
| 14 | GZMB | Stim8hr | donor_fragile | 496 | 0.2266 | 0.2824 | 2 |
| 15 | FANCL | Stim48hr | donor_intermediate | 329 | 0.496 | 0.5587 | 2 |
| 16 | TNNC1 | Stim48hr | donor_fragile | 260 | 0.3248 | 0.3657 | 2 |
| 17 | BCKDHA | Stim8hr | donor_supported | 374 | 0.5236 | 0.617 | 2 |
| 18 | ZC3H12A | Stim8hr | donor_supported | 261 | 0.8033 | 0.8664 | 2 |
| 19 | IRF4 | Stim8hr | donor_fragile | 567 | 0.1875 | 0.2597 | 2 |
| 20 | RXRB | Stim48hr | donor_supported | 422 | 0.7523 | 0.7816 | 2 |

This packet replays released donor-correlation and guide fields for campaign prioritization. It does not prove wet-lab result, clinical result, or accepted biological state.
