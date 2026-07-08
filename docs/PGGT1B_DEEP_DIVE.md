# PGGT1B deep dive

Status: `evidence_attached`. Claim scope: hypothesis to test.

## Prospect read

PGGT1B has a large stimulated CD4+ transcriptional footprint at 8h with on-target knockdown, a smaller Rest footprint, no broad K562 footprint, and no CollecTRI regulon annotation.

## Exact frozen facts

| fact | value |
|---|---:|
| Rest DE genes | 175 |
| Rest knockdown | on-target KD |
| Stim8hr DE genes | 3014 |
| Stim8hr knockdown | on-target KD |
| Stim48hr DE genes | 202 |
| Stim48hr knockdown | no on-target KD |
| K562 DE genes | 1 |
| RPE1 DE genes | not measured |
| CollecTRI targets | 0 |
| Current PGGT1B graph edges | 0 |

## Condition-level summary

| condition | target cells | up genes | down genes | total DE | effect | on-target |
|---|---:|---:|---:|---:|---:|---|
| Rest | 81 | 145 | 30 | 175 | -3.887 | on-target KD |
| Stim8hr | 102 | 2,172 | 842 | 3,014 | -4.218 | on-target KD |
| Stim48hr | 49 | 171 | 31 | 202 | -2.088 | no on-target KD |

## Evidence capsule

Decision: `advance_to_orthogonal_assay`. Trust boundary: `proposal_only`.

| measure | value |
|---|---:|
| strongest condition | Stim8hr |
| stimulated to Rest ratio | 17.22x |
| stimulated to K562 ratio | 3014.0x |
| Stim8hr up fraction | 0.721 |
| Stim8hr down fraction | 0.279 |

Evidence ladder:

- `computationally_reproduced`: stimulated CD4+ footprint, 3014 DE genes at Stim8hr with on-target PGGT1B knockdown.
- `computationally_reproduced`: stimulation gate, Stim8hr DE count is 17.22x the Rest DE count.
- `computationally_reproduced`: non-immune transfer check, K562 has 1 DE gene for PGGT1B in the reduced Replogle table.
- `evidence_attached`: prenylation-linked mechanism, external mouse T-cell literature motivates RHOA or RAC pathway readouts.

Assay gates:

- orthogonal knockdown reproduces the Stim8hr transcriptional footprint
- matched Rest culture stays much smaller than stimulated culture
- non-immune transfer check remains small before acceptance work
- RHOA or RAC pathway readout moves in the expected direction

Missing for acceptance:

- target-level summary is not a transcript identity list; acceptance would need the matrix-derived moved-transcript slice
- orthogonal perturbation has not been run
- human review has not signed any new accepted state from this hypothesis

## Hypothesis

PGGT1B (geranylgeranyltransferase-I beta subunit) is a stimulation-gated, cell-type-specific regulator of the CD4+ T-cell activation transcriptome, likely acting upstream via prenylation-dependent signaling rather than as a transcription factor.

## Literature context

- 2019, Gastroenterology, DOI [10.1053/j.gastro.2019.07.007](https://www.sciencedirect.com/science/article/pii/S0016508519410871): mouse CD4+ T-cell PGGT1B links prenylation, RHOA function, alpha4beta7 expression, and intestinal inflammation.
- 2020, Cell Metabolism, DOI [10.1016/j.cmet.2020.10.022](https://www.cell.com/cell-metabolism/fulltext/S1550-4131(20)30591-X): mouse Treg work places Pggt1b upstream of TCR-dependent transcriptional programming and Rac-mediated signaling.

## Assay decision plan

- Sample: primary human CD4+ T cells.
- Intervention: CRISPRi knockdown plus an orthogonal knockdown or small-molecule prenylation perturbation.
- Primary readout: activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h.
- Expected pattern: advance only if stimulated PGGT1B perturbation shifts the activation program while Rest and non-immune controls remain comparatively small.
- Negative controls: non-targeting guide, safe-harbor guide, unstimulated matched culture.
- Positive controls: VAV1, LAT, CD3E.

Stop rules:

- failed on-target knockdown in the stimulated condition
- Rest-only transcriptional shift
- broad K562 or RPE1 effect on replication
- canonical effector-only readout without upstream transcriptome movement

## Wet-lab follow-up

repeat CRISPRi or orthogonal knockdown in stimulated primary CD4+ T cells; measure activation markers, targeted RNA-seq at 8h and 48h, and prenylation-linked RHOA or RAC pathway readouts.

## Caveats

- Stim48hr is not scored as on-target because the screen reports no on-target knockdown in that condition.
- The current frontier has no sliced PGGT1B gene-to-gene edge neighborhood, so the packet uses summary-count evidence.
- External papers make the mechanism plausible; they do not move accepted Prospect state.

Rebuild:

```bash
python frontier/pggt1b_deep_dive.py
```
