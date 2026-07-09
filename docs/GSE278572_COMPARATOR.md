# GSE278572 corrective comparator

## Decision

Prospect Finding 3 needs a narrower interpretation for MED12.

The Prospect measurement remains: MED12 moves 2,843 transcripts at Rest and 2,046 at Stim48hr in
the released Marson table. The corrective result is interpretive: high Rest reach is evidence
against activation specificity, but is not sufficient by itself to label a gene housekeeping or
an essentiality artifact.

Status: `evidence_attached`  
Accepted: `false`  
Proposal: `proposal_e33de6bedec7c950`

This is computation over released data, not wet-lab or clinical truth. The signed Prospect frontier
is unchanged.

## What was compared

The GSE278572 reduced tables contain 28 CRISPRi perturbation targets across resting and stimulated
primary human CD4+ Teff and Treg cells. Twenty-four targets occur in the Prospect backbone.
`DNMT1`, `MED11`, `PRDM1`, and `ZNF217` do not.

The matched comparisons are:

- GSE278572 resting Teff against Prospect `Rest`.
- GSE278572 stimulated Teff at 48 hours against Prospect `Stim48hr`.
- Treg contexts as an informative extension.

Across the 24 shared targets, published pseudobulk DE-count rank agreement is moderate at Rest,
Spearman rho 0.456973, and stronger after 48-hour stimulation, rho 0.644507. These correlations
describe cross-study rank agreement. They do not establish biological equivalence.

## Locked-rule result

Six shared genes carry the current high-Rest label. MED12 is the only one that satisfies every
pre-registered qualification criterion.

| Gene | Prospect Rest DE | Prospect Stim48hr DE | Locked result | Exact reason |
| --- | ---: | ---: | --- | --- |
| FOXO1 | 1,328 | 581 | Does not meet rule | Teff effects reverse, but Stimulated is not significant and S9 has no DE rows in either state. |
| MED12 | 2,843 | 2,046 | `needs_qualification` | Both lineages have significant opposite effects and more than 10 DE genes in both states. |
| MED24 | 1,539 | 1,607 | Does not meet rule | Teff is significant and broad in both states, but its activation-score deltas have the same sign. |
| MYB | 1,325 | 1,222 | Does not meet rule | Stimulated effects are not significant and Resting Teff has only 8 DE genes. |
| STAT5B | 1,135 | 1,060 | Does not meet rule | Effects reverse, but Resting is not significant and has only 2 Teff DE genes. |
| USP22 | 1,783 | 1,849 | Does not meet rule | Stimulated effects are not significant and neither lineage has more than 10 DE genes in both states. |

For MED12 specifically:

| Lineage | Rest delta vs control | Stimulated delta vs control | Rest DE | Stimulated DE |
| --- | ---: | ---: | ---: | ---: |
| Teff | +97.132305 | -70.261674 | 28 | 50 |
| Treg | +53.375573 | -72.786510 | 22 | 40 |

All four MED12 adjusted P values are below 0.01. Loss of MED12 shifts resting cells toward a more
activated score and stimulated cells toward a less activated score in both lineages. The source
paper describes MED12 as a context-dependent regulator of rest and activation, consistent with the
frozen table result.

## Corrected interpretation

The proposal is:

> High Rest reach identifies broad, context-spanning regulators and general machinery. It is
> evidence against activation specificity, but is not sufficient by itself to label a gene
> housekeeping or an essentiality artifact. MED12 is the inspected exception.

This result does not relabel all 139 high-Rest genes. GSE278572 covers only six of them. It also does
not change Finding 3 automatically. Any accepted wording change requires human review and a new
signed state transition.

## Source integrity and replay

- Zenodo archive: 57,967,623 bytes, SHA-256
  `dc9e2efb04d24f1a6d4b8db6a8b1d5cd01c935777c3740088be339de5b5062b4`.
- S8: 116 rows.
- S9: 705 rows, all published adjusted P values below 0.05.
- S14: 100,087 unique cells, two donors, four contexts, 65 guides.
- GEO linkage: all 100,087 retained cells matched the frozen 249,799-barcode file.

```bash
python frontier/gse278572_comparator.py --check
python -m pytest tests/test_gse278572_comparator.py -q
```

The machine-readable proposal is `examples/data/gse278572_comparator.json`. It remains
`evidence_attached`, `accepted=false`, with `human_review_required` as the next step.
