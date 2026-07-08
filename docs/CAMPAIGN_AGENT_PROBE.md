# Campaign agent probes

Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from these probes.

Probe: `campaign_probe_77f01058c6dc2cbe`. Campaign: `campaign_07a2bdd5697274c9`. Model: `claude-opus-4-8`. Tool calls: 16.

## Summary

- `aligned`: 2
- `more_aggressive`: 3

## Probe rows

| rank | gene | deterministic decision | agent recommendation | alignment | rationale |
|---:|---|---|---|---|---|
| 1 | PGGT1B | advance_to_assay_design | advance_to_assay_design | aligned | Largest stimulated footprint (3014 DE at Stim8hr) with on-target KD at its strongest condition and K562-inert cell-type-specific behavior, though it remains proposal-only pending orthogonal reproduction. |
| 2 | RCC1L | hold_as_ranked_backup | advance_to_assay_design | more_aggressive | Robust on-target Stim48hr footprint (1167 DE) with a low Rest baseline (58 DE) and K562-inert profile, making it a clean condition-specific candidate. |
| 3 | MCAT | hold_as_ranked_backup | hold_as_ranked_backup | aligned | Its Rest-condition KD is flagged as putative off-target and K562 shows the highest residual signal (20 DE) among the set, warranting caution despite the on-target Stim48hr footprint. |
| 4 | RWDD2B | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target Stim8hr footprint (720 DE) is meaningful but the elevated Rest baseline (190 DE) and near-zero Stim48hr signal (1 DE) make its stimulated specificity less clean than the top pair. |
| 5 | CCDC22 | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | Clean on-target condition-specific Stim48hr footprint (619 DE) with modest Rest (116 DE) and K562-inert behavior, ranking it as a solid but lower-priority advance. |

Rebuild with a live model run:

```bash
python loop/campaign_probe.py --limit 5
```
