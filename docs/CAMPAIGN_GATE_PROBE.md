# Campaign gate probe

Status: `evidence_attached`. Trust boundary: proposal only. Gate pressure can add controls or lower priority; it cannot accept state.

Probe: `campaign_gate_probe_e37545b3a0703803`. Source triage: `campaign_probe_0c252cc895887e61`. Model: `claude-opus-4-8`. Tool calls: 66.
Coverage: 11 returned / 11 requested. Complete: yes.

Allowed recommendations: `gate_sufficient`, `add_control`, `lower_priority`.

## Summary

- `add_control`: 4
- `gate_sufficient`: 6
- `lower_priority`: 1

## Gate rows

| rank | gene | triage decision | gate recommendation | rationale |
|---:|---|---|---|---|
| 2 | RCC1L | secondary_assay_queue | gate_sufficient | On-target KD gives a clean condition_specific stim48hr footprint (1167 DE vs Rest 58, K562 inert 5) with all artifact flags false, so the orthogonal-KD-plus-matched-RNA-seq gate adequately tests the disagreement. |
| 4 | RWDD2B | capacity_assay_queue | lower_priority | Rest DE is 190 against a Stim8hr peak of 720 (and Stim48hr collapses to 1 DE) on the lowest-ranked row, so its stimulated specificity is the weakest of the set. |
| 5 | CCDC22 | secondary_assay_queue | gate_sufficient | On-target KD yields Stim48hr 619 DE versus Rest 116 with K562 inert (13) and no artifact flags, so the specified orthogonal-KD-plus-RNA-seq gate is adequate as written. |
| 8 | CYB5RL | capacity_assay_queue | gate_sufficient | On-target KD shows the cleanest stim-specific ratio (Stim48hr 389 vs Rest 11, K562 inert) with all flags false, so the orthogonal-KD-plus-non-immune-transfer gate suffices. |
| 11 | SCO2 | capacity_assay_queue | add_control | The Stim48hr signal (200 DE) is tagged putative off-target while only Stim8hr (369) is on-target, so a control arm is needed to disambiguate the off-target condition before spending assay capacity. |
| 12 | CCDC136 | secondary_assay_queue | add_control | On-target KD is confirmed only at Stim48hr (263 DE) while Rest (17 DE) and Stim8hr (38 DE) report no on-target KD, so a cross-condition knockdown control is needed to substantiate the claimed rest-specificity. |
| 13 | MITD1 | secondary_assay_queue | gate_sufficient | On-target KD is confirmed at every measured condition with tight specificity (Rest 11, Stim8hr 1, Stim48hr 250 DE) and K562-inert cell-type specificity, leaving only the standard orthogonal-reproduction step already in the gate. |
| 14 | GZMB | capacity_assay_queue | add_control | On-target KD is confined to Stim8hr with Rest 261 DE arising under a no-on-target-KD condition and cross_cell_type verdict not_tested, so the non-immune transfer control is missing from the gate. |
| 15 | FANCL | capacity_assay_queue | gate_sufficient | On-target KD reproduces across Stim48hr (329 DE) and Stim8hr (181 DE) with cross_cell_type K562 inert/cell-type-specific, satisfying the orthogonal-signal and non-immune transfer elements of the proposal-only assay gate. |
| 17 | BCKDHA | secondary_assay_queue | gate_sufficient | The 374-DE Stim8hr driver has on-target KD and is inert in K562 (1 DE, cell-type-specific), so the attached evidence supports the activation-specific ranked-backup gate as written. |
| 18 | ZC3H12A | capacity_assay_queue | add_control | The headline 796-DE Stim48hr footprint has no on-target KD while only a modest KD-confirmed window remains (261 Stim8hr vs 181 Rest), so an orthogonal knockdown control is needed before spending assay capacity. |

Fixture rebuild:

```bash
python loop/campaign_gate_probe.py --sample
```

Live rebuild:

```bash
python loop/campaign_gate_probe.py
```
