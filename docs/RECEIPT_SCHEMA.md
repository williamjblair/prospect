# Prospect receipt schema v0

Status: `evidence_attached`. This document specifies the portable receipt shape used by Prospect
producers and adapters.

The boundary is:

`Activity < Receipt < Proposal < Review < Verification < Accepted < State`

A receipt is not accepted state. It is a proposal object that binds a claim to artifacts, evidence
atoms, replay metadata, and the status the evidence earns. Submission through the MCP bridge returns
`accepted=false` and `human_signature_required` unless a human key-custody step accepts a state
transition.

## Required fields

- `schema_version`: fixed at `prospect.receipt.v0`.
- `receipt_id`: content-addressed receipt identifier, prefixed with `rcpt_`.
- `frontier`: the frontier or dataset namespace the receipt targets.
- `claim`: the claim text carried across the boundary.
- `kind`: the claim family, such as finding, hypothesis, external reproduction, or measurement.
- `subject`: genes or entities affected by the claim.
- `producer`: the activity source that produced the claim.
- `submitter_identity`: the producer identity exposed to the receiving frontier.
- `artifacts`: frozen artifact hashes and locators.
- `evidence`: evidence atoms, each with a fact, value, and source.
- `conditions`: assay, dataset, or scope conditions under which the claim is framed.
- `verifier`: the frozen checker or replay code that adjudicates the receipt.
- `verification_requirements`: requirements before a receipt can affect state.
- `replay_metadata`: command, verifier, replayability, and frontier metadata.
- `status`: typed status only, one of `claimed`, `evidence_attached`,
  `computationally_reproduced`, `independently_reanalyzed`, `contradicted`, or `refuted`.
- `replayability`: `exact`, `reanalysis`, `attested`, or `none`.
- `state_diff`: the proposed effect on state. A model can never apply it.
- `accepted`: boolean acceptance marker.

## Lab writeback fields

Lab results use the same receipt shape whether they confirm or refute a proposal. A lab writeback
receipt adds:

- `executed_protocol`: protocol, intervention, sample, conditions, and controls actually run.
- `assay_readout`: assay summary, required measurements, and result payload reference.
- `affected_claims`: receipts or accepted claims that the lab result bears on.
- `reviewer_signature`: human reviewer signature field for the returned receipt.

The return receipt is still `accepted=false` until review and a human state-signing step. A
refuting lab result uses status `contradicted` and enters as a new receipt proposal.

## State diff

`state_diff` must include:

- `accepted`: whether the receipt already has a human acceptance record.
- `model_can_apply`: always `false`.
- `delta_id`: the accepted frontier delta if one exists, otherwise empty.
- `effect`: either existing accepted state or proposal-only no state mutation.

## Acceptance rule

A receipt can be structurally valid and still not accepted. Accepted state requires:

- frozen replay passes
- reviewer accepts a state delta
- human Ed25519 signature

The JSON Schema is [receipt_schema_v0.json](../receipt/receipt_schema_v0.json). The emitter is pinned
to it by `tests/test_receipt_schema_spec.py`.
