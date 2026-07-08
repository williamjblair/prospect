# Campaign gate probe

Status: `evidence_attached`. Trust boundary: proposal only. Gate pressure can add controls or lower priority; it cannot accept state.

Probe: `campaign_gate_probe_d3b3bd75a27d54e7`. Source triage: `campaign_probe_0c252cc895887e61`. Model: `claude-opus-4-8`. Tool calls: 48.
Coverage: 5 returned / 11 requested. Complete: no.

Allowed recommendations: `gate_sufficient`, `add_control`, `lower_priority`.

## Summary

- `add_control`: 1
- `gate_sufficient`: 3
- `lower_priority`: 1

## Gate rows

| rank | gene | triage decision | gate recommendation | rationale |
|---:|---|---|---|---|
| 2 | RCC1L | secondary_assay_queue | gate_sufficient | On-target KD gives a clean condition_specific stim48hr footprint (1167 DE vs Rest 58, K562 inert 5) with all artifact flags false, so the orthogonal-KD-plus-matched-RNA-seq gate adequately tests the disagreement. |
| 4 | RWDD2B | capacity_assay_queue | lower_priority | Rest DE is 190 against a Stim8hr peak of 720 (and Stim48hr collapses to 1 DE) on the lowest-ranked row, so its stimulated specificity is the weakest of the set. |
| 5 | CCDC22 | secondary_assay_queue | gate_sufficient | On-target KD yields Stim48hr 619 DE versus Rest 116 with K562 inert (13) and no artifact flags, so the specified orthogonal-KD-plus-RNA-seq gate is adequate as written. |
| 8 | CYB5RL | capacity_assay_queue | gate_sufficient | On-target KD shows the cleanest stim-specific ratio (Stim48hr 389 vs Rest 11, K562 inert) with all flags false, so the orthogonal-KD-plus-non-immune-transfer gate suffices. |
| 11 | SCO2 | capacity_assay_queue | add_control | The Stim48hr signal (200 DE) is tagged putative off-target while only Stim8hr (369) is on-target, so a control arm is needed to disambiguate the off-target condition before spending assay capacity. |

Fixture rebuild:

```bash
python loop/campaign_gate_probe.py --sample
```

Live rebuild:

```bash
python loop/campaign_gate_probe.py
```
