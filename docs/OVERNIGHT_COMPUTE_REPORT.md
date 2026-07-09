# Overnight compute report

All outputs are proposal-only and accepted=false. No model is in the trust path. A human key accepts no state in this run.

Ceiling: Computation over released data, not wet-lab or clinical truth.

## Three Numbers

- Genome-wide atlas genes typed: 11526
- Literature claims contradicted: 51 of 229
- Defended leaderboard entries clearing the compute bar: 3 of 2734

## Phase 1

`overnight_atlas_10f89bef8887817c` scored 11526 genes. Counts: {'associative_only': 4859, 'evidence_attached': 3054, 'not_assayed': 3613}.

## Phase 2

`overnight_literature_audit_15341eff619f8029` mined 209 Europe PMC records into 229 typed claims. Counts: {'contradicted': 51, 'evidence_attached': 61, 'not_assayed': 28, 'orthogonal_phenotype': 89}.

## Phase 3

`overnight_leaderboard_2a67e8fe8cc9de1d` scored 2734 candidate drivers absent from CollecTRI and standard annotations. Cleared compute bar: 3.

## Public Artifacts

- `/data/overnight_preregistration.json`
- `/data/overnight_genome_wide_atlas.json`
- `/data/overnight_literature_claims.json`
- `/data/overnight_literature_audit.json`
- `/data/overnight_defended_leaderboard.json`

## Reproduce

```bash
./prospect overnight-compute
```
