# Gladstone Assay Handoff

This is a one-page wet-lab handoff for Prospect's top follow-up rows from the Marson primary human
CD4+ CRISPRi Perturb-seq screen. It is assay planning, not accepted biological state.

Status for every row remains `evidence_attached`. Receipt submission and this handoff are proposal only.
Accepted state still requires the frozen replay path plus the human signing path, and a
biological conclusion would require new wet-lab evidence.

The current queue follows the campaign challenger ledger: RWDD2B is removed from primary assay
capacity because donor replay is fragile and the gate probe lowered priority. CYB5RL fills the open
slot because it is donor-supported and its disagreement gate was sufficient.

## Assay Frame

Question: which non-canonical perturbations gate the stimulated CD4+ activation program without
behaving like broad housekeeping or non-immune effects?

Intervention: CRISPRi knockdown in primary human CD4+ T cells.

Conditions: Rest, Stim8hr, Stim48hr.

Primary readout: stimulated primary CD4+ T cells, activation-marker flow cytometry plus targeted
RNA-seq at 8h and 48h.

Secondary readout: compare Rest, Stim8hr, and Stim48hr programs against non-targeting and pathway
controls.

Negative controls:

- non-targeting guide
- safe-harbor guide
- unstimulated matched culture

Positive controls:

- VAV1
- LAT
- CD3E

Stop rules:

- failed on-target knockdown
- broad non-immune effect
- Rest-only transcriptional shift
- canonical effector readout without upstream program shift

Promotion rule: advance only if stimulated knockdown shifts the activation program without a
Rest-only or broad non-immune effect. An orthogonal knockdown is required before treating any row as
more than an assay candidate.

## Candidate Queue

| rank | gene | strongest condition | stimulated DE | Rest DE | K562 DE | assay note |
|---:|---|---|---:|---:|---:|---|
| 1 | PGGT1B | Stim8hr | 3014 | 175 | 1 | strongest stimulated footprint, cell-type-specific transfer check, no CollecTRI regulon |
| 2 | RCC1L | Stim48hr | 1167 | 58 | 5 | high stimulated footprint with low Rest and low K562 signal |
| 3 | MCAT | Stim48hr | 780 | 113 | 20 | capacity-gated row because the Rest condition carries a knockdown caveat |
| 4 | CCDC22 | Stim48hr | 619 | 116 | 13 | clean on-target stimulated footprint with selected immune genetic context |
| 5 | CYB5RL | Stim48hr | 389 | 11 | 13 | challenger-added row with low Rest signal, donor support, and sufficient gate probe |

## Monday-Morning Protocol

1. Recreate each perturbation with orthogonal guide design.
2. Confirm on-target knockdown before interpreting any transcriptome shift.
3. Run matched Rest, Stim8hr, and Stim48hr cultures with negative and pathway controls.
4. Read activation markers by flow and a targeted RNA-seq panel at 8h and 48h.
5. Drop any row that fails the stop rules.
6. Promote only rows whose stimulated program shift survives the matched Rest and transfer checks.

## Replay Links

- `/data/lab_packet.json`
- `/data/campaign_challenger_ledger.json`
- `/data/judge_packet.json`
- `/data/frontier.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/receipt_bridge/receipt_contract.json`

Local replay:

```bash
./prospect verify
./prospect lab-pack
python examples/receipt_bridge_client.py
```
