# Final deterministic red team

Status: `computationally_reproduced`

Every inspected scientific object remains proposal-only with `accepted=false`. This audit is
computation over released data, not wet-lab or clinical truth. No model-proposed attack lane ran
because no separate API budget was authorized.

## Adjudicated attacks

| Attack | Target | Evidence and replay | Result | Change |
| --- | --- | --- | --- | --- |
| SRC-01 | GSE271788 source hashes, cardinalities, donors, targets, and batch labels | `python frontier/gse271788_calibration.py --check` | did not land | none |
| SRC-02 | Registered substrate replay command | `python frontier/substrate_coverage.py` | landed | add repo-root import bootstrap and a subprocess regression test |
| STAT-01 | Positive broad-reach result was being read as activation-specific evidence | `python frontier/gse271788_activation_specificity.py --check` | landed | show the failed partial sensitivity beside the broad calibration |
| STAT-02 | Partial-rank implementation could be numerically wrong | independent pandas ranks plus NumPy least squares | did not land | independent partial rho `0.045808`, matching the frozen output |
| PROTO-01 | UTF-8 BOM CSV header could be rejected | `python -m pytest tests/test_acceptance_soak.py -q` | landed | strip BOM from the parsed header and pin the behavior |
| PROTO-02 | Transport, receipt, concurrency, or restart could change identity or create accepted state | `python cli/acceptance_soak.py` | did not land | zero identity mismatches and zero acceptance events at full scale |
| PROTO-03 | Generated substrate-coverage packet could retain obsolete claim-mode semantics | `python frontier/substrate_coverage.py` | landed | regenerate the packet and pin the associative signature at 25 passengers and zero contradicted claims |
| NARR-01 | Public Evidence surface omitted the conclusion-changing sensitivity | compare the two frozen GSE271788 proposals | landed | public copy now separates broad reach from incremental activation specificity |
| NARR-02 | Public copy could contain blocked strong language or an untraceable headline | `./prospect rigor-audit` | did not land after NARR-01 | all traced public claims pass the local audit |

## Frozen statistical decision

The original 79-target analysis remains `evidence_attached` for broad cross-study perturbation
reach: Spearman rho `0.373895`, one-sided permutation P `0.00039996`, with three of three original
kills passing.

The pre-registered activation-specific sensitivity is separate. Across 76 complete cases, partial
rho is `0.045808`, one-sided permutation P is `0.35246475`, and the bootstrap interval is
`[-0.166003, 0.260058]`. Batch direction, general machinery, influential target, and subset
instability fail. Cell-count adjustment passes. The status is `orthogonal_phenotype`: broad reach
replicates, but incremental activation-specific reach is not established.

## Protocol stress result

- 11,526 genes under two claim modes and two evidence modes.
- 46,104 gene-mode-evidence evaluations in 12 batches.
- Direct Python, HTTP, stdio MCP, and Streamable HTTP MCP returned matching identities.
- 100,000 parser and identifier cases produced 81,250 typed outcomes and 18,750 clear failures.
- 10,000 HTTP submissions produced 7,000 typed outcomes and 3,000 clear failures.
- 1,000 concurrent requests preserved duplicate identity.
- 100 process restarts preserved proposal and receipt identity.
- Every one of the 17 Receipt v1 bound fields changed the receipt id when mutated.
- 5,001 genes and 1,000,001 input bytes were rejected with HTTP 413.
- Accepted responses: 0. Acceptance events: 0.
- The replayed 52-gene associative packet contains 25 `associative_only` and zero `contradicted`,
  matching the canonical evaluator.

## Remaining risk

- The model-proposed attack lane was not run because no dollar cap was set.
- The activation-specific analysis is a secondary computational sensitivity over released tables,
  not a new experiment.
- Producer identity in public submissions remains self-declared.
- External-team adoption is still a human outreach dependency and fixtures do not count.
- PGGT1B still lacks a comparable independent stimulated primary-CD4 perturbation with adequate
  replication, so its batch-specificity kill remains uncleared.

## Reproduce

```bash
python frontier/gse271788_calibration.py --check
python frontier/gse271788_activation_specificity.py --check
python frontier/substrate_coverage.py
python cli/acceptance_soak.py --check
./prospect rigor-audit
```
