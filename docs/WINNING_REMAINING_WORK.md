# Winning Remaining Work Memo

Audit date: July 8, 2026

Live project: https://prospect-sepia-six.vercel.app

Current git state: use `git log -1 --oneline` as the source of truth. This memo was refreshed after
the receipt bridge client, final-check gate, Gladstone assay handoff, campaign gate probe, and
transfer replay packet shipped. The Frontier tab now also includes the judge-facing "Try the boundary"
receipt bridge strip. The demo recording runbook and submission form packet now package the human
recording and upload path.

Signed root audited: `root_a8b0dcdd4024e12f`

## Bottom line

There are no repo-level blockers left before submission. Prospect is live, replayable, documented,
and aligned with the Build Track story: durable software for a named scientific user, built with
Claude Code, using real life-sciences data, with Claude useful but outside the trust path.

The remaining work is not about making the project viable. It is about increasing the chance it wins.
The highest-leverage remaining work is mostly packaging and judge persuasion:

1. Record the demo video from `docs/DEMO.md`.
2. Submit the live URL, GitHub URL, and `docs/SUBMISSION.md` text.
3. Treat a full second signed frontier as an ambitious stretch only. It is valuable, but it is the easiest place
   to dilute the story or create deadline risk.

## Event frame

The public event materials define the relevant bar:

- The event window is July 7-13, 2026.
- The Build Track is about shipping practical software that outlasts the week for a real scientist,
  clinician, bioinformatician, or biotech user.
- The event emphasizes Claude Science, Claude Code, real Gladstone datasets, and a concrete output
  rather than a throwaway demo.
- The judging audience includes Gladstone, so domain credibility matters more than spectacle.

Prospect is well matched to that frame. It names a real user: a skeptical immunologist or
computational biologist reading the Marson lab screen. It ships a working app, replayable CLI,
receipts, MCP bridge, live data endpoints, a wet-lab packet, and a demo script. It also has a sharp
"Built with Claude" story: Claude proposes and pressure-tests, but frozen code and a human key decide
state.

## Evidence that the current project is submission-ready

This audit used the current worktree and live production data as the source of record.

### Repo and deployment state

- `master` and `origin/master` are checked by `git branch -vv` and `git ls-remote --heads origin master`.
- `.env` exists locally and contains `ANTHROPIC_API_KEY`, without printing the key.
- Production alias is `https://prospect-sepia-six.vercel.app`.
- Live public endpoints return current data:
  - `/data/judge_packet.json`: root `root_a8b0dcdd4024e12f`, 8 campaign probe rows, 4 campaign triage rows, 4 campaign gate probe rows.
  - `/data/campaign_agent_probe.json`: 8 rows, 3 aligned, 4 more-aggressive, 1 more-cautious.
  - `/data/campaign_gate_probe.json`: 4 rows, 2 gate-sufficient, 1 add-control, 1 lower-priority.
  - `/data/transfer_replay_packet.json`: 377 compared T-cell regulators, no accepted-state mutation.
  - `/data/pggt1b_matrix_slice.json`: 671 moved transcripts, top increased `KLF2`, top decreased `IL5`.
  - `./prospect submit-smoke`: executable production smoke for the upload checklist.

### Gate state

Commands run during this audit:

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
```

Observed results:

- `./prospect verify`: 53,485 objects, 0 drift, root `root_a8b0dcdd4024e12f`.
- `python benchmark/mutation_pack.py`: 0 false admissions, 10 of 10 clean regulator claims admitted.
- `python tests/test_skill_parity.py`: 112 claims checked, 0 mismatches.

Recent full-gate evidence from the preceding deployment pass:

- Full `tests/test_*.py` sweep passed.
- `cd web && npm run build` passed.
- Browser QA passed on local port 8124 and production alias.
- Repo scans passed for no em dashes, no attribution footers, no forbidden prior-work references,
  no retired CSS vocabulary, and no changed-file secret values.

### Current artifact surface

Public bundle counts in `web/public/data/frontier.json` and live judge packet:

- 11,526 genes mapped.
- 37,106 regulatory edges.
- 5 signed findings.
- 6 receipts.
- 20 campaign candidates.
- 20 campaign review rows.
- 8 campaign probe rows.
- 4 disagreement triage rows.
- 4 campaign gate probe rows.
- 377 transfer replay rows.
- 5 validation candidates.
- 5 wet-lab assay packet candidates.
- 5 PGGT1B evidence ladder steps.
- 671 PGGT1B matrix-slice transcripts.

### Current narrative surface

The core story is present and coherent across `README.md`, `docs/PROTOCOL.md`, `docs/FINDINGS.md`,
`docs/DEMO.md`, `docs/SUBMISSION.md`, and `docs/JUDGE_PACKET.md`:

- Generation got cheap; adjudication did not.
- Activity is not state.
- Receipt is the portable boundary object.
- No model is in the trust path.
- Status language is typed: `computationally_reproduced`, `evidence_attached`, `contradicted`.
- The Marson screen catches model overclaiming: 48% core contradicted, 64% on famous target genes.
- Prospect recovers known biology before making surprising claims.
- PGGT1B remains a hypothesis to test, not an accepted biological result.
- The lab packet and campaign triage convert model pressure into assay gates, not accepted state.

## Remaining work by priority

### P0, required before submission

These are not repo blockers. They are human/process tasks.

1. **Record the demo video.**
   - Use `docs/DEMO.md` and `docs/DEMO_RECORDING_RUNBOOK.md`.
   - Keep the first 20 seconds on the refusal and overclaiming number.
   - Do not open on the graph.
   - End on the receipt boundary plus PGGT1B lab-facing packet.
   - Risk if skipped: judges may not discover the story in the right order.

2. **Submit the project.**
   - Use live URL: `https://prospect-sepia-six.vercel.app`.
   - Use repo URL: `https://github.com/williamjblair/prospect`.
   - Use `docs/SUBMISSION_FORM_PACKET.md` for copy-paste fields.
   - Include the replay gate commands from `docs/JUDGE_PACKET.md`.

3. **Do a final submitter-side smoke right before upload.**
   - Open production alias.
   - Click Overview, Findings, Frontier, Agent.
   - Open `/data/judge_packet.json`.
   - Confirm root `root_a8b0dcdd4024e12f`.
   - Run `./prospect verify`.
   - Run `./prospect submit-smoke`.

### P1, highest leverage if there is still build time

These could improve the chance of winning without changing the core scientific state.

1. **Add a tiny external MCP receipt-client demo.**
   - Current state: shipped as `python examples/receipt_bridge_client.py`.
   - Why it matters: Prospect claims to be a protocol, not only an app. The MCP bridge exists and is
     tested, but a judge-facing demo client would make that executable boundary obvious in one command.
   - Shape:
     - `examples/receipt_bridge_client.py` or `docs/RECEIPT_BRIDGE_WALKTHROUGH.md`.
     - Starts `./prospect mcp`.
     - Calls schema, validate, submit.
     - Shows submit returns `accepted: false`.
     - Never touches accepted state.
   - Gate:
     - Add a test that runs the demo against the local server or checks the walkthrough commands.
     - Keep public docs and web links current.
   - Risk:
     - Low. The server already exists and tests pass.
   - Recommendation:
     - Do this before attempting a second frontier.

2. **Add a final-check command.**
   - Current state: shipped as `./prospect final-check`.
   - Why it matters: judges can see one command that reproduces the trust floor.
   - Shape:
     - `./prospect final-check` runs `verify`, mutation pack, Skill parity, Python tests, web build,
       em dash scan, forbidden-reference scan.
     - It prints a compact report, not a wall of logs.
   - Gate:
     - Test the CLI dispatch.
     - Keep runtime reasonable.
   - Risk:
     - Medium. A wrapper can become brittle if it assumes local Node or network state. Keep it local
       and explicit.
   - Recommendation:
     - Useful if the demo needs a single terminal moment.

3. **Add a transfer replay packet.**
   - Current state: shipped as `./prospect transfer-replay`, [TRANSFER_REPLAY_PACKET.md](TRANSFER_REPLAY_PACKET.md), and `/data/transfer_replay_packet.json`.
   - Why it matters: it proves the same checker interface replays across Marson CD4+ T cells and Replogle K562/RPE1 without creating a new accepted-state mutation.
   - Shape:
     - Compact JSON and Markdown packet.
     - Status: `computationally_reproduced`.
     - Trust boundary: frozen checkers over frozen tables.
     - Counts: 377 T-cell regulators compared, 70 of 129 essentiality-artifact genes reproduced in K562, 199 of 248 activation-or-effector genes cell-type-specific.
   - Gate:
     - `python tests/test_transfer_replay_packet.py`.
     - Included in `./prospect final-check`.
   - Risk:
     - Low. It summarizes the already signed transfer finding and does not alter the root.
   - Recommendation:
     - Show it in the final demo only if there is time after the receipt bridge and lab handoff.

4. **Add a judge-facing receipt bridge card or walkthrough link in the UI.**
   - Current state: shipped in the Frontier tab as "Try the boundary."
   - Why it matters: the current Frontier tab links bridge artifacts, but the proof that a submitted
     receipt stays proposal-only may be more legible as a short UI beat.
   - Shape:
     - Add one compact section in Frontier: "Try the boundary."
     - Show the three MCP tools and the key invariant: `submit` returns `accepted: false`.
     - Link to the walkthrough or public contract.
   - Gate:
     - Static UI contract test passed.
     - Browser smoke passed on local port 8124 with system Chrome.
   - Risk:
     - Low to medium. Avoid adding cards inside cards or explanatory clutter.

5. **Run an agent pass against disagreement gates.**
   - Current state: shipped as `./prospect campaign-gate-probe`.
   - Why it matters: the campaign probe currently asks Claude to inspect top campaign candidates.
     A second pass could ask whether the deterministic assay gates are sufficient, too strict, or
     missing a control, without moving state.
   - Shape:
     - New artifact: `campaign_gate_probe.json`.
     - Input: rows from `campaign_triage.json`.
     - Output status: `evidence_attached`.
     - Trust boundary: `proposal_only`.
     - Allowed recommendations should be a closed enum, for example `gate_sufficient`,
       `add_control`, `lower_priority`.
   - Gate:
     - Test fixture mode without API.
     - Live run only if `.env` has `ANTHROPIC_API_KEY`.
     - Regenerate web data and judge packet.
   - Risk:
     - Medium. It adds another model artifact, so the copy must stay disciplined.
   - Recommendation:
     - Good if the project needs a stronger "Claude as scientific co-worker" signal.

6. **Add a Gladstone assay handoff one-pager.**
   - Current state: shipped as `docs/GLADSTONE_ASSAY_HANDOFF.md`.
   - Why it matters: the lab packet is already strong, but a single page named for a wet-lab handoff
     would make the practical value easier to judge.
   - Shape:
     - `docs/GLADSTONE_ASSAY_HANDOFF.md`.
     - Top five rows, controls, readouts, stop rules, replay links, missing evidence before acceptance.
     - No new claims, no stronger status.
   - Gate:
     - Add a readiness test that the file contains all five genes and required public endpoints.
   - Risk:
     - Low.
   - Recommendation:
     - Good if the final video has time to show "what a lab can do Monday."

### P2, high ceiling but higher risk

1. **Full second signed frontier on another dataset.**
   - Why it matters: it would prove Prospect generalizes beyond the Marson CD4+ screen.
   - Current safer substitute:
     - Shipped: `./prospect transfer-replay` as a compact, no-state-mutation replay packet over Replogle K562/RPE1.
   - Best conservative target:
     - Replogle K562/RPE1 is already partially integrated through the checker interface.
     - A small second-frontier demo could focus on replaying major-regulator claims in non-immune
       cells, not on building a full parallel product surface.
   - Required shape:
     - Same typed status discipline.
     - Same no-model trust path.
     - Separate signed root or clearly separate replay artifact.
     - No weakening of the Marson story.
   - Risk:
     - High. It can dilute the winning narrative, increase build time, and create new gate burden.
   - Recommendation:
     - Do only if the submission video and protocol bridge packaging are already finished.

2. **Probe all 20 campaign rows.**
   - Why it matters: a broader Claude campaign pass would look more complete.
   - Risk:
     - Medium. The current top-eight pass already covers the strongest rows and produces useful
       disagreement. A top-20 pass may add cost, noise, and weaker candidates.
   - Recommendation:
     - Do not make this a priority unless the agent pass is used to test assay gates, not just create
       more rows.

3. **Attach deeper literature context for every campaign candidate.**
   - Why it matters: it could help wet-lab judges assess novelty.
   - Risk:
     - High. It invites literature hallucination or uneven citation quality unless every source is
       checked carefully.
   - Recommendation:
     - Avoid unless there is time for source-by-source review.

4. **Produce a PDF or slide deck.**
   - Why it matters: judges may appreciate a self-contained artifact.
   - Risk:
     - Medium. The web app and docs already carry the story. A deck can become redundant.
   - Recommendation:
     - Only useful after the demo recording is done.

### P3, do not do before submission

1. **Do not move any campaign, PGGT1B, or assay row into accepted state.**
   - Reason: there is no wet-lab evidence. The project wins by refusing to launder weak evidence.

2. **Do not use a model to alter signed frontier state.**
   - Reason: this breaks the core trust property.

3. **Do not add clinical or therapeutic claims.**
   - Reason: the released screen can support perturbation evidence, not clinical action.

4. **Do not redesign the app.**
   - Reason: the Observatory system is already coherent and tested. A broad redesign creates more
     risk than value.

5. **Do not add prior-project branding or imports.**
   - Reason: New Work Only and standalone are non-negotiable.

6. **Do not chase a full wet-lab result.**
   - Reason: the correct state is a wet-lab-ready hypothesis with assay gates. Anything stronger would
     overclaim.

## Requirement-by-requirement audit

| Requirement | Current status | Evidence | Remaining work |
|---|---|---|---|
| New Work Only and standalone | Satisfied in repo audit | No forbidden prior-work references in tracked scan; AGENTS rules preserved | None |
| No model in trust path | Satisfied | `docs/PROTOCOL.md`, receipt bridge, judge packet, tests, live artifacts | None |
| Typed status language | Satisfied | Copy discipline tests; docs use typed statuses for findings, hypotheses, contradictions | None |
| Replayable signed root | Satisfied | `./prospect verify` reports 53,485 objects, 0 drift, root `root_a8b0dcdd4024e12f` | None |
| Mutation floor | Satisfied | `python benchmark/mutation_pack.py`, 0 false admissions | None |
| Skill parity | Satisfied | `python tests/test_skill_parity.py`, 112 claims, 0 mismatches | None |
| Buildable web app | Satisfied by recent gate | `cd web && npm run build` passed in final deployment pass | None |
| Live production | Satisfied | Stable alias returns current public JSON and Agent content; `./prospect submit-smoke` checks the final upload endpoints | None |
| Built with Claude story | Satisfied | Benchmark, propose loop, autonomous agent, campaign probe, docs | Optional gate-probe pass |
| Gladstone/domain credibility | Strong | Marson screen facts, PubMed citations, PGGT1B matrix slice, wet-lab packet | Optional assay handoff one-pager |
| Protocol claim | Strong | Receipts, MCP bridge, public contract, tests | Optional external client demo |
| Submission packaging | Mostly human task | `docs/SUBMISSION_FORM_PACKET.md`, `docs/SUBMISSION.md`, `docs/DEMO.md`, `docs/DEMO_RECORDING_RUNBOOK.md`, `docs/FINAL_SUBMISSION_CHECKLIST.md`, live site | Record and submit |

## Recommended next sequence

If work continues, do it in this order:

1. **Human submitter work:** record the two-minute demo from `docs/DEMO_RECORDING_RUNBOOK.md` and submit. This is the only P0 work.
2. **Final checklist:** use `docs/FINAL_SUBMISSION_CHECKLIST.md`.
3. **Second frontier:** only if the above are done and there is enough time to keep the current story
   clean.

## Definition of done for the next build slice

Any remaining build slice should pass all of the following before deployment:

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
for t in tests/test_*.py; do python "$t" || exit 1; done
cd web && npm run build
git diff --check
python tests/test_repo_hygiene.py
```

Browser QA should use port 8124, not 3000.

Production deploy remains:

```bash
cd web && vercel --prod --yes --scope constellate-dc388081
```

## Final assessment

Prospect is already submission-ready and credible. The most important remaining work is not more
biology. It is making the protocol boundary obvious enough that a judge understands it in one pass:
Claude does useful scientific work, the receipt carries that work across a boundary, frozen code
decides what replays, and a human key accepts state. The current project proves that on Gladstone's
own screen. The optional work should sharpen that proof, not expand the scope for its own sake.
