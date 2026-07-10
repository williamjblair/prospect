# Prospect handoff

Read [AGENTS.md](../AGENTS.md) first. This file is the current implementation map for the Jul 13,
2026 Built with Claude: Life Sciences submission.

Active execution memo: [Final Compute and Evidence Hardening](plans/2026-07-10-final-compute-and-evidence-hardening.md).

## Product

Prospect tells a biologist which genes in an AI-generated list behave as candidate causal drivers in
a frozen perturbation assay. An associative submission can return `evidence_attached`,
`associative_only`, or `not_assayed`. `contradicted` is reserved for an explicit causal-driver claim
with a comparable phenotype that the frozen assay refutes.

The trust boundary is fixed: a producer emits activity, Prospect creates a Receipt v1 proposal,
frozen code replays it, and only a human Ed25519 acceptance event can change accepted state. Every
public submission is `accepted=false` with `next=human_signature_required`.
Receipt v1 envelopes are also always `accepted=false`. Their legacy frontier-root attestations
record provenance only and are not receipt acceptance events.

- Web: https://prospect-sepia-six.vercel.app
- Repo: https://github.com/williamjblair/prospect, branch `master`
- Signed root: `root_a8b0dcdd4024e12f`
- Ceiling: computation over released data, not wet-lab or clinical truth

## Judge Flow

1. Check opens on a real Claude Science Sade-Feldman scRNA-seq export.
2. The associative 52-gene signature types as 12 `evidence_attached`, 25 `associative_only`,
   0 `contradicted`, and 15 `not_assayed`.
3. The authenticated Claude Science run reported no reviewer issues, then Prospect independently
   returned proposal `proposal_f07c2c5c7578bbdb`, `accepted=false`, and
   `human_signature_required` after consulting all six frozen substrates.
4. A judge pastes a gene list, signature JSON, ranked marker table, or DE CSV. The canonical service
   returns an immutable proposal, receipt, replay command, and shareable HTTPS page.
5. An explicit causal claim can earn `contradicted` only when cell type, condition, phenotype, and
   source are declared and comparable.
6. Evidence shows the 48% and 64% overclaiming benchmark. Lead shows PGGT1B as one proposal-only
   experiment worth running. Receipts closes on the human acceptance boundary.

## Canonical Architecture

- `receipt/acceptance_service.py`: the only evaluator used by Python, HTTP, stdio MCP, and hosted MCP.
- `receipt/schema.py`: `prospect.receipt.v1`; the receipt id binds claim, producer, artifacts,
  conditions, verdicts, verifier, replay metadata, and proposed state diff.
- `services/prospect_acceptance_service.py`: official Python MCP SDK plus Streamable HTTP, SQLite
  immutable proposals, append-only submission events, and separate acceptance events.
- `receipt/mcp_server.py`: compatibility stdio MCP route, backed by the same evaluator.
- `web/app/page.tsx`: four primary surfaces, Check, Evidence, Lead, Receipts. No browser evaluator or
  browser receipt hashing exists.
- `web/public/data/check.json`: compact first load. `frontier.json` is lazy-loaded only for Explorer.
- `frontier/gse278572_comparator.py`: pre-registered corrective comparator.
- `frontier/gse271788_calibration.py`: pre-registered 79-target independent primary-CD4 calibration.
- `frontier/pggt1b_comparability_audit.py`: frozen PGGT1B coverage and readout audit.
- `receipt/substrate_manifest.py`: six frozen substrate manifests exposed through HTTP and MCP.

## Science State

The accepted frontier remains unchanged. New analyses are proposals only.

- Real Claude Science export: 52 genes, 12 drivers, 25 passengers, 0 contradictions, 15 not assayed.
  The authenticated UI run and its reviewer completed within a $5 cap. Reviewer result:
  `no_issues_found`. Prospect result: `accepted=false`, receipt `rcpt_f844b7e8206d9a8d`.
- Benchmark: 46 of 96 comparable major-regulator claims contradicted, 48%; 64% on the canonical
  checkpoint and cytokine subset.
- PGGT1B: `evidence_attached`. Shifrut and Schmidt cover PGGT1B only under non-matching readouts, so
  both are `orthogonal_phenotype`. No comparable public stimulated-transcriptome replication was found.
- GSE278572 correction: 24 overlapping regulators. MED12 meets the locked qualification rule in both
  Teff and Treg. High Rest reach argues against activation specificity, but cannot alone establish
  housekeeping or essentiality. Proposal `proposal_e33de6bedec7c950` remains unaccepted.
- GSE171737/GSE271788 calibration: 84 published targets, 79 overlapping Marson, five `not_assayed`.
  The pre-registered Stim48hr comparison has Spearman `rho=0.373895`, one-sided 10,000-permutation
  `P=0.00039996`, bootstrap 95% interval `[0.169361, 0.547610]`, and all three adversarial kills
  pass. Proposal `proposal_e32e34a8d41b10ab` remains unaccepted.
- PGGT1B registry audit: seven candidate accessions were inspected. No source directly perturbs
  PGGT1B with a comparable stimulated primary-human-CD4 transcriptomic readout, so the independent
  batch-specificity kill remains open.

`evidence_mode=primary_only` preserves the original canonical receipt identity. New Check requests
use `evidence_mode=all_frozen`, which binds all consulted manifests, dataset-specific verdicts,
comparability decisions, hashes, and replay commands into the receipt. `GET /substrates`, hosted MCP
`discover_substrates`, and stdio MCP `prospect.receipt.substrates` expose the same registry.
For hosted MCP, `evidence_mode` is a top-level submit field, not part of `claim_context`.

## Gate

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
cd web && npm run typecheck && npm run build
docker build -f Dockerfile.acceptance -t prospect-acceptance .
```

The acceptance path is secret-free. `.env` is only needed for optional Claude proposal loops. Never
print or commit it. Never re-sign or mutate `root_a8b0dcdd4024e12f` during automated work.

## Local Run

```bash
python -m pip install -r requirements.txt
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
cd web && NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL=http://127.0.0.1:8130 npm run dev -- --port 8125
```

Port 300 belongs to Atlas. Use 8125 for Prospect.

## Deployment

The service deploys from `Dockerfile.acceptance` and `fly.acceptance.toml` with a persistent volume.
The web uses one environment variable, `NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL`. Follow
[DEPLOY_READINESS.md](DEPLOY_READINESS.md), run the post-deploy smoke, then deploy the static app.

Will performs the final human-key decision, records the demo, and submits. Automated work must not
accept proposals or mutate the signed root.
