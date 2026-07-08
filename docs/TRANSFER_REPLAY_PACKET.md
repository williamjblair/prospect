# Transfer replay packet

Status: `computationally_reproduced`.

No accepted state changes. This packet summarizes the signed cross-cell-type finding and keeps the signed frontier root unchanged.

Signed root: `root_a8b0dcdd4024e12f`

Source finding: `cross_cell_type_transfer` / `cid_0d7f599b5770014f`

## Replay

```bash
./prospect transfer-replay
```

## Frozen Tables

- `marson2025_cd4_perturbseq`
- `replogle2022_k562_gwps`
- `replogle2022_rpe1`

## Results

- T-cell regulators compared: 377
- Essentiality-artifact regulators reproduced in K562: 70 of 129 (0.5426)
- Activation or effector genes cell-type-specific: 199 of 248 (0.8024)
- Housekeeping exemplars: MED19, MED12, KDM1A, WDR82, ELOF1
- Immune-specific exemplars: BCL10, CBLB, CD247, CD28, CD3D

The replay strengthens the protocol claim: the same checker interface separates broad cellular machinery from T-cell-specific regulation across independent Perturb-seq releases.
