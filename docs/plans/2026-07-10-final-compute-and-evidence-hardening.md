# Prospect Final Compute and Evidence Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Determine whether Prospect's 79-target cross-study result contains activation-specific
signal beyond general perturbation breadth, exhaustively attack the acceptance service, and freeze a
submission whose public claims survive those attacks.

**Architecture:** Add one pre-registered sensitivity analysis beside the existing GSE271788
calibration without changing the original result. Run all service stress work against temporary local
stores through the canonical evaluator and existing transports. Models may propose attacks, but only
frozen tests and replayable code may change a typed result or public claim.

**Tech Stack:** Python 3.12, standard-library statistics plus pandas where needed, pytest, official
Python MCP SDK, Starlette, SQLite, Next.js 16, TypeScript, Docker, Fly, Vercel.

---

## Active Goal

Complete Prospect's final compute and evidence-hardening program before the July 13 submission:

1. Pre-register and execute an activation-specificity confound audit of the 79-target cross-study
   result.
2. Exhaustively soak and fuzz the canonical acceptance service across claim modes and transports.
3. Run independent adversarial reviews whose findings count only after a frozen test reproduces the
   issue.
4. Obtain real external-team usage or report the actual count without presenting fixtures as
   adoption.
5. Surface only results that change or materially sharpen the submission conclusion.
6. Keep every new scientific object proposal-only with `accepted=false`.
7. Preserve signed root `root_a8b0dcdd4024e12f`.
8. Finish with a green gate, fresh-clone reproduction, deployed smoke checks, and a submission
   freeze.

## Current Baseline

The baseline is commit `291223d` on `master`, aligned with `origin/master`.

- The signed frontier contains 53,485 objects and replays with zero drift at
  `root_a8b0dcdd4024e12f`.
- The real Claude Science submission is `proposal_f07c2c5c7578bbdb`, receipt
  `rcpt_f844b7e8206d9a8d`.
- The 52-gene associative signature has 12 `evidence_attached`, 25 `associative_only`, zero
  `contradicted`, and 15 `not_assayed` verdicts.
- The published cross-study calibration covers 79 targets. Stim48hr has Spearman rho `0.373895`,
  one-sided permutation P `0.00039996`, and all three original adversarial kills pass.
- Rest has descriptive rho `0.436270`, which is larger than Stim48hr. The current result therefore
  supports broad cross-study perturbation reach but does not establish activation specificity.
- PGGT1B remains `evidence_attached`; no comparable public replication clears its donor or batch
  specificity gap.
- The public adoption ledger contains zero real external-team submissions. The second-producer
  fixture demonstrates genericity only.

## Decision Rule For New Work

New work must answer one of these questions:

1. Does Stim48hr reach explain independent day-eight reach after controlling for Rest reach and
   pre-registered technical covariates?
2. Can malformed, adversarial, concurrent, or transport-shifted activity cause Prospect to produce
   inconsistent identities, silent wrong answers, or accepted state?
3. Does an existing public sentence exceed what its frozen artifact supports?

Do not start another genome-wide discovery campaign, literature corpus, module narrative, frontend
surface, or open-ended PGGT1B search. Do not mutate the existing calibration or signed frontier.

## Non-Negotiable Discipline

- New scientific outputs use typed statuses only.
- `contradicted` requires an explicit causal claim and a comparable readout.
- The sensitivity audit cannot retroactively alter the pre-registered 79-target calibration.
- Missing coverage remains `not_assayed`.
- Supplemental contexts retain explicit comparability.
- A model can suggest an attack but cannot decide whether it landed.
- All service stress tests use temporary local SQLite stores and `publish_to_ledger=false`.
- No automated step signs, accepts, or re-signs a proposal.
- No model API spending occurs until Will states a separate dollar cap.
- No em dashes, old-project branding, attribution footers, or secrets enter the repository.
- Every public scientific statement includes the ceiling: computation over released data, not
  wet-lab or clinical truth.

## Workstream A: Activation-Specificity Confound Audit

### Locked Scientific Question

Does Marson Stim48hr transcriptomic reach retain positive association with the independent day-eight
activated-CD4 knockout reach after controlling for Marson Rest reach and the independent-study batch?

This is a secondary sensitivity analysis. It does not replace the existing primary result.

### Locked Population

- Start from the 79 targets in `examples/data/gse271788/target_reach.csv` that overlap Marson.
- Use complete cases with both Marson Rest and Stim48hr values. The expected complete-case count is
  76, but the implementation must derive and assert the count from frozen inputs.
- Do not replace missing Rest values with zero.
- Keep the two independent-study batches as fixed strata:
  `gse171737_il2ra_regulators` and `gse271788_iei_background`.

### Locked Primary Statistic

Compute partial Spearman correlation by this exact procedure:

1. Rank independent day-eight reach, Stim48hr reach, and Rest reach with average ranks for ties.
2. Encode batch as one binary fixed-effect column.
3. Regress ranked Stim48hr reach on an intercept, ranked Rest reach, and batch.
4. Regress ranked independent reach on the same design matrix.
5. Compute Pearson correlation between the two residual vectors.
6. Report the result as partial Spearman rho.

Do not log-transform, winsorize, trim, or change thresholds after observing the result.

### Locked Primary Inference

- Seed: `271789`.
- Permutations: 10,000.
- Bootstrap samples: 10,000.
- Alternative: partial rho is greater than zero.
- Permutation method: Freedman-Lane residual permutation within each frozen batch.
- P value: `(permuted at least observed + 1) / 10001`.
- Bootstrap: sample targets with replacement within each batch, preserving each batch size.
- Confidence interval: percentile 95 percent interval.

The activation-specific extension earns `evidence_attached` only when:

1. One-sided permutation P is at most `0.01`.
2. The lower bootstrap bound is above zero.
3. Every status-determining kill below passes.

Otherwise type the extension `orthogonal_phenotype` and state that broad reach replicates while
incremental activation-specific reach is not established. This analysis cannot earn `contradicted`.

### Locked Adversarial Kills

1. **Batch direction:** partial association is positive in each batch where the model has enough
   complete cases to estimate it.
2. **General machinery:** after excluding targets with Replogle K562 reach above 25, the partial
   association remains positive. K562 gaps remain `not_assayed` and are reported separately.
3. **Influential target:** every leave-one-target-out partial association remains positive.
4. **Subset instability:** 10,000 seeded leave-five-target-out draws all report their distribution;
   at least 95 percent must remain positive.
5. **Cell-count confound:** residualize both ranked outcomes on ranked Rest reach, batch, and ranked
   median live-cell count. The resulting partial association must remain positive.

Editing efficiency is missing by design for the older GSE171737 batch. Report the editing-efficiency
subset as descriptive sensitivity only. Do not impute it and do not use it to determine status.

### Required Outputs

- `examples/data/gse271788_activation_specificity_preregistration.json`
- `docs/GSE271788_ACTIVATION_SPECIFICITY_PREREGISTRATION.md`
- `frontier/gse271788_activation_specificity.py`
- `examples/data/gse271788_activation_specificity.json`
- `docs/GSE271788_ACTIVATION_SPECIFICITY.md`
- `tests/test_gse271788_activation_specificity.py`

The result must contain:

- pre-registration id and hashes of every frozen input;
- complete-case target list and missing rows;
- primary partial rho, P value, interval, seed, and sample counts;
- every kill result and all exclusion lists;
- descriptive editing-efficiency sensitivity;
- one Receipt v1 proposal with replay command;
- `accepted=false`, `human_signature_required`, and unchanged frontier root.

## Workstream B: Exhaustive Acceptance Soak

### Required Scale

Run the following against temporary local stores:

- All 11,526 Marson genes under `associative_signature` and `explicit_driver_claim`.
- Both `primary_only` and `all_frozen` evidence modes.
- Direct Python, HTTP, stdio MCP, and Streamable HTTP MCP parity for each deterministic batch.
- At least 100,000 generated parser and identifier cases.
- At least 10,000 HTTP submissions sampled from the fuzz corpus.
- At least 1,000 concurrent requests across duplicate and unique payloads.
- At least 100 forced process restarts with proposal fetches after restart.
- Every Receipt v1 bound field and selected nested fields mutated independently.

Do not run the exhaustive corpus against the production Fly database. Production receives only the
small final smoke set.

### Input Families

The fuzz corpus must cover:

- plain symbols, Ensembl ids, frozen aliases, and unknown ids;
- duplicate genes across multiple JSON keys;
- varied DE and marker column names;
- quoted CSV, embedded newlines, BOMs, CRLF, tabs, and empty cells;
- Unicode confusables and non-human identifiers;
- malformed JSON and tables;
- injection-like strings and HTML fragments;
- empty inputs, one-gene inputs, maximum-size inputs, and over-limit inputs;
- conflicting claim modes and missing explicit-driver context;
- artifact descriptor mutations and self-declared producer metadata;
- repeated submissions before and after service restart.

### Invariants

Every typed case must satisfy:

1. The evaluator never crashes.
2. Unknown or uncovered genes become `not_assayed` or a clear input error.
3. An associative signature produces zero `contradicted` verdicts.
4. An explicit driver claim can produce `contradicted` only with complete comparable context.
5. Identical canonical requests produce identical proposal and receipt ids across transports.
6. A changed bound field changes the receipt id.
7. Duplicate submissions do not create divergent immutable proposal bodies.
8. Restarted storage returns the same proposal and receipt.
9. Every response contains `accepted=false`.
10. No submission event creates an acceptance event.

### Required Outputs

- `cli/acceptance_soak.py`
- `tests/test_acceptance_soak.py`
- `examples/data/acceptance_soak_report.json`
- `docs/ACCEPTANCE_SOAK.md`

The report stays outside the primary navigation. It records corpus seeds, counts, elapsed time,
transport totals, failure classes, receipt mutations, restart checks, and zero-acceptance evidence.

## Workstream C: Independent Adversarial Review

Run four independent review lanes:

1. **Source lane:** attack source hashes, row cardinalities, target mapping, missing-row semantics,
   donor labels, and batch membership.
2. **Statistics lane:** attack rank handling, residualization, exchangeability, bootstrap strata,
   influence, and multiple interpretations.
3. **Protocol lane:** attack receipt identity, claim comparability, persistence, transport parity,
   and acceptance-event separation.
4. **Narrative lane:** attack every public number, status word, screenshot, demo sentence, and
   submission claim.

Raw model output belongs under gitignored `var/red_team/`. A review statement changes code or prose
only after an engineer writes a deterministic failing test or points to a frozen artifact mismatch.
The final normalized report is `docs/FINAL_RED_TEAM.md` and contains:

- attack id;
- target claim or invariant;
- evidence inspected;
- deterministic reproduction command;
- landed or did-not-land result;
- code or wording change, if any;
- remaining risk.

Without an explicit model budget, run source, statistics, protocol, and narrative checks with local
code only. Record that the model-proposed attack lane was not run rather than spending credits.

## Workstream D: Real External Usage

This workstream depends on human outreach.

Provide another team with both paths:

- Web: `https://prospect-sepia-six.vercel.app`
- MCP: `https://prospect-acceptance.fly.dev/mcp`

Ask for a real gene list, signature JSON, ranked marker table, or DE CSV. Require explicit consent
before `publish_to_ledger=true`. Producer identity remains self-declared.

Target two real external-team proposals. For each, preserve:

- team-provided producer label;
- input artifact hash;
- claim mode and context;
- proposal and receipt ids;
- typed-status counts;
- proposal URL;
- confirmation that no human acceptance occurred.

If no team responds by submission freeze, report adoption count zero. Keep the second-producer
fixture labeled as genericity evidence, never adoption evidence.

## Workstream E: Surface, Freeze, and Submit

### Surface Rule

Do not add navigation. The activation-specificity audit may appear in the existing Evidence surface
only when it changes or materially sharpens the interpretation:

- If it clears the locked bar, state that Stim48 contributes incremental rank information beyond
  Rest under the frozen sensitivity rule.
- If it fails, state that broad perturbation reach replicates but activation-specific incremental
  reach does not clear the pre-registered bar.

Do not put the soak report on the first screen. Surface a service defect only after fixing it and
pinning the regression test.

### Freeze Rule

Will confirms the official submission cutoff. Freeze code at least 12 hours before that cutoff.
After freeze, accept only:

- correctness fixes;
- deployment failures;
- broken demo paths;
- wording that violates a typed-status or comparability rule.

No new dataset, feature, claim family, or visual redesign enters after freeze.

## Task Plan

### Task 1: Commit the sensitivity pre-registration

**Files:**
- Create: `examples/data/gse271788_activation_specificity_preregistration.json`
- Create: `docs/GSE271788_ACTIVATION_SPECIFICITY_PREREGISTRATION.md`
- Test later: `tests/test_gse271788_activation_specificity.py`

**Steps:**

1. Write the exact population, statistic, permutation, bootstrap, kill, and status rules above.
2. Bind the existing source manifest, target projection, Marson table, and K562 table hashes.
3. Compute a content-addressed pre-registration id over the body excluding the id field.
4. Confirm the JSON and Markdown agree.
5. Scan for em dashes and forbidden branding.
6. Commit only the pre-registration files.

**Commit:**

```bash
git add examples/data/gse271788_activation_specificity_preregistration.json \
  docs/GSE271788_ACTIVATION_SPECIFICITY_PREREGISTRATION.md
git commit -m "Pre-register activation specificity audit"
```

Do not run any new scoring before this commit exists.

### Task 2: Write failing tests for the locked audit

**Files:**
- Create: `tests/test_gse271788_activation_specificity.py`

**Steps:**

1. Test pre-registration id and source hashes.
2. Test complete-case and missing-row semantics.
3. Test average-rank ties and partial-correlation residualization on hand-calculated fixtures.
4. Test within-batch permutation determinism.
5. Test stratified bootstrap determinism.
6. Test each kill independently with synthetic pass and fail fixtures.
7. Test receipt identity, proposal-only state, and unchanged root.
8. Run the test file and confirm failure because the module does not exist.

**Run:**

```bash
python -m pytest tests/test_gse271788_activation_specificity.py -q
```

**Expected:** fail during import of `frontier.gse271788_activation_specificity`.

### Task 3: Implement and freeze the audit

**Files:**
- Create: `frontier/gse271788_activation_specificity.py`
- Create: `examples/data/gse271788_activation_specificity.json`
- Create: `docs/GSE271788_ACTIVATION_SPECIFICITY.md`
- Modify: `tests/test_gse271788_activation_specificity.py`

**Steps:**

1. Reuse frozen input validation from `frontier/gse271788_calibration.py`.
2. Implement rank, least-squares residual, partial correlation, Freedman-Lane permutation, and
   stratified bootstrap functions.
3. Implement all five status-determining kills.
4. Implement descriptive editing-efficiency sensitivity without imputation.
5. Build a Receipt v1 proposal that binds every input and the pre-registration.
6. Write deterministic JSON and Markdown outputs.
7. Add `--check` and drift detection.
8. Run the test file until it passes.
9. Run the complete Prospect gate.
10. Commit the implementation and frozen outputs.

**Commit:**

```bash
git add frontier/gse271788_activation_specificity.py \
  tests/test_gse271788_activation_specificity.py \
  examples/data/gse271788_activation_specificity.json \
  docs/GSE271788_ACTIVATION_SPECIFICITY.md
git commit -m "Audit activation specific cross-study reach"
```

### Task 4: Write the soak harness tests

**Files:**
- Create: `tests/test_acceptance_soak.py`
- Modify only if needed: `cli/robustness_fuzz.py`

**Steps:**

1. Define deterministic corpus seeds and scale constants.
2. Test corpus generation without running the full soak in ordinary pytest.
3. Test all invariants on a small representative corpus.
4. Test restart and duplicate-submission behavior with temporary stores.
5. Test receipt mutation coverage against `canonical_receipt_body()`.
6. Run the tests and confirm they fail because the soak harness is absent.

### Task 5: Implement and run the exhaustive soak

**Files:**
- Create: `cli/acceptance_soak.py`
- Create: `examples/data/acceptance_soak_report.json`
- Create: `docs/ACCEPTANCE_SOAK.md`
- Modify: `tests/test_acceptance_soak.py`
- Modify if a defect lands: the narrow owning module and its regression test

**Steps:**

1. Implement checkpointed JSONL progress under gitignored `var/acceptance_soak/`.
2. Implement resume by corpus seed and completed case id.
3. Run direct evaluator coverage for every gene and both claim modes.
4. Run both evidence modes.
5. Run local HTTP, stdio MCP, and Streamable HTTP MCP parity.
6. Run the 100,000-case normalization corpus.
7. Run concurrency, restart, duplicate, limit, and mutation lanes.
8. Stop immediately on silent wrong answer, accepted state, or identity drift.
9. Write a failing regression test before fixing any defect.
10. Regenerate the final compact report after every lane reaches target scale.
11. Run the complete gate and commit.

**Run:**

```bash
python -m cli.acceptance_soak --resume --full
python -m cli.acceptance_soak --check
```

**Commit:**

```bash
git add cli/acceptance_soak.py tests/test_acceptance_soak.py \
  examples/data/acceptance_soak_report.json docs/ACCEPTANCE_SOAK.md
git commit -m "Exhaust the acceptance service invariants"
```

### Task 6: Run and adjudicate the red team

**Files:**
- Create: `docs/FINAL_RED_TEAM.md`
- Modify: only files with a reproduced defect or unsupported sentence
- Test: add one narrow regression test for each landed issue

**Steps:**

1. Create four attack briefs under `var/red_team/`.
2. Run local deterministic audits first.
3. Run model-proposed attacks only after Will sets a dollar cap.
4. Reproduce each proposed issue with frozen code or reject it with a recorded reason.
5. Fix landed issues in separate commits.
6. Run the complete gate after each landed fix.
7. Write the normalized report and commit it.

### Task 7: Collect external proposals

**Files:**
- Modify only after consent: persistent production ledger through the service
- Update: `docs/HANDOFF.md`
- Update: `docs/SUBMISSION.md`

**Steps:**

1. Send the web and MCP paths to at least two teams.
2. Keep publication off unless each submitter consents.
3. Confirm each proposal survives refresh and replay.
4. Record the actual external-team count.
5. Keep fixtures out of the adoption count.
6. Commit only documentation changes, never private submissions.

### Task 8: Update the existing Evidence surface only if earned

**Files:**
- Modify if warranted: `receipt/causal_bridge.py`
- Modify if warranted: `web/app/page.tsx`
- Modify if warranted: `web/gen_data.py`
- Modify: `docs/HANDOFF.md`
- Modify: `docs/SUBMISSION.md`
- Modify: `docs/DEMO.md`
- Test: `tests/test_web_data_contract.py`

**Steps:**

1. Write a failing data-contract test for the exact earned interpretation.
2. Add a compact audit summary to the existing Evidence surface.
3. Do not add navigation, a campaign packet, or a new first-screen card.
4. Regenerate web data.
5. Run typecheck, build, and in-app Browser QA.
6. Commit only if the audit changes the story.

### Task 9: Final gate and fresh-clone reproduction

**Run:**

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
cd web && npm run typecheck && npm run build
docker build -f Dockerfile.acceptance -t prospect-acceptance:final .
```

Then clone `origin/master` without hardlinks into a fresh temporary directory, install pinned Python
and Node dependencies, and run the same gate. Record the final commit and root.

### Task 10: Deploy, smoke, and freeze

**Steps:**

1. Push only after the complete gate and fresh-clone run pass.
2. Deploy the acceptance service from the final commit.
3. Deploy the web app from the same commit.
4. Confirm direct Python, HTTP, stdio MCP, hosted MCP, and proposal replay return identical ids.
5. Use the in-app Browser for desktop, 390-pixel mobile, light, dark, keyboard, overflow, console,
   submission, refresh, and proposal permalink checks.
6. Run `./prospect rigor-audit` and regenerate the judge handout.
7. Confirm no tracked em dash or forbidden brand reference exists.
8. Confirm `root_a8b0dcdd4024e12f` is unchanged.
9. Record the actual external-team count.
10. Declare submission freeze.

## Checkpoint Cadence

Report after each milestone:

1. Pre-registration committed, before scoring.
2. Primary partial rho and its exact complete-case count.
3. Each adversarial kill, including exclusions and missing coverage.
4. Final sensitivity status and receipt id.
5. Soak progress at 10 percent intervals and any landed defect.
6. Final soak totals and zero-acceptance result.
7. Red-team attacks landed or rejected.
8. External-team count.
9. Final gate, deployment, and freeze commit.

Every report must distinguish full-scale completion from a sample.

## Completion Criteria

The active goal is complete only when:

- the sensitivity pre-registration predates scoring;
- the partial-correlation result and all five kills replay from frozen inputs;
- the result is typed by the locked rule without changing the original calibration;
- the exhaustive soak reaches its declared scales or records a concrete resource failure;
- every transport preserves canonical ids on the tested corpus;
- no malformed input creates silent wrong output or accepted state;
- every landed red-team issue has a deterministic regression test;
- the actual external-team count is reported honestly;
- no unearned result expands the public surface;
- the full and fresh-clone gates pass;
- Fly and Vercel correspond to the final pushed commit;
- every new proposal remains `accepted=false`;
- signed root `root_a8b0dcdd4024e12f` remains unchanged;
- Will retains sole control of signing, video recording, and final submission.

## Human-Only Boundary

Will alone:

- sets any model API budget;
- approves external ledger publication;
- signs or accepts a proposal;
- confirms the official deadline and freeze time;
- records the video;
- submits the hackathon entry.

