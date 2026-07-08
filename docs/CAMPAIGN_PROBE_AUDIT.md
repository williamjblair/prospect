# Campaign probe audit

Status: `computationally_reproduced`. Trust boundary: frozen audit over proposal-only model pressure.

No accepted state changes.

Source probe: `campaign_probe_0890c20aed2180b0`.
Passed: `yes`. Issues: 0.

## Checks

- `proposal_only_status`
- `complete_coverage`
- `deterministic_review_lane_match`
- `closed_recommendation_enum`
- `rationale_contradicts_frozen_kd`
- `rationale_contradicts_k562_transfer`

## Issues

No audit issues detected in the committed probe artifact.

## Promotion rule

A campaign probe can be promoted only when coverage is complete, recommendations are closed, deterministic review fields match, and rationale audit reports no frozen-fact contradictions.

Run on a temporary expanded probe before promotion:

```bash
python loop/campaign_probe_audit.py --input /tmp/prospect_campaign_probe.json
```
