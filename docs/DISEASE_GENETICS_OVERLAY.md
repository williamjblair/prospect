# Disease-genetics overlay packet

Status: `evidence_attached`.

No accepted state changes. This packet attaches external Open Targets disease context to campaign rows without changing Prospect state.

Signed root: `root_a8b0dcdd4024e12f`

## Replay

```bash
./prospect disease-overlay
```

Refresh source extract from Open Targets:

```bash
./prospect disease-overlay --refresh-source
```

## Counts

- Campaign rows: 20
- Rows with external context: 20
- Immune or hematologic context: 10
- Immune or hematologic genetic context: 4
- Immune or hematologic non-genetic context: 6
- No immune or hematologic context: 10

## Campaign Rows

| Rank | Gene | Overlay class | Top context | Evidence type | Score |
| ---: | --- | --- | --- | --- | ---: |
| 1 | PGGT1B | immune_or_hematologic_non_genetic_context | psoriasis | literature | 0.0823 |
| 2 | RCC1L | no_immune_or_hematologic_context |  |  |  |
| 3 | MCAT | no_immune_or_hematologic_context |  |  |  |
| 4 | RWDD2B | no_immune_or_hematologic_context |  |  |  |
| 5 | CCDC22 | immune_or_hematologic_genetic_context | immune dysregulation-polyendocrinopathy-enteropathy-X-linked syndrome | genetic_association | 0.1183 |
| 6 | GAS2L1 | no_immune_or_hematologic_context |  |  |  |
| 7 | SNAP29 | immune_or_hematologic_non_genetic_context | multiple sclerosis | affected_pathway | 0.2038 |
| 8 | CYB5RL | no_immune_or_hematologic_context |  |  |  |
| 9 | LETM2 | immune_or_hematologic_non_genetic_context | multiple sclerosis | affected_pathway | 0.2291 |
| 10 | DAPK2 | no_immune_or_hematologic_context |  |  |  |
| 11 | SCO2 | immune_or_hematologic_genetic_context | B-cell chronic lymphocytic leukemia | genetic_association | 0.2377 |
| 12 | CCDC136 | no_immune_or_hematologic_context |  |  |  |
| 13 | MITD1 | no_immune_or_hematologic_context |  |  |  |
| 14 | GZMB | immune_or_hematologic_genetic_context | vitiligo | genetic_association | 0.3465 |
| 15 | FANCL | immune_or_hematologic_non_genetic_context | acute myeloid leukemia | genetic_literature | 0.4637 |
| 16 | TNNC1 | no_immune_or_hematologic_context |  |  |  |
| 17 | BCKDHA | no_immune_or_hematologic_context |  |  |  |
| 18 | ZC3H12A | immune_or_hematologic_non_genetic_context | inflammatory bowel disease | literature | 0.0864 |
| 19 | IRF4 | immune_or_hematologic_genetic_context | B-cell chronic lymphocytic leukemia | literature | 0.6186 |
| 20 | RXRB | immune_or_hematologic_non_genetic_context | psoriasis | clinical | 0.5839 |

This overlay attaches external disease context to campaign rows. It is not a therapeutic claim, clinical result, or accepted biological state.
