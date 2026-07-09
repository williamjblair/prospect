# Exhaustive literature audit

ID: `exhaustive_literature_audit_0f320bf477801bdf`

Status: `evidence_attached`. accepted=false. next=human_signature_required.

Ceiling: Computation over released data, not wet-lab or clinical truth.

## Headline Number

At the configured Day 1 stop, Prospect mined 10000 Europe PMC records into 5975 typed CD4+ regulatory claims. 1547 were typed `contradicted`, a rate of 25.89%.

This is computation over released data. It is not wet-lab or clinical truth.

## Typed Counts

- `contradicted`: 1547
- `evidence_attached`: 1787
- `orthogonal_phenotype`: 1856
- `not_assayed`: 785

## Scale Assessment

hit configured 10,000-record stop on the first Europe PMC query cursor; this is a real-scale audit, not the full possible Europe PMC corpus

## Public Artifacts

- `/data/exhaustive_literature_audit.json`
- `/data/exhaustive_literature_claims.jsonl`
- `/data/exhaustive_literature_claims.csv`
- `/data/exhaustive_literature_documents.jsonl`

## Reproduce

```bash
./prospect exhaustive-compute --phase literature --max-records 10000 --checkpoint-every 250 --rate-limit-seconds 0.35
./prospect exhaustive-compute --phase freeze-literature
```
