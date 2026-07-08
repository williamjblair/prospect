# Winning Remaining Work Memo

Audit date: July 8, 2026

Live project: https://prospect-sepia-six.vercel.app

Signed root audited: `root_a8b0dcdd4024e12f`

Current git state: use `git log -1 --oneline` as the source of truth.

## Active goal

Complete all remaining high-ceiling work for Prospect to maximize its chance to win the Built with
Claude: Life Sciences hackathon by July 13, 2026. Preserve the existing submission-ready floor,
then build the strongest defensible extensions: a second-substrate replay surface, a deeper
Claude-campaign pressure loop, a Gladstone-ready assay operations bundle, and final demo/submission
production. Every slice must keep Prospect's trust rules intact and pass the gate before deployment.

Submission-ready is the floor, not the finish line. The project is already live, replayable, and
credible. The remaining work should raise the ceiling without weakening the story.

## Hackathon runway

This memo treats July 8, 2026 as day one of the build window, with work available through the end of
July 13, 2026. The correct posture is not "nothing remains." The correct posture is: the floor is
green, production is live, and the remaining time should be spent only on work that increases the
chance of winning without weakening the trust boundary.

The active goal is therefore not a single feature. It is the whole remaining campaign:

- Keep the signed, replayable floor green at all times.
- Keep the live app and public artifacts aligned with the committed state.
- Increase protocol credibility through replay surfaces and receipt portability.
- Increase the Built with Claude story through bounded model pressure, never model acceptance.
- Increase Gladstone usefulness through assay-ready packets and explicit stop rules.
- End with a recorded demo, submission packet, production smoke, release manifest, and a memo that
  names any human-only actions plainly.

## Non-negotiable rules

- New Work Only and standalone. No prior-project imports, branding, or references.
- No model in the trust path. Claude may propose, search, and pressure-test. Frozen code over frozen
  released tables decides what replays. A human key accepts state.
- Status language stays typed: `computationally_reproduced`, `evidence_attached`, `contradicted`.
- This proves computation over released data, not wet-lab or clinical truth.
- Proposal work stays proposal-only unless a human signing path accepts a replayable state change.
- No accepted-state mutation may come from a model artifact.
- No em dashes, no attribution footers, no secrets in repo or chat.

## Current floor to preserve

Prospect is currently strong enough to submit. Do not lose any of this while building.

- Live app: https://prospect-sepia-six.vercel.app
- Repo: https://github.com/williamjblair/prospect
- Signed root: `root_a8b0dcdd4024e12f`
- `./prospect final-check` passes.
- `./prospect submit-smoke` passes against production.
- `./prospect release-manifest` hashes the public data artifact surface.
- `./prospect rendered-qa` emits the durable browser QA checklist.
- `./prospect verify` re-derives 53,485 objects with 0 drift.
- `python benchmark/mutation_pack.py` admits 0 tampered claims.
- `python tests/test_skill_parity.py` checks 112 claims with 0 mismatches.
- Production exposes all public artifacts listed by `./prospect submit-pack`.
- The live Overview now states what outlasts the week: working software for a skeptical immunologist,
  a replayable CLI, public endpoints, receipt bridge, wet-lab handoff, and human-signed root.

Preserve the floor with every change:

```bash
./prospect final-check
./prospect submit-smoke
./prospect release-manifest
./prospect rendered-qa
./prospect submit-pack
./prospect demo-pack
```

For any web-facing change, also deploy:

```bash
cd web && vercel --prod --yes --scope constellate-dc388081
```

## Winning thesis

Generation got cheap; adjudication did not. Prospect wins if judges understand that it is not just a
nice app on a Gladstone dataset. It is a protocol surface for machine-generated science:

1. An AI produces activity.
2. A receipt carries that activity across a boundary.
3. Frozen verifiers replay the relevant evidence.
4. Human acceptance is explicit.
5. Only then does state change.

The current Marson screen proves the boundary on real CD4+ biology. The remaining ceiling work
should show that the boundary generalizes, that Claude is useful without being trusted, and that
Gladstone could act on the output without accepting weak evidence.

## Workstreams

### P0, protect the existing submission floor

Goal: keep the entry always uploadable while extending it.

Deliverables:

- Keep `docs/FINAL_SUBMISSION_CHECKLIST.md`, `docs/JUDGE_QUICKSTART.md`,
  `docs/SUBMISSION_FORM_PACKET.md`, and `docs/DEMO_TELEPROMPTER.md` current.
- Keep production smoke aligned with the public artifact manifest.
- Keep `./prospect release-manifest` aligned with every public endpoint.
- Keep `./prospect rendered-qa` aligned with the final judge path.
- Keep the live URL stable and redeployed after every web-facing change.
- Keep the root and replay counts honest in every public doc.

Gate:

- `./prospect final-check`
- `./prospect submit-smoke`
- `./prospect release-manifest`
- `./prospect rendered-qa`
- Production rendered QA for web-facing changes.

Risk:

- Low, but any rushed extension can break the upload path. Treat this as the invariant.

### P1, second-substrate replay surface

Goal: prove Prospect is a protocol, not a one-dataset viewer, without building a risky full second
frontier.

Status: shipped as `./prospect substrate-replay`, `examples/data/substrate_replay_packet.json`,
[SUBSTRATE_REPLAY_PACKET.md](SUBSTRATE_REPLAY_PACKET.md), `/data/substrate_replay_packet.json`, the
judge packet, final-check, submit-smoke, and a Findings tab card. It reports 377 replayed T-cell
regulators across Marson CD4+ T cells, Replogle K562, and Replogle RPE1, with no accepted-state
mutation.

Recommended shape:

- Add a compact `./prospect substrate-replay` or stronger `./prospect replogle-replay` command.
- Use the existing Replogle K562/RPE1 checker tables and the Marson checker interface.
- Emit a JSON packet and Markdown memo, for example `examples/data/substrate_replay_packet.json` and
  `docs/SUBSTRATE_REPLAY_PACKET.md`.
- Public status: `computationally_reproduced`.
- Trust boundary: frozen checkers over frozen released tables, no accepted-state mutation.
- Show the same claim interface crossing Marson, Replogle K562, and Replogle RPE1 where data exists.
- Surface the packet in `web/public/data/frontier.json`, the judge packet, and the live app.

What to show:

- Essentiality artifacts transfer to non-immune substrates.
- Activation-module genes stay T-cell-specific.
- Concrete contrast rows such as MED19 versus BCL10.
- Counts of regulators compared, transferred, and substrate-specific.
- Cases where data is missing or not gradeable.

Why it helps win:

- Gladstone judges see the Marson result is not a bespoke demo.
- The protocol claim becomes executable across substrates.
- It raises scientific credibility without changing accepted biological state.

Guardrails:

- Do not call this a full second frontier unless it has its own signed root and complete state model.
- Do not launder transfer replay into wet-lab truth.
- Do not mutate the signed Marson frontier.

Gate:

- New tests for packet schema, typed status, no accepted-state mutation, and public web bundle.
- Add to `./prospect final-check`.
- Add to `./prospect submit-smoke` only after it is public.

### P1, complete the Claude campaign pressure loop

Goal: make the "Built with Claude" story deeper than one agent run while preserving the boundary.

Status: shipped as `./prospect campaign-pressure`,
`examples/data/campaign_pressure_summary.json`, [CAMPAIGN_PRESSURE_SUMMARY.md](CAMPAIGN_PRESSURE_SUMMARY.md),
`/data/campaign_pressure_summary.json`, the judge packet, final-check, submit-smoke, and an Agent tab
card. It accounts for 20 campaign rows, 20 deterministic review rows, 8 Claude probe rows, 4
more-aggressive rows converted to assay gates, gate-probe recommendations, and 0 accepted-state
mutations. The campaign probe now records requested versus returned coverage, so a larger model pass
cannot be mistaken for complete coverage if Claude returns fewer decisions than requested. The probe
runner also supports bounded chunked live passes into temporary files, which is the right path for
all-20 expansion experiments.

Recommended shape:

- Extend the existing campaign probe beyond the top eight rows, or run a second pass focused on all
  disagreement gates.
- Prefer a controlled pass over all 20 campaign candidates only if it returns closed recommendations
  and bounded evidence.
- If a larger pass returns fewer decisions than requested, keep it as a partial pressure artifact or
  rerun it. Do not let it replace the committed eight-row chain unless the coverage and downstream
  triage artifacts are regenerated together.
- If a larger pass returns complete coverage but any rationale contradicts frozen lookup facts, keep
  it out of the public chain or turn the contradiction into explicit review work before promotion.
- Keep outputs proposal-only and deterministic where possible.
- Preserve existing enums such as `gate_sufficient`, `add_control`, and `lower_priority`.
- Add a summary layer that tells judges what Claude changed, what Prospect refused to change, and
  what wet-lab work remains.

What to show:

- Claude aligns with deterministic review on some rows.
- Claude pushes harder on some rows.
- Prospect turns that pressure into assay gates, not accepted state.
- The model is useful because it creates review work, not because it decides truth.

Why it helps win:

- It makes the Claude story visible and mature.
- It proves the system can absorb model pressure without surrendering state.
- It creates a richer leaderboard for the demo and Agent tab.

Guardrails:

- No campaign, PGGT1B, or assay row enters accepted state.
- No row gets stronger than `evidence_attached` without new evidence and human acceptance.
- Use fixture/sample modes in tests so the suite does not require API access.

Gate:

- Tests for output schema, closed recommendations, proposal-only status, web bundle inclusion, and
  live copy.
- Add generated-artifact drift checks to `./prospect final-check`.

### P1, Gladstone-ready assay operations bundle

Goal: make the wet-lab handoff feel immediately usable by a domain expert while staying honest.

Status: shipped as `./prospect assay-ops`, `examples/data/assay_operations_bundle.json`,
`examples/data/assay_operations_bundle.csv`, [ASSAY_OPERATIONS_BUNDLE.md](ASSAY_OPERATIONS_BUNDLE.md),
`/data/assay_operations_bundle.json`, the judge packet, final-check, submit-smoke, and an Agent tab
card. It keeps all five rows `evidence_attached`, names expected positive, weakening, and rejection
evidence, and reports 0 accepted-state mutations.

Recommended shape:

- Expand the existing lab packet and Gladstone handoff into an operations bundle.
- Keep top rows headed by PGGT1B unless new evidence changes ranking.
- For each row, include intervention, controls, readouts, exclusion rules, expected positive result,
  weakening result, rejection result, replay links, and missing evidence before acceptance.
- Add a compact CSV for bench planning and a Markdown memo for human reading.
- Surface the bundle in the Agent tab and judge packet.

What to show:

- A lab can act Monday morning without guessing the controls.
- The packet says exactly what evidence would promote, weaken, or reject each hypothesis.
- The system does not claim wet-lab truth before the wet-lab work exists.

Why it helps win:

- Gladstone is judging. A practical lab handoff matters.
- It turns the abstract trust layer into an operational workflow.
- It makes the domain expert user concrete.

Guardrails:

- Do not add clinical or therapeutic claims.
- Do not chase a full wet-lab result.
- Keep every row proposal-only and `evidence_attached`.

Gate:

- Tests that every row has controls, readouts, stop rules, missing evidence, and replay links.
- Public artifact and web bundle checks.
- Copy tests for no overclaiming.

### P2, submission and demo production

Goal: convert the expanded build into a winning two-minute narrative and a low-friction judge path.

Deliverables:

- Refresh `docs/DEMO.md`, `docs/DEMO_RECORDING_RUNBOOK.md`, and `docs/DEMO_TELEPROMPTER.md` after
  every major new artifact.
- Keep `./prospect demo-pack` aligned with the best two-minute path.
- Keep `./prospect submit-pack` aligned with the final public artifacts.
- Keep `./prospect judge-handout` aligned with the final five-minute judge path.
- Record the demo video.
- Submit the live URL, repo URL, and copy from `docs/SUBMISSION_FORM_PACKET.md`.

Recommended demo arc after P1 work:

1. Open with the A1BG refusal.
2. Show the 48 percent and 64 percent overclaiming numbers.
3. Show signed Marson findings.
4. Show second-substrate replay as protocol generalization.
5. Show Claude campaign pressure becoming assay gates.
6. Close on PGGT1B and the Gladstone assay operations bundle.

Gate:

- `./prospect demo-pack --json`
- `./prospect submit-pack --json`
- `./prospect submit-smoke`
- `./prospect rendered-qa`
- Manual browser pass through Overview, Findings, Frontier, Agent.

### P2, optional polish after the ceiling work

Only do these after the P1 workstreams and demo path are coherent.

- A one-page print handout generated from existing docs. Shipped as `./prospect judge-handout` and
  [JUDGE_HANDOUT.md](JUDGE_HANDOUT.md).
- Public release manifest. Shipped as `./prospect release-manifest` and
  [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md). Hashes prove deployed byte identity, not wet-lab or
  clinical truth.
- Rendered QA packet. Shipped as `./prospect rendered-qa` and
  [RENDERED_QA_PACKET.md](RENDERED_QA_PACKET.md). It preserves the manual browser checklist for
  Overview, Findings, Frontier, and Agent across desktop and mobile viewports.
- A short static "judge packet" landing view if the live Overview becomes too dense.
- A small visual diagram of the receipt boundary, only if it clarifies rather than decorates.

### P3, deliberate non-goals

Do not spend hackathon time here unless the core plan changes.

- Do not build a full second signed frontier unless the substrate-replay surface is already done and
  the story remains clean.
- Do not probe all campaign rows merely to increase counts. More rows are useful only if they produce
  better review work.
- Do not attach broad literature context to every candidate unless each citation is source-checked.
- Do not redesign the app.
- Do not add clinical or therapeutic claims.
- Do not chase a full wet-lab result.
- Do not use a model to alter signed frontier state.

## Requirement-by-requirement audit

| Requirement | Current state | Completion plan |
|---|---|---|
| New Work Only and standalone | Satisfied | Keep repo scans and copy checks in `final-check`. |
| No model in the trust path | Satisfied | Preserve proposal-only campaign and receipt boundaries. |
| Typed status language | Satisfied | Every new artifact must use `computationally_reproduced`, `evidence_attached`, or `contradicted`. |
| Replayable signed root | Satisfied | Do not mutate Marson accepted state for replay or campaign work. |
| Mutation floor | Satisfied | Keep `benchmark/mutation_pack.py` in the gate. |
| Skill parity | Satisfied | Keep `python tests/test_skill_parity.py` in the gate. |
| Live production | Satisfied | Redeploy after web changes and run `./prospect submit-smoke`. |
| Public release manifest | Shipped | Keep `./prospect release-manifest` in final-check and submit-smoke. |
| Rendered QA packet | Shipped | Keep `./prospect rendered-qa` in final-check and the final audit. |
| Protocol generalization | Shipped | Keep substrate replay in final-check, submit-smoke, and the live Findings tab. |
| Built with Claude story | Shipped stronger | Keep campaign pressure summary in the Agent tab and demo script. |
| Gladstone usefulness | Shipped stronger | Keep the assay operations bundle in the Agent tab, judge packet, final-check, and submit-smoke. |
| Submission packaging | Shipped, human upload remains | Keep `./prospect submission-audit`, demo, and submit packets aligned after any final polish. |

## Execution order

1. Protect the floor: run the full gate before starting and after every slice.
2. Build second-substrate replay surface. Shipped.
3. Build or extend Claude campaign pressure loop. Shipped as the pressure summary.
4. Build Gladstone assay operations bundle. Shipped.
5. Refresh demo and submission surfaces. Shipped with `./prospect submission-audit`.
6. Keep the public release manifest current. Shipped.
7. Keep the rendered QA packet current. Shipped.
8. Record and submit.

## Definition of done for the full active goal

The active goal is complete only when:

- P0 floor remains green.
- Second-substrate replay surface is shipped or explicitly rejected with evidence.
- Claude campaign pressure loop is shipped or explicitly bounded with evidence.
- Gladstone assay operations bundle is shipped or explicitly bounded with evidence.
- Demo and submission packets reflect the final artifact surface.
- Production is deployed and smoke-tested.
- `./prospect final-check` passes.
- `./prospect submit-smoke` passes.
- `./prospect release-manifest` is current.
- `./prospect rendered-qa` is current.
- The final memo states any remaining human-only actions plainly.
- `./prospect submission-audit` names shipped workstreams, required gates, public artifacts, and
  human-only actions.

## Final judgment

Do not stop at submission-ready. Use the remaining hackathon window to raise the ceiling in ways
that strengthen the same thesis: Claude makes activity cheap, Prospect decides what becomes
replayable state. The remaining work is final production: keep the gate green, record the demo from
the current teleprompter, submit the live URL and repo, and state plainly that wet-lab execution is a
human next step outside this repo.
