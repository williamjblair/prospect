# Scannable findings index

Status: `computationally_reproduced`. Source: `frontier/findings.jsonl`.

| rank | finding | genes | readout |
|---:|---|---:|---|
| 1 | `activation_module` | 245 | 245 genes are quiet at Rest and become broad regulators after stimulation. |
| 2 | `regulator_vs_effector` | 18 | 18 field-targeted genes have confirmed knockdown and near-zero stimulated DE. |
| 3 | `essentiality_artifact` | 139 | 139 genes have high Rest reach under the frozen threshold. |
| 4 | `cross_cell_type_transfer` | 377 | The high-Rest group has broader K562 effects than the activation module among covered genes. |
| 5 | `regulon_recovery` | 19 | CollecTRI targets are 4.03x enriched among moved genes, with combined p near 1e-26. |

Rebuild:

```bash
python frontier/finding_index.py
```
