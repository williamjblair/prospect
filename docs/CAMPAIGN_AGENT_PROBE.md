# Campaign agent probes

Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from these probes.

Probe: `campaign_probe_0890c20aed2180b0`. Campaign: `campaign_07a2bdd5697274c9`. Model: `claude-opus-4-8`. Tool calls: 25.

## Summary

- `aligned`: 3
- `more_aggressive`: 4
- `more_cautious`: 1

## Probe rows

| rank | gene | deterministic decision | agent recommendation | alignment | rationale |
|---:|---|---|---|---|---|
| 1 | PGGT1B | advance_to_assay_design | advance_to_assay_design | aligned | Largest stimulated footprint (3014 DE at Stim8hr) with on-target KD at its strongest condition and K562-inert cell-type-specific verdict. |
| 2 | RCC1L | hold_as_ranked_backup | advance_to_assay_design | more_aggressive | Strong Stim48hr footprint (1167 DE) with on-target KD, low Rest DE (58), and cell-type-specific (K562 inert). |
| 3 | MCAT | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target 780-DE Stim48hr footprint but the Rest condition carries a 'putative off-target' KD flag, warranting capacity gating. |
| 4 | RWDD2B | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target 720-DE Stim8hr footprint and cell-type-specific, but elevated Rest DE (190) makes it a capacity-gated candidate. |
| 5 | CCDC22 | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | Clean on-target 619-DE Stim48hr footprint that is K562-inert but mid-tier in magnitude, fitting capacity-dependent advancement. |
| 6 | GAS2L1 | advance_if_capacity_allows | advance_if_capacity_allows | aligned | On-target 457-DE footprint at its strongest Stim48hr condition with low Rest DE (20), though Stim8hr shows no on-target KD, so gate on capacity. |
| 7 | SNAP29 | advance_if_capacity_allows | hold_as_ranked_backup | more_cautious | Clean on-target 407-DE Stim8hr footprint with low Rest DE (19) but a smaller, less distinctive footprint suited to backup ranking. |
| 8 | CYB5RL | hold_as_ranked_backup | hold_as_ranked_backup | aligned | Smallest stimulated footprint (389 DE) among the eight, on-target and cell-type-specific but lowest-magnitude, best held as a ranked backup. |

Rebuild with a live model run:

```bash
python loop/campaign_probe.py --limit 8
```
