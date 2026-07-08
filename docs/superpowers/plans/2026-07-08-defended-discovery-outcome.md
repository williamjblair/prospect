# Defended Discovery Outcome Plan

## Goal

Produce one defended scientific discovery about human CD4+ T-cell activation, or document that every candidate in the frozen ranked list fails the pre-registered bar.

## Discipline

- Keep every claim proposal-only unless the frozen replay path and human key accept it.
- Freeze and content-address every new public dataset before scoring a candidate against it.
- Compare phenotypes before assigning agreement or contradiction.
- Remove a candidate if any pre-registered kill criterion is met.
- State the ceiling on every public surface: computation over released data, not wet-lab or clinical truth.

## Implementation Steps

1. Pre-register the ranked candidate list, the full success bar, dataset slots, comparability rules, kill criteria, and failure policy.
2. Add tests that pin the pre-registration to the existing discovery campaign packet.
3. Generate a content-sealed JSON packet and a concise memo for reviewers.
4. Run the focused pre-registration tests, then the full local gate.
5. Commit the pre-registration milestone locally.
6. In later milestones, freeze each external dataset before scoring any candidate and work down the ranked list until a survivor clears the bar or every candidate fails.

## First Milestone Exit Criteria

- `examples/data/defended_discovery_preregistration.json` exists and is deterministic.
- `docs/DEFENDED_DISCOVERY_PREREGISTRATION.md` names all 18 candidates in rank order.
- The packet defines at least five orthogonal public dataset requirements and at least three independent kill attempts.
- The packet is content-sealed but not accepted state.
- Full gate passes before commit.
