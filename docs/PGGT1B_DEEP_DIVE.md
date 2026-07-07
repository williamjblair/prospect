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

## Hypothesis

PGGT1B (geranylgeranyltransferase-I beta subunit) is a stimulation-gated, cell-type-specific regulator of the CD4+ T-cell activation transcriptome, likely acting upstream via prenylation-dependent signaling rather than as a transcription factor.

## Literature context

- 2019, Gastroenterology, DOI [10.1053/j.gastro.2019.07.007](https://www.sciencedirect.com/science/article/pii/S0016508519410871): mouse CD4+ T-cell PGGT1B links prenylation, RHOA function, alpha4beta7 expression, and intestinal inflammation.
- 2020, Cell Metabolism, DOI [10.1016/j.cmet.2020.10.022](https://www.cell.com/cell-metabolism/fulltext/S1550-4131(20)30591-X): mouse Treg work places Pggt1b upstream of TCR-dependent transcriptional programming and Rac-mediated signaling.

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
