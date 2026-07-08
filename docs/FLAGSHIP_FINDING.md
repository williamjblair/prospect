# Flagship finding

Status: `evidence_attached`. Trust boundary: proposal only. No module enters accepted state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

Claim: Hypothesis: a prenylation and small-GTPase-trafficking module anchored on PGGT1B modulates stimulated human CD4+ T-cell activation.

## Module

Anchor: PGGT1B. Members: PGGT1B, CCDC22, SNAP29, MITD1.

Mechanism: A proposal that stimulated CD4+ activation depends on prenylation-linked small-GTPase signaling and endosomal trafficking logistics.

## Evidence ladder

| rung | status | detail |
|---|---|---|
| marson_frontier | computationally_reproduced | PGGT1B has 3,014 stimulated DE genes and CCDC22 has 619 in the frozen frontier. |
| independent_primary_t_cell_screen | evidence_attached | PGGT1B and CCDC22 are hits in Shifrut 2018 screen 1107. |
| contradiction | contradicted | All four members are non-hits in Schmidt 2022 screen 2427. |
| network_coherence | evidence_attached | STRING neighborhoods connect PGGT1B to prenylation and small-GTPase partners and the other members to trafficking complexes. |
| immune_expression | evidence_attached | All four members have DICE activated CD4 expression rows. |

## Competing modules

| rank | module | members | score | screen-supported members |
|---:|---|---|---:|---|
| 1 | prenylation_small_gtpase_trafficking | PGGT1B, CCDC22, SNAP29, MITD1 | 222.9 | PGGT1B, CCDC22 |
| 2 | rna_decay_and_effector_context | DAPK2, GZMB, ZC3H12A, TNNC1 | 113.67 | TNNC1 |
| 3 | mitochondrial_metabolic_activation | RCC1L, MCAT, SCO2, BCKDHA | 46.9 |  |

## Refutation experiment

System: stimulated primary human CD4+ T cells.

Perturbations: PGGT1B, CCDC22, SNAP29, MITD1.

Readout: CRISPRi followed by activation-marker flow cytometry and targeted RNA-seq at 8h and 48h.

Refutes if: orthogonal knockdown produces no reproducible activation-program shift for the module, or the effect is equally strong at Rest and in non-immune controls.

Rebuild:

```bash
./prospect flagship-module
```
