# Wet-lab assay packet

Status: `evidence_attached`. Trust boundary: proposal only. This packet is assay planning, not accepted biological state.

## Controls

- Negative: non-targeting guide, safe-harbor guide, unstimulated matched culture
- Positive: VAV1, LAT, CD3E
- Exclude: failed on-target knockdown, broad non-immune effect, Rest-only transcriptional shift, canonical effector readout without upstream program shift

## Candidate rows

| rank | gene | primary readout | stim max DE | Rest DE | K562 DE | score |
|---:|---|---|---:|---:|---:|---:|
| 1 | PGGT1B | stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h | 3014 | 175 | 1 | 3389 |
| 2 | RCC1L | stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h | 1167 | 58 | 5 | 1659 |
| 3 | MCAT | stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h | 780 | 113 | 20 | 1217 |
| 4 | CCDC22 | stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h | 619 | 116 | 13 | 1053 |
| 5 | CYB5RL | stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h | 389 | 11 | 13 | 928 |

## Replay links

- `/data/frontier.json`
- `/data/agent_campaign.json`
- `/data/campaign_challenger_ledger.json`
- `/data/pggt1b_deep_dive.json`
- `/data/receipt_bridge/receipt_contract.json`

Rebuild:

```bash
python frontier/lab_packet.py
```
