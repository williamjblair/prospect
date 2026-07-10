# Acceptance service soak

Accepted: `false`
Next: `human_signature_required`
Signed root: `root_a8b0dcdd4024e12f`

## Result

The canonical evaluator completed a local, unpublished soak with zero transport identity mismatches,
zero silent wrong answers, zero accepted responses, and zero acceptance events. Computation over released data, not wet-lab or clinical truth.

| Lane | Scale | Result | Elapsed seconds |
| --- | ---: | --- | ---: |
| Full-genome transport parity | 46104 gene-mode-evidence evaluations in 12 batches | 0 identity mismatches across 4 transports | 63.976 |
| Parser and identifier fuzz | 100000 cases | 81250 typed, 18750 clear failures, 0 unexpected exceptions | 32.052 |
| HTTP fuzz | 10000 submissions | 7000 typed, 3000 clear failures | 15.753 |
| Concurrency | 1000 requests | duplicate ids stable, 500 unique proposal ids | 1.575 |
| Restart persistence | 100 forced restarts | 100 proposal fetches, 0 identity mismatches | 128.258 |
| Receipt v1 mutation | 17 bound-field mutations | every mutation changed the receipt id | n/a |
| Service limits | 2 over-limit probes | 5,001 genes and 1,000,001 bytes both rejected clearly | n/a |

## Genome coverage

- Frozen Marson genes: 11526.
- Claim modes: `associative_signature`, `explicit_driver_claim`.
- Evidence modes: `primary_only`, `all_frozen`.
- Transports: direct Python, HTTP, stdio MCP, Streamable HTTP MCP.
- Associative signatures produced zero `contradicted` verdicts.
- Every transport returned the same proposal and receipt identity for each deterministic batch.
- A 5000-gene batch was accepted for typing; 5,001 genes and an over-byte request were rejected with HTTP 413.

## Persistence boundary

The local SQLite store contains 1519 immutable proposals and
8024 append-only submission events from this soak. None were
published to the ledger. The acceptance-event table contains 0
rows.

## Replay

The full soak uses temporary local service state under `var/acceptance_soak/`. It does not send the
corpus to the production service.

```bash
python cli/acceptance_soak.py
python -m pytest tests/test_acceptance_soak.py -q
```
