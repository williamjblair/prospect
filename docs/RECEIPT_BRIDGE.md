# Receipt bridge

Prospect exposes the activity-to-state boundary as a small local MCP server.
An external workbench can discover the receipt contract, validate a receipt,
and submit it as a proposal. Submission never moves accepted state. Accepted
state still requires the frozen verifier and the human signing path.

Run:

```bash
./prospect mcp
```

The server speaks JSON-RPC over stdio and exposes three tools:

| tool | purpose |
|---|---|
| `prospect.receipt.schema` | returns the receipt contract and current frontier manifest |
| `prospect.receipt.validate` | checks receipt shape, typed status, replay fields, and acceptance fields |
| `prospect.receipt.submit` | returns a proposal result with `accepted: false` and `next: human_signature_required` |

Example:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n' | ./prospect mcp
```

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
