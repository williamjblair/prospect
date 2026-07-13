# Prospect technical note for judges

## Trust model

Prospect separates activity from accepted state. An AI system, notebook, or external workbench can produce an artifact and a receipt. The receipt is a proposal. The trust path is frozen code over frozen released data, then a human Ed25519 key. A model cannot move accepted state.

Boundary:

```text
Activity < Receipt < Proposal < Review < Verification < Accepted < State
```

In this submission, public external submissions remain `accepted=false` and `human_signature_required`.

## Typed status ladder

- `evidence_attached`: the gene behaves as a candidate driver in the frozen perturbation rule.
- `associative_only`: the gene appears in an associative signature, but perturbation does not support a driver claim.
- `contradicted`: a causal or driver claim was explicitly made, and the frozen perturbation rule refutes that driver claim in this assay.
- `not_assayed`: the gene is not covered comparably by the frozen rule.
- `orthogonal_phenotype`: a supplemental dataset measures a non-equivalent condition or readout.

Prospect does not claim wet-lab or clinical truth. It proves computation over released data.

## Receipt shape

Every receipt carries:

- producer identity and input kind
- claim under test
- artifact hashes
- typed evidence atoms
- replay command
- proposed state diff showing no model-applied mutation
- human signature requirement

The schema lives at `receipt/receipt_schema_v1.json`, and the bridge contract is exported under `/data/receipt_bridge/`.

Each `all_frozen` proposal also binds `consulted_substrates[]` and `dataset_verdicts[]`. The same six
content-addressed manifests are discoverable through `GET /substrates`, hosted MCP
`discover_substrates`, and stdio MCP `prospect.receipt.substrates`.

## Judge commands

All of these run offline from a bare `git clone` + `pip install -r requirements.txt`: no API key,
no network, no hosted service (the connector clients use the stdio MCP, not the hosted `--url` path):

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python examples/claude_science_connector_client.py --json
python examples/prospect_connector_client.py --case openresearch --json
python frontier/gse271788_calibration.py --check
./prospect demo-mode --reset
```

The demo command creates one shareable proposal through the same acceptance rule the service uses.
The signed root `root_a8b0dcdd4024e12f` is committed; verify it by re-derivation, do not re-sign (a
fresh clone mints its own key and would produce a different root).
