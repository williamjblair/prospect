# Campaign gate probe

Status: `evidence_attached`. Trust boundary: proposal only. Gate pressure can add controls or lower priority; it cannot accept state.

Probe: `campaign_gate_probe_a575022da05ec6c3`. Source triage: `campaign_probe_0890c20aed2180b0`. Model: `claude-opus-4-8`. Tool calls: 13.

Allowed recommendations: `gate_sufficient`, `add_control`, `lower_priority`.

## Summary

- `add_control`: 1
- `gate_sufficient`: 2
- `lower_priority`: 1

## Gate rows

| rank | gene | triage decision | gate recommendation | rationale |
|---:|---|---|---|---|
| 2 | RCC1L | secondary_assay_queue | gate_sufficient | On-target KD in all conditions with a 1167-DE Stim48hr footprint, low Rest (58 DE), and K562-inert cell-type-specificity, all covered by the matched Rest/Stim8hr/Stim48hr RNA-seq gate. |
| 3 | MCAT | capacity_assay_queue | add_control | check_regulator reports a 'putative off-target' KD flag in the Rest condition that the generic gate does not specifically resolve, so an off-target control is warranted. |
| 4 | RWDD2B | capacity_assay_queue | lower_priority | The footprint is transient at Stim8hr (720 DE) but collapses to 1 DE at Stim48hr while carrying the highest Rest DE (190) of the set, weakening its specificity. |
| 5 | CCDC22 | capacity_assay_queue | gate_sufficient | Clean on-target KD across conditions with a 619-DE Stim48hr footprint and K562-inert verdict is adequately covered by the orthogonal-KD plus non-immune transfer-check gate. |

Fixture rebuild:

```bash
python loop/campaign_gate_probe.py --sample
```

Live rebuild:

```bash
python loop/campaign_gate_probe.py
```
