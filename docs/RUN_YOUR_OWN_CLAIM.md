# Run your own claim through Prospect

Prospect accepts common AI biology outputs and returns typed causal verdicts
against the frozen Marson CD4+ CRISPRi Perturb-seq table. It does not accept
state. Every submission returns `accepted=false` and
`next=human_signature_required`.

Ceiling: computation over released data, not wet-lab or clinical truth.

## What you can paste

- Plain gene list, one gene per line or separated by commas.
- Signature JSON, including arrays such as `up`, `down`, `markers`, or
  `signature_genes`.
- DE or ranked marker CSV, with common columns such as `gene`, `symbol`,
  `gene_symbol`, `marker`, `feature`, `target`, or `name`.
- Mixed symbols, common aliases, and Ensembl IDs from the frozen Marson table.

Unknown genes, non-human genes, and genes not assayed in the Marson table return
`not_assayed`. Duplicates are ignored with a warning. Empty submissions and
tables without a gene-like column fail with a clear message.

## Path 1: no-setup web submit

Open the Overview tab and use **Run your own claim through Prospect**. Paste a
gene list or table and press **Submit to Prospect**. The result includes:

- typed counts: `evidence_attached`, `associative_only`, `contradicted`,
  `not_assayed`
- a receipt id
- `accepted=false`
- `human_signature_required`
- a shareable state link in the URL hash

Example input:

```text
IL7R
CCR7
PD-1
ENSG00000121410
NOTGENE
```

Expected shape: IL7R is typed as a candidate driver, CCR7 as an associative
passenger, PD-1 as a contradicted explicit driver claim in this assay, A1BG as
not assayed due to no on-target knockdown, and NOTGENE as not found.

## Path 2: one-command local service

Run the service:

```bash
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
```

Submit a claim:

```bash
curl -s http://127.0.0.1:8130/submit \
  -H 'content-type: application/json' \
  -d '{"source_name":"external_team","filename":"signature.txt","text":"IL7R\nCCR7\nPD-1\nNOTGENE"}'
```

Open the returned `state_url`, for example:

```text
http://127.0.0.1:8130/state/state_<id>
```

The service writes each result to `var/acceptance_service/states`, so the state
page survives a restart. The public ledger is:

```bash
curl -s http://127.0.0.1:8130/ledger.json
```

Health check:

```bash
curl -s http://127.0.0.1:8130/health
```

## Path 3: MCP-style connector call

The same service exposes the submit tool over a JSON-RPC style HTTP endpoint:

```bash
curl -s http://127.0.0.1:8130/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Submit an artifact bundle:

```bash
curl -s http://127.0.0.1:8130/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"prospect.acceptance.submit_artifact","arguments":{"source_name":"external_team","filename":"signature.txt","text":"IL7R\nCCR7\nPD-1\nNOTGENE"}}}'
```

Fetch the stored verdict:

```bash
curl -s http://127.0.0.1:8130/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"prospect.acceptance.get_verdict","arguments":{"state_id":"state_<id>"}}}'
```

For stdio MCP, use:

```bash
./prospect mcp
```

The tool name is the same: `prospect.receipt.submit_artifact`.

## Path 4: container service

The production service image is defined in `Dockerfile.acceptance` and uses
`PROSPECT_ACCEPTANCE_DATA_DIR` for durable state.

```bash
docker build -f Dockerfile.acceptance -t prospect-acceptance .
docker run --rm -p 8130:8130 -v "$PWD/var/acceptance_service:/data" prospect-acceptance
```

`fly.acceptance.toml` is the matching hosted service template. It exposes port
8130, checks `/health`, mounts `/data`, and keeps the same typed-status
contract.

## Typed verdicts

- `evidence_attached`: the submitted gene behaves as a candidate causal driver
  in the frozen Marson perturbation assay.
- `associative_only`: the submitted gene may be associated with a phenotype,
  but perturbation does not move the activation program enough to type it as a
  driver.
- `contradicted`: reserved for an explicit causal or driver claim refuted by
  the perturbation assay.
- `not_assayed`: absent from the frozen Marson table, not human-mapped here, or
  lacking on-target knockdown.

Prospect does not reject an external signature. It separates drivers from
passengers for the specific causal question this assay can test.
