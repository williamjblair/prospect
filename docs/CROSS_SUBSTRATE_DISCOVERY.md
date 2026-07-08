# Cross-substrate discovery packet

Status: `computationally_reproduced`.

No accepted state changes. This packet classifies frozen Marson and Replogle count rows into reproducible cross-substrate discovery lanes.

Signed root: `root_a8b0dcdd4024e12f`

## Replay

```bash
./prospect cross-substrate-discovery
```

## Counts

- Marson genes considered: 11526
- K562 overlap: 8112
- RPE1 overlap: 1337
- Any non-immune overlap: 8112
- Campaign rows intersected: 20

## Class Counts

- `shared_cellular_machinery`: 80
- `t_cell_specific_activation`: 409
- `non_immune_only_effect`: 333
- `ambiguous_or_not_tested`: 10704

## Exemplars

| Gene | Class | Rest DE | Stim max DE | K562 DE | RPE1 DE | Campaign rank |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| MED19 | shared_cellular_machinery | 2012 | 3869 | 3716 | 3090 |  |
| TADA2B | shared_cellular_machinery | 4681 | 5920 | 149 | 657 |  |
| BCL10 | t_cell_specific_activation | 1 | 3456 | 2 | not measured |  |
| PGGT1B | t_cell_specific_activation | 175 | 3014 | 1 | not measured | 1 |
| RAC3 | non_immune_only_effect | 0 | 3 | 245 | 3499 |  |
| LAT | ambiguous_or_not_tested | 4 | 5536 | not measured | not measured |  |

## Campaign Intersections

| Rank | Gene | Class | Rest DE | Stim max DE | K562 DE | RPE1 DE |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | PGGT1B | t_cell_specific_activation | 175 | 3014 | 1 | not measured |
| 2 | RCC1L | t_cell_specific_activation | 58 | 1167 | 5 | not measured |
| 3 | MCAT | t_cell_specific_activation | 113 | 780 | 20 | not measured |
| 4 | RWDD2B | t_cell_specific_activation | 190 | 720 | 1 | not measured |
| 5 | CCDC22 | t_cell_specific_activation | 116 | 619 | 13 | not measured |
| 6 | GAS2L1 | t_cell_specific_activation | 20 | 457 | 1 | not measured |
| 7 | SNAP29 | t_cell_specific_activation | 19 | 407 | 1 | not measured |
| 8 | CYB5RL | t_cell_specific_activation | 11 | 389 | 13 | not measured |
| 9 | LETM2 | ambiguous_or_not_tested | 18 | 386 | not measured | not measured |
| 10 | DAPK2 | ambiguous_or_not_tested | 11 | 350 | not measured | not measured |

This packet proves computation over released frozen tables. It does not prove wet-lab result, clinical result, or accepted biological state.
