# Production Acceptance Service Implementation Plan

**Goal:** Make the Prospect acceptance service durable, container-ready, MCP-registerable, fuzz-tested, and adoption-countable for real external teams.

**Architecture:** Keep the current stdlib HTTP server, but move state management into a small disk-backed store under a configurable data directory. Keep all verdict generation in `receipt.acceptance_service`; the HTTP layer handles persistence, rate limiting, and MCP transport. The public ledger is derived from stored result JSON files, not a separate mutable record.

**Tech Stack:** Python stdlib HTTP server, JSON-RPC MCP over HTTP, current Prospect frozen Marson verifier, pytest, Docker, fly.io config.

---

### Task 1: Disk-Backed State Store

**Files:**
- Modify: `services/prospect_acceptance_service.py`
- Test: `tests/test_acceptance_service_workstream1.py`

**Steps:**
1. Write failing tests for storing a result, creating a fresh store, resolving `/state/<id>`, and rendering the ledger tally.
2. Implement `AcceptanceStore` with JSON files keyed by state_id plus a ledger method.
3. Wire `/state/<id>` and `/ledger.json` to the store.
4. Run focused tests.

### Task 2: MCP Tools Over HTTP

**Files:**
- Modify: `services/prospect_acceptance_service.py`
- Test: `tests/test_acceptance_service_workstream1.py`

**Steps:**
1. Write failing tests for `initialize`, `tools/list`, `prospect.acceptance.discover_schema`, `prospect.acceptance.submit_artifact`, and `prospect.acceptance.get_verdict`.
2. Add the tools and route them through the same verifier and store.
3. Run focused tests.

### Task 3: Robustness, Rate Limit, and Identifier Mapping

**Files:**
- Modify: `receipt/input_normalizer.py`
- Modify: `services/prospect_acceptance_service.py`
- Test: `tests/test_acceptance_service_workstream1.py`

**Steps:**
1. Write failing tests for malformed CSV, wrong columns, mixed IDs, duplicates, empty lists, 10k-gene lists, non-human genes, concurrent submissions, and submit rate limit.
2. Expand alias mapping from a committed alias table and enforce clear errors.
3. Add a simple per-client rate limiter to `/submit`.
4. Run focused tests.

### Task 4: Container and Fly Config

**Files:**
- Create: `Dockerfile.acceptance`
- Create: `fly.acceptance.toml`
- Test: `tests/test_acceptance_service_workstream1.py`

**Steps:**
1. Write failing static tests that assert health check, data dir, command, and port are present.
2. Add config files.
3. Run focused tests.

### Task 5: Docs and Gate

**Files:**
- Modify: `docs/JUDGE_HANDOUT.md` via generator if needed
- Modify: `docs/RECEIPT_BRIDGE.md` or create `docs/ACCEPTANCE_SERVICE.md`

**Steps:**
1. Document the one-command server, MCP registration path, ledger, and data directory.
2. Run full gate.
3. Commit locally.
