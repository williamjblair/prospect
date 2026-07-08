# Campaign agent probes

Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from these probes.

Probe: `campaign_probe_0c252cc895887e61`. Campaign: `campaign_07a2bdd5697274c9`. Model: `claude-opus-4-8`. Tool calls: 80.
Coverage: 20 returned / 20 requested. Complete: yes.

## Summary

- `aligned`: 6
- `more_aggressive`: 11
- `more_cautious`: 3

## Probe rows

| rank | gene | deterministic decision | agent recommendation | alignment | rationale |
|---:|---|---|---|---|---|
| 1 | PGGT1B | advance_to_assay_design | advance_to_assay_design | aligned | Rank-1 condition-specific regulator with a 3014-gene Stim8hr footprint under on-target KD and near-inert K562 behavior (1 DE, cell-type-specific). |
| 2 | RCC1L | hold_as_ranked_backup | advance_to_assay_design | more_aggressive | On-target KD drives 1167 DE at Stim48hr against only 58 at Rest and 5 in K562, a clean cell-type-specific stimulated footprint. |
| 3 | MCAT | hold_as_ranked_backup | hold_as_ranked_backup | aligned | Despite 780 on-target Stim48hr DE, the Rest condition is flagged as putative off-target and it shows the set's highest K562 DE (20), a specificity concern. |
| 4 | RWDD2B | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target KD with 720 Stim8hr DE and inert K562 (1 DE), but the lowest score and relatively high Rest activity (190 DE) make it a lower-priority advance. |
| 5 | CCDC22 | hold_as_ranked_backup | advance_to_assay_design | more_aggressive | Top-scoring candidate (1053, rank 5) with the largest stimulated footprint (619 DE at Stim48hr under on-target KD) that is cell-type-specific (inert in K562), making it the strongest proposal-only lead to advance. |
| 6 | GAS2L1 | advance_if_capacity_allows | advance_if_capacity_allows | aligned | Solid stim-specific footprint (457 DE at Stim48hr on-target KD, only 20 at Rest) but the Stim8hr arm showed no on-target KD, so it is worth advancing contingent on capacity. |
| 7 | SNAP29 | advance_if_capacity_allows | hold_as_ranked_backup | more_cautious | Its footprint is confined to Stim8hr (407 DE) and collapses to 2 DE by Stim48hr, indicating a transient signal that warrants holding as a ranked backup rather than immediate advancement. |
| 8 | CYB5RL | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | Cleanest stim-specific signal (389 DE at Stim48hr on-target KD versus only 11 at Rest, inert in K562) but lowest score/rank (928, rank 8), so advance only if capacity permits. |
| 9 | LETM2 | advance_if_capacity_allows | advance_if_capacity_allows | aligned | Rank-9 with an on-target KD Stim48hr footprint (386 DE), but cross-cell-type is not_tested so its non-immune specificity gap is unresolved. |
| 10 | DAPK2 | advance_if_capacity_allows | hold_as_ranked_backup | more_cautious | Its 350-DE signal is confined to the single Stim48hr on-target condition while Stim8hr/Rest show no on-target KD, and transfer is not_tested, making it the weaker untested candidate. |
| 11 | SCO2 | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | K562-inert cell-type specificity is confirmed and strongest Stim8hr is on-target, but the Stim48hr putative-off-target flag and elevated Rest DE (53) warrant caution before assay design. |
| 12 | CCDC136 | advance_if_capacity_allows | advance_to_assay_design | more_aggressive | On-target KD at the strongest condition (Stim48hr, 263 DE) with low Rest DE and confirmed K562-inert cell-type specificity leaves only the standard orthogonal-reproduction risk. |
| 13 | MITD1 | advance_if_capacity_allows | advance_to_assay_design | more_aggressive | Strongest-condition footprint (Stim48hr, 250 DE) is under confirmed on-target KD with low Rest (11 DE) and K562-inert cell-type-specific behavior. |
| 14 | GZMB | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target Stim8hr signal (496 DE) is strong but the high Rest DE (261) derives from a no-on-target-KD condition and cross-cell transfer is not tested. |
| 15 | FANCL | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target KD footprint reproduces across two stim conditions (329 and 181 DE) with K562-inert specificity, though Rest DE (110) sits under a non-KD condition. |
| 16 | TNNC1 | hold_as_ranked_backup | hold_as_ranked_backup | aligned | Stim8hr is flagged putative off-target and cross-cell is not tested, weakening its lowest-ranked (score 706) stimulated on-target signal. |
| 17 | BCKDHA | hold_as_ranked_backup | advance_to_assay_design | more_aggressive | On-target KD drives a 374-DE Stim8hr footprint that is inert in K562 (1 DE, cell-type-specific), and its 291-DE Rest signal has no on-target KD so the activation-specific case holds. |
| 18 | ZC3H12A | hold_as_ranked_backup | advance_if_capacity_allows | more_aggressive | On-target KD confirms only a modest stim window (261 vs 181 Rest DE) while the large 796-DE Stim48hr footprint lacks on-target KD, and its flagged risk is needing orthogonal reproduction. |
| 19 | IRF4 | use_as_regulon_anchor | use_as_regulon_anchor | aligned | It is a known CollecTRI TF with 59 targets, the largest on-target stim footprint (567 DE), and the cleanest cross-cell-type profile (0 K562 DE). |
| 20 | RXRB | use_as_regulon_anchor | hold_as_ranked_backup | more_cautious | Lowest score with on-target-KD-confirmed Rest DE (308) nearly matching Stim48hr (422), making it the least activation-specific, and its 15-target regulon is a weaker anchor than IRF4. |

Rebuild with a live model run:

```bash
python loop/campaign_probe.py --limit 20
```

Run a bounded chunked live model pass into temporary files before promotion:

```bash
python loop/campaign_probe.py --limit 20 --chunk-size 4 --out-json /tmp/prospect_campaign_probe.json --out-doc /tmp/prospect_campaign_probe.md
```
