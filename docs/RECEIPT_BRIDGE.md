# Receipt bridge

Prospect exposes the activity-to-state boundary as a small local MCP server.
An external workbench can discover the receipt contract, validate a receipt,
and submit it as a proposal. Submission never moves accepted state. Accepted
state still requires the frozen verifier and the human signing path.

The written receipt shape is [RECEIPT_SCHEMA.md](RECEIPT_SCHEMA.md), backed by
`receipt/receipt_schema_v0.json`.

Run:

```bash
./prospect mcp
```

The server speaks JSON-RPC over stdio and exposes four tools:

| tool | purpose |
|---|---|
| `prospect.receipt.schema` | returns the receipt contract and current frontier manifest |
| `prospect.receipt.validate` | checks receipt shape, typed status, replay fields, and acceptance fields |
| `prospect.receipt.submit` | returns a proposal result with `accepted: false` and `next: human_signature_required` |
| `prospect.receipt.submit_artifact` | accepts an external claim bundle or gene list and returns typed causal verdicts |

Example:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n' | ./prospect mcp
```

Judge demo client:

```bash
python examples/receipt_bridge_client.py
python examples/receipt_bridge_client.py --json
python examples/claude_science_connector_client.py --json
python examples/prospect_connector_client.py --case openresearch --json
python examples/openresearch_receipt_client.py --json
```

The receipt client starts `./prospect mcp`, discovers the tools, validates the
first committed receipt, and submits it across the bridge. The expected summary
contains `accepted=false` and `next=human_signature_required`. It does not write
the frontier signature or receipt bundle.

The Claude Science client submits a real local export from the Sade-Feldman
2018 melanoma immunotherapy scRNA-seq session:

- `examples/data/claude_science_real_export/signature_genes.json`
- `examples/data/claude_science_real_export/responder_DE_CD8.csv`
- `examples/data/claude_science_real_export/responder_DE_all.csv`

The source session produced an associative responder signature and noted that
the signature needs independent validation. Prospect does not say the signature
is wrong. It separates candidate causal drivers from associative passengers by
checking each gene against its strongest on-target effect across Rest, Stim8hr,
and Stim48hr in the frozen Marson CRISPRi screen. The pinned result is 52
submitted genes, 12 drivers typed `evidence_attached`, 22 `associative_only`
passengers, 3 `contradicted` explicit checkpoint-driver claims, and 15
`not_assayed` comparably. The connector returns `accepted=false` and
`next=human_signature_required`.

The OpenResearch-style client constructs a biology-shaped external run bundle,
replays the VAV1 claim against the Marson checker through the same
`prospect.receipt.submit_artifact` tool, and submits the resulting receipt as a
proposal only.

The static export lives at:

- `receipts/bridge/receipt_contract.json`
- `receipts/bridge/receipt_manifest.json`
- `receipts/bridge/receipt_bundle.json`

For the web app, the same files are copied under:

- `web/public/data/receipt_bridge/receipt_contract.json`
- `web/public/data/receipt_bridge/receipt_manifest.json`
- `web/public/data/receipt_bridge/receipt_bundle.json`

This is the protocol point: Claude activity can produce a receipt, but the
receipt is still only a proposal until the frozen gate and a human key accept
the state change.
