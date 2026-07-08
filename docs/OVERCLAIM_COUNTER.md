# Overclaim counter

Status: `evidence_attached`. Trust boundary: proposal only. The counter measures refusals, not accepted state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

The benchmark caught 46 of 96 checkable model major-regulator claims as `contradicted`.

The discovery ladder kept 18 of 11,526 Phase 1 genes; 14 of 18 then lacked an independent screen-hit rung.

PGGT1B advanced because it survived the novelty filter, gained Shifrut 2018 support, retained the Schmidt 2022 contradiction honestly, and anchored the highest-scoring module.

## Rungs

| rung | status | count | source |
|---|---|---:|---|
| frozen_marson_checker | contradicted | 46 | examples/data/phantom_summary.json |
| mutation_floor | refuted | 0 | python benchmark/mutation_pack.py |
| novelty_filter | evidence_attached | 11508 | examples/data/discovery_campaign.json |
| external_screen_ladder | contradicted | 14 | examples/data/cross_validation.json |
| module_selection | evidence_attached | 2 | examples/data/flagship_module.json |

Rebuild:

```bash
./prospect overclaim-counter
```
