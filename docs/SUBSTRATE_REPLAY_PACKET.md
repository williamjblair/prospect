# Substrate replay packet

Status: `computationally_reproduced`.

No accepted state changes. This packet shows the checker contract replaying across primary human CD4+ T cells, K562, and RPE1 while keeping the signed frontier root unchanged.

Signed root: `root_a8b0dcdd4024e12f`

## Replay

```bash
./prospect substrate-replay
```

## Frozen Substrates

- `marson2025_cd4_perturbseq`: primary human cd4 t cells
- `replogle2022_k562_gwps`: k562 non immune cell line
- `replogle2022_rpe1`: rpe1 non immune cell line

## Results

- T-cell regulators compared: 377
- Essentiality-artifact regulators reproduced in K562: 70 of 129 (0.5426)
- Activation or effector regulators cell-type-specific: 199 of 248 (0.8024)

## Example Rows

| Gene | Class | Marson CD4 status | K562 status | K562 DE | RPE1 DE |
| --- | --- | --- | --- | ---: | ---: |
| MED19 | shared_cellular_machinery | supported | supported | 3716 | 3090 |
| BCL10 | t_cell_specific_regulation | needs_qualification | refuted | 2 | None |
| TADA2B | shared_cellular_machinery | supported | supported | 149 | 657 |
| LAT | t_cell_specific_regulation | supported | unsupported | None | None |

This packet proves replay of computation over released frozen tables. It does not prove wet-lab truth, clinical truth, or accepted biological state.
