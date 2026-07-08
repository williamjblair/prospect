# Prospect Acceptance Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Prospect usable by another team this week through generic input normalization, typed verdicts, receipts, shareable state pages, a web paste flow, and a one-command HTTP service.

**Architecture:** Keep the frozen verifier in Python as the canonical trust path. Add a parser that normalizes common biology outputs into gene symbols, then call the existing causal bridge to produce typed driver, passenger, contradiction, and not-assayed verdicts. The web paste flow consumes a generated acceptance rule derived from the same frozen Marson table, while the one-command Python service provides `/submit`, `/state/<id>`, and `/mcp` for hosted use.

**Tech Stack:** Python stdlib for parser, service, tests, and MCP HTTP shim. Next.js client component for the paste and share-link path. Existing Prospect receipt schema and Marson frozen table for verdicts.

---

### Task 1: Generic Input Normalization

**Files:**
- Create: `receipt/input_normalizer.py`
- Test: `tests/test_acceptance_service.py`

- [x] Add tests for signature JSON, DE CSV with varied columns, ranked marker CSV, plain gene lists, Ensembl ids, aliases, duplicates, unknowns, empty input, and wrong columns.
- [x] Implement `parse_submission_text(text, filename="")` returning `{"genes": [...], "warnings": [...], "input_kind": "..."}`.
- [x] Build symbol and Ensembl maps from `examples/data/marson_de_full.csv`.
- [x] Add a small alias map for common checkpoint names such as PD-1, TIM3, CTLA-4, LAG-3, and TIGIT.

### Task 2: Canonical Submission Service

**Files:**
- Create: `receipt/acceptance_service.py`
- Modify: `receipt/causal_bridge.py`
- Test: `tests/test_acceptance_service.py`

- [x] Add tests that a parsed submission returns typed counts, a receipt, `accepted=false`, `human_signature_required`, and a deterministic share id.
- [x] Add tests that malformed input fails with a clear message rather than a traceback.
- [x] Implement `build_submission_result(text, filename="", source_name="external")`.
- [x] Route generic MCP bundles through the same parser instead of only raw gene arrays.

### Task 3: One-Command HTTP and MCP Endpoint

**Files:**
- Create: `services/prospect_acceptance_service.py`
- Modify: `cli/__main__.py`
- Test: `tests/test_acceptance_http_service.py`

- [x] Add tests that `POST /submit` returns a typed result and state URL.
- [x] Add tests that `GET /state/<id>` returns a readable HTML state page.
- [x] Add tests that `POST /mcp` supports `tools/list` and `tools/call` for `prospect.receipt.submit_artifact`.
- [x] Add `./prospect serve-acceptance --port 8130`.

### Task 4: Web Paste Flow and Share Link

**Files:**
- Modify: `web/app/page.tsx`
- Test: `tests/test_acceptance_web_contract.py`

- [x] Add tests that page source contains the paste form, share-link logic, and required status labels.
- [x] Add a compact Overview section where a user can paste genes, CSV, or JSON.
- [x] Compute typed counts client-side from a generated acceptance lookup derived from the frozen Marson table.
- [x] Encode a compact result in `#prospect-state=` so the page can be shared.

### Task 5: Guide and Gate

**Files:**
- Create: `docs/RUN_YOUR_OWN_CLAIM.md`
- Modify: `docs/JUDGE_HANDOUT.md`, `cli/judge_handout.py`, `docs/RECEIPT_BRIDGE.md`
- Test: existing docs and web contracts

- [x] Document web paste and one-command HTTP paths for another hackathon team.
- [x] Include the accepted-state boundary and computation-only ceiling.
- [ ] Run full gate and Browser QA.
- [ ] Commit locally. Do not push or deploy.
