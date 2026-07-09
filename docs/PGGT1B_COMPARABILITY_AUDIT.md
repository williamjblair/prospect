# PGGT1B comparability audit

Status: `evidence_attached`. Accepted: `false`. Next: `human_signature_required`.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

## Determination

No independent public dataset in this audit directly perturbs PGGT1B and measures a matched stimulated activation transcriptome.

The frozen comparators do not clear the batch or dataset specificity kill. They also do not contradict the PGGT1B activation-transcriptome hypothesis because their PGGT1B readouts are nonmatching phenotypes. The two transcriptomic panels omit PGGT1B from their target manifests.

## Coverage audit

| study object | PGGT1B coverage | readout | typed status | determination |
|---|---:|---|---|---|
| shifrut_2018 ORCS 1107 | yes | CFSE-separated proliferation after TCR stimulation | `orthogonal_phenotype` | hit, rank 1095 of 19108 |
| shifrut_2018 ORCS 1109 | yes | CFSE-separated proliferation after TCR stimulation | `orthogonal_phenotype` | non_hit, rank 18667 of 19089 |
| shifrut_2018 GSE119450 | no | single-cell transcriptome | `not_assayed` | PGGT1B absent from 20-gene target manifest |
| schmidt_2022 ORCS 2423 | yes | IL-2 protein accumulation after stimulation | `orthogonal_phenotype` | non_hit, rank 8935 of 18920 |
| schmidt_2022 ORCS 2424 | yes | IFN-gamma protein accumulation after stimulation | `orthogonal_phenotype` | non_hit, rank 18016 of 18900 |
| schmidt_2022 ORCS 2427 | yes | TNF-alpha protein accumulation after stimulation | `orthogonal_phenotype` | non_hit, rank 4529 of 18894 |
| schmidt_2022 GSE190604 | no | single-cell transcriptome | `not_assayed` | PGGT1B absent from 73-gene target manifest |

Shifrut GSE119450 uses 48 guides: 40 guides across 20 genes and 8 non-targeting controls. It profiles stimulated and unstimulated primary human CD8+ T cells from two donors, but PGGT1B is not among the 20 gene targets.

Schmidt GSE190604 contains 73 non-control target labels plus `NO-TARGET` in the public guide-call table. It profiles resting and restimulated primary human T cells using CRISPR activation, but PGGT1B is not among those target labels.

## Source anchors

- [Shifrut et al. 2018](https://pubmed.ncbi.nlm.nih.gov/30449619/): DOI 10.1016/j.cell.2018.10.024, [GEO GSE119450](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE119450).
- [Schmidt et al. 2022](https://pubmed.ncbi.nlm.nih.gov/35113687/): DOI 10.1126/science.abj4008, [GEO GSE190604](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190604).
- PGGT1B screen rows: [BioGRID ORCS gene 5229](https://orcs.thebiogrid.org/Gene/5229) and the frozen Prospect snapshot named in the JSON artifact.
- Exact source URLs, byte sizes, SHA-256 hashes, and extraction rules are frozen in the JSON artifact.

## Stop criteria

Stop the public search and retain `evidence_attached` unless one accession meets every criterion:

- primary human CD4+ T cells.
- direct PGGT1B loss-of-function with guide identity and on-target evidence.
- matched stimulated and resting or unstimulated controls.
- transcriptome-wide RNA readout linked to PGGT1B-perturbed cells.
- at least two donors or independent biological replicates.
- processed matrix, guide assignments, and metadata available without controlled access.
- source files can be content-addressed and replayed deterministically.

Proliferation, cytokine abundance, FOXP3 abundance, or activation-marker abundance alone remains `orthogonal_phenotype`. Sparse target-manifest coverage remains `not_assayed`.

## Rebuild

```bash
python frontier/pggt1b_comparability_audit.py --check
python -m pytest tests/test_pggt1b_comparability_audit.py -q
```
