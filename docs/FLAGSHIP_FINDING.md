# Flagship finding

Status: `evidence_attached`. Trust boundary: proposal only. No hypothesis enters accepted state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

Claim: Hypothesis: PGGT1B modulates the stimulated primary human CD4+ T-cell activation transcriptome through geranylgeranylation of small-GTPase signaling that supports immune-synapse traffic.

This is a single PGGT1B hypothesis, not a module claim.

Selection rationale: PGGT1B is selected because it is the rank-1 novelty survivor, has the largest Marson activation-transcriptome signal in the candidate set, has Shifrut support, and has a direct geranylgeranylation link to small-GTPase traffic. CCDC22, LETM2, and TNNC1 remain explicit supported alternatives.

## Evidence ladder

| rung | status | detail |
|---|---|---|
| novelty_funnel | evidence_attached | Rank 1 among 18 novelty survivors after scanning 11,526 frontier genes. |
| marson_frontier | computationally_reproduced | 3014 stimulated DE genes in the frozen Marson replay. |
| replogle_specificity | evidence_attached | T-cell activation signal stays inert in the Replogle K562/RPE1 transfer screen. |
| shifrut_primary_t_cell_screen | evidence_attached | shifrut_2018_1107 |
| schmidt_cytokine_screen | orthogonal_phenotype | A Schmidt 2022 non-hit does not contradict a Marson activation-transcriptome regulator claim unless the claim is narrowed to cytokine production. |
| protein_prenylation_context | evidence_attached | STRING attaches PGGT1B to prenylation and small-GTPase partners: FNTA, HEYL, RABGGTA, CCDC112, WTIP, AMMECR1L, FNTB, RAP1A, CDC42, HRAS. |
| immune_expression | evidence_attached | DICE activated CD4 mean TPM 16.101. |
| disease_genetics | evidence_attached | immune_or_hematologic_non_genetic_context |

## Supported alternatives

| gene | rank | tier | screen support | Schmidt status | why not the flagship |
|---|---:|---|---|---|---|
| CCDC22 | 5 | screen_hit_plus_context | shifrut_2018_1107 | orthogonal_phenotype | Independent Shifrut support and genetic disease context remain visible, but PGGT1B is rank-1 in the novelty funnel and has the strongest direct prenylation hook. |
| LETM2 | 9 | screen_hit_plus_context | shifrut_2018_1109 | orthogonal_phenotype | Independent Shifrut support remains visible, but its mechanism is less directly tied to small-GTPase prenylation and immune-synapse traffic. |
| TNNC1 | 16 | screen_hit_plus_context | shifrut_2018_1107 | orthogonal_phenotype | Independent Shifrut support remains visible, but the current packet lacks a stronger T-cell-specific mechanistic bridge than PGGT1B. |

## Refutation experiment

System: stimulated primary human CD4+ T cells.

Perturbations: PGGT1B.

Readout: CRISPRi followed by activation-marker flow cytometry and targeted RNA-seq at 8h and 48h.

Refutes if: orthogonal PGGT1B knockdown produces no reproducible activation-program shift, or the shift is equally strong at Rest and in non-immune controls.

## Caveats

- Single-lab-derived Marson replay, not wet-lab or clinical truth.
- Schmidt 2022 is an orthogonal cytokine-production phenotype, not a comparable contradiction.
- External context proposes mechanism and assay priority, but does not accept state.

Rebuild:

```bash
./prospect flagship-module
```
