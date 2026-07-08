# Lab writeback receipt

Status: `evidence_attached`. Trust boundary: proposal only.

A wet-lab result returns to Prospect as a receipt with one shape whether it confirms or refutes.
It never overwrites accepted state. It proposes a state transition and waits for a human key.

## Required return shape

- `executed_protocol`
- `assay_readout`
- `affected_claims`
- `reviewer_signature`
- `state_diff`

## Contradiction as proposal

`never_overwrite`: a later contradiction of an accepted claim is a new `contradicted` receipt.
It cites the affected claim, carries the executed protocol and assay readout, and returns
`accepted=false` with `human_signature_required` until review accepts a new signed state event.

## Template receipts

### confirming

- Typed status: `independently_reanalyzed`
- Accepted: `false`
- State effect: `proposal_only_no_state_mutation`
- Affected claim: `rcpt_9b0c29c407ab05c8`

### refuting

- Typed status: `contradicted`
- Accepted: `false`
- State effect: `proposal_only_no_state_mutation`
- Affected claim: `rcpt_9b0c29c407ab05c8`

Rebuild:

```bash
python -m receipt.writeback
```
