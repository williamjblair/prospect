# Perturbation-atlas scout packet

Status: `evidence_attached`.

No accepted state changes. This packet ranks candidate perturbation resources for future replay work and does not ingest a new dataset.

Signed root: `root_a8b0dcdd4024e12f`

## Replay

```bash
./prospect perturbation-scout
```

## Recommendation

Decision: `do_not_ingest_new_large_dataset_before_submission`.

The shipped cross-substrate, donor-condition, and disease-overlay packets already advance the frontier. A rushed large-corpus ingest would add trust-path risk without a stronger judge story.

Next best action: `campaign_challenger_ledger`.

## Counts

- Candidate sources: 5
- Go now: 0
- Scout only: 3
- No-go large ingest: 2
- Public app surface: 0

## Candidate Sources

| Source | Decision | Replay fit | Download size | Reason |
| --- | --- | --- | --- | --- |
| CZI K562 Essential Perturb-seq Benchmark Dataset | `scout_only` | highest | single processed h5ad | single processed h5ad, but overlaps an already shipped Replogle substrate |
| scPerturb | `scout_only` | medium | 25.01 GB | best broad genetic-perturbation catalog, but full archive is too large for immediate trust-path ingestion |
| PerturBase | `scout_only` | medium | about 5 million cells across database | excellent search surface, but not yet a small reproducible replay extract |
| Tahoe-100M | `no_go_large_ingest` | low_for_current_question | 100 million cells | large chemical perturbation atlas, not a direct genetic replay substrate for CD4+ candidates |
| pertpy Replogle 2022 K562 GWPS loader | `no_go_large_ingest` | redundant | AnnData loader | useful loader, but not a new substrate beyond the shipped Replogle K562 replay |

## Future Ingest Rules

- license and terms are clear enough for a committed frozen extract
- download or API path is reproducible without private credentials
- a small table can be frozen with source hashes
- the replay checks a claim not already covered by the shipped Replogle substrates
- status remains computationally_reproduced for frozen local facts and evidence_attached for interpretation

## Source Facts

### CZI K562 Essential Perturb-seq Benchmark Dataset

Source: https://virtualcellmodels.cziscience.com/dataset/k562-essential-perturb-seq

- single processed H5AD file
- K562 CRISPRi essential-gene Perturb-seq
- contains DE gene sets in unstructured AnnData fields
- median greater than 100 cells per perturbation after filtering
- license prohibits some commercial or unauthorized uses

### scPerturb

Source: https://projects.sanderlab.org/scperturb/

- standardized single-cell perturbation datasets
- dataset explorer includes publication links, perturbation type, and perturbation counts
- RNA and protein H5AD archive is 25.01 GB
- the resource includes E-distance tooling for perturbation effect testing

### PerturBase

Source: https://academic.oup.com/nar/article-abstract/53/D1/D1099/7815638

- 122 scPerturbation datasets from 46 public studies
- 115 single-modal and 7 multi-modal datasets
- 24,254 genetic and 230 chemical perturbations
- about 5 million cells
- web modules expose dataset and perturbation views

### Tahoe-100M

Source: https://arcinstitute.org/news/arc-vevo

- 100 million cells
- 60,000 drug-cell interactions
- 50 cancer cell lines
- 1,200 drug perturbations
- open through Arc Virtual Cell Atlas

### pertpy Replogle 2022 K562 GWPS loader

Source: https://pertpy.readthedocs.io/en/stable/api/data/pertpy.data.replogle_2022_k562_gwps.html

- loads Replogle 2022 K562 genome-wide Perturb-seq as AnnData
- CRISPRi K562 day-8 loss-of-function assay
- obtained from scPerturb
- useful tooling path, not a distinct new biological substrate

This is a scout packet, not a replay packet. It attaches source-backed feasibility judgments and changes no accepted biological state.
