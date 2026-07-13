# Prospect one-page judge handout

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## What Prospect proves

Prospect tells a biologist which genes in an AI-generated prediction list behave as causal drivers, which are passengers, and which driver claims the perturbation data contradicts. The first-screen output is a driver/passenger/contradicted split.

Reproducible is not verified.

Prospect proves computation over released data, not wet-lab or clinical truth.

## Numbers To Inspect

- Real Claude Science signature: reviewer no issues found, Prospect returned 52 genes, 12 drivers, 25 passengers, 0 contradicted driver claims, 15 not assayed, and accepted=false
- ORCS primary T-cell context reduces uncovered Sade-Feldman genes to 5
- GSE278572: 24 overlapping regulators, 1 pre-registered interpretation qualification
- GSE171737/GSE271788: 79 shared primary-CD4 perturbations, rho 0.373895, permutation P 0.00039996, 3 of 3 adversarial kills passed
- Activation-specific sensitivity: partial rho 0.045808, permutation P 0.35246475, 1 of 5 kills passed, status orthogonal_phenotype
- PGGT1B registry audit: 7 candidate accessions inspected, direct comparable replication found: no
- PGGT1B remains proposal-only; independent batch-specificity kill not cleared, protocol minimum donors 3
- 5 signed CD4+ findings and 7 receipts
- 12 public data artifacts
- Reliability benchmark: 46 of 96 confident major-regulator claims contradicted (47.9%, 95% CI 38 to 58 percent); famous genes overclaimed 63.9% versus 7.0% baseline, permutation p 0.0001; stated confidence does not track correctness

## Five-minute judge path

1. Check: real Claude Science signature enters Prospect and receives typed causal verdicts.
2. Check: paste a gene list, DE table, or signature and copy the shareable result link.
3. Check: inspect the reliability benchmark, about half of confident claims contradicted (95% CI 38 to 58 percent), 64% on famous genes at permutation p 0.0001.
4. Check: inspect the GSE278572 correction that qualifies Prospect's own MED12 interpretation.
5. Evidence: inspect the broad 79-target calibration, then its activation-specific sensitivity that does not clear the locked bar.
6. Lead: PGGT1B is the caveated mechanism-first hypothesis worth testing.
7. Evidence: signed CD4+ T-cell findings show the frozen evidence graph.
8. Receipts: receipts and MCP bridge show accepted=false until a human key signs.

## Trust Boundary

- Model role: propose, search, draft
- Model in trust path: no
- Accepted record: human_signed_replayable_root
- Model accepted record mutations: 0

## Public Artifacts

- `/data/check.json`
- `/data/frontier.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/gse278572_comparator.json`
- `/data/gse271788_calibration.json`
- `/data/gse271788_activation_specificity.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/overclaim_counter.json`

## Commands

**Offline: a bare `git clone` + `pip install -r requirements.txt`. No API key, no network, no hosted service.**

- `./prospect verify`
- `./prospect reliability-benchmark`
- `python benchmark/mutation_pack.py`
- `python tests/test_skill_parity.py`
- `python tests/test_marson.py`
- `./prospect demo-mode --reset`
- `./prospect claude-science`
- `./prospect substrate-coverage`
- `./prospect pggt1b-defended-evidence`
- `python frontier/gse271788_calibration.py --check`
- `python frontier/gse271788_activation_specificity.py --check`
- `python examples/claude_science_connector_client.py --json`
- `python examples/receipt_bridge_client.py --json`
- `python receipt/replay_proposal.py <local-proposal.json>`

**Needs a local acceptance service: start it first, then point the connectors at it.**

- `./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service`
- `python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json`
- `python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json`

**Hosted (already live): the paste box and the hosted MCP at prospect-acceptance.fly.dev run the same frozen gate.**

- `python receipt/replay_proposal.py <hosted-proposal-url>`

Verify the signature, do not re-sign. The signed root is committed; a fresh clone auto-generates its own local key, so a signing command would mint a different root. Re-derive and compare the committed root instead.

## What remains human-only

- sign the evidence root
- accept a submitted receipt
- accept a PGGT1B record change
- wet-lab execution
