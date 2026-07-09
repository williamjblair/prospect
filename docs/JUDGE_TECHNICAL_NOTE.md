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

Prospect does not claim wet-lab or clinical truth. It proves computation over released data.

## Receipt shape

Every receipt carries:

- producer identity and input kind
- claim under test
- artifact hashes
- typed evidence atoms
- replay command
- state diff showing no model-applied mutation
- human signature requirement

The schema lives at `receipt/receipt_schema_v0.json`, and the bridge contract is exported under `/data/receipt_bridge/`.

## Judge commands

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python examples/claude_science_connector_client.py --json
python examples/prospect_connector_client.py --case openresearch --json
./prospect demo-mode --reset
```

The demo command creates one shareable proposal state through the same acceptance rule the service uses.
