# Why Prospect is built this way

Prospect is a claim-checker on the surface. Underneath it is an argument about what AI is about to
do to science, and what has to exist for that to be an improvement rather than a flood.

## The problem: generation got cheap, adjudication did not

An AI can assert a claim about any gene in a second. On the Marson lab's own CD4+ T-cell screen,
four frontier models assert "major regulator" claims that the released data contradicts 48% of the
time, and 64% of the time on the genes the field targets most. The models are not broken. They are
doing exactly what they are good at: producing plausible biology quickly.

The bottleneck is no longer generation. It is deciding which of that output the field should hold
as knowledge. That decision does not scale by adding more models, because a model's confidence is
not evidence, and a reviewer agent flagging issues is not acceptance.

## The distinction that everything rests on: activity is not state

A model run, a notebook, an agent trace, a figure, a paragraph of interpretation: these are
**activity**. Activity is cheap, plentiful, and mostly ephemeral. It records what happened.

**State** is different. State is the set of accepted, reviewable, replayable changes to what is
known, uncertain, contradicted, or ready to test. Provenance answers "what happened?". State
answers "what should the field now hold, and can it be re-derived and challenged later?".

Most systems being built for AI science preserve activity well and never cross into state. They
keep the trace and call it memory. Prospect is built entirely around the crossing.

## The receipt: the portable bridge

The crossing is an object, not a vibe. A **receipt** records exactly what a piece of activity
proposes to change:

- the claim, and the entities it is about
- the frozen artifacts it stands on, by hash
- the evidence atoms: specific reproduced facts, verbatim from a verifier
- the verifier and the one command that re-derives the result
- the typed status the evidence actually earns
- the replayability class
- the human acceptance signature, if any

A receipt is not a truth object. It is a structured proposal to change state, and it makes the
boundary portable:

```
Activity  <  Receipt  <  Proposal  <  Review  <  Verification  <  Accepted event  <  State
```

No step is silently skipped. Any producer of activity can emit a receipt. The same frozen gate
decides what becomes state. That is the shape of a protocol: the workbench is where you do the
work; the receipt is what crosses the boundary; the gate is separate from both.

## No model in the trust path

The verifier is frozen code checking a frozen released table. The acceptance is a human key. A
model may propose, search, reason, and draft. It never moves accepted state on its own word. This
is not a limitation to be engineered away. It is the property that makes the state worth trusting
at machine speed: the thing that decides is not the thing that hallucinates.

## The typed status ladder, so language never outruns evidence

The failure mode of AI-for-science is laundering weak evidence through strong words. Prospect
refuses it structurally. Status is typed, and never collapses to "verified" or "true":

- `computationally_reproduced`: re-derives bit-for-bit from frozen released inputs (the EXACT lane)
- `evidence_attached`: the supporting facts are reproduced, but the claim itself is a proposal to test
- `contradicted`: the data disagrees
- `refuted`: a stronger claim the data overturns

The agent's PGGT1B hypothesis is `evidence_attached`, not reproduced: every fact it rests on is a
reproduced lookup, and the hypothesis is a proposal a human accepted as worth testing, not an
established result. The four re-derivable findings are `computationally_reproduced`. The
regulator-vs-effector finding is `contradicted`. The words match the evidence exactly.

## Replayability is the strongest currency

The reason `computationally_reproduced` means something is that `prospect verify` re-derives every
object in the frontier from its frozen fields with zero drift. A content id is a pure function of
the source-derived inputs, so a hand-edited or fabricated object fails. This is the property a
session trace can never give you: not "here is what the model did," but "here is a result anyone
can reconstruct from the same frozen inputs and get the same hash."

## Why this is a protocol, not a project

Prospect is one instance, on one dataset, written from scratch for this event. But the pieces are
deliberately general. The receipt does not care whether the activity came from Prospect's agent, a
notebook, or another workbench. The gate does not care who proposed. The typed status ladder and the
replay contract are the same whether the claim is about a T cell or anything else with a frozen
verifier. The point of building it end to end in the messiest domain, biology, is to show the
pattern survives where exact proof does not exist: hold the exact lane where it does, type the
status honestly where it does not, and never let a model be the thing that decides.

Generation is cheap. Replayable, human-accepted state is the scarce thing, and it is the
thing that compounds.
