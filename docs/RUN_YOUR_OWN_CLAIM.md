# Run your own claim through Prospect

Prospect accepts a gene list, signature JSON, ranked marker table, or DE CSV. It normalizes common
symbols, aliases, and frozen Ensembl mappings, then returns typed per-gene verdicts from a frozen
perturbation evaluator. Every result is a proposal with `accepted=false` and
`next=human_signature_required`.

Ceiling: computation over released data, not wet-lab or clinical truth.

## Web

Open Check, choose the claim mode, paste the artifact, and submit. Associative signature is the
default. Explicit causal claim requires a source, cell type, condition, and phenotype. Only a
comparable explicit claim can earn `contradicted`.

The response links to a persistent proposal page containing the receipt, replay command, artifact
hashes, typed verdicts, and human acceptance boundary. Producer identity is self-declared. Publish
to the public ledger only when the submitter consents.

## HTTP

```bash
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service

curl -s http://127.0.0.1:8130/submit \
  -H 'content-type: application/json' \
  -d '{"producer":"external_team","filename":"signature.txt","input_text":"IL7R\nCCR7\nPD-1\nNOTGENE","claim_mode":"associative_signature","publish_to_ledger":false}'
```

Open the returned `proposal_url`. The SQLite database stores immutable proposals, append-only
submission events, and separate acceptance events. `/ledger` and `/ledger.json` expose only events
submitted with `publish_to_ledger=true`.

## MCP

Hosted Streamable HTTP endpoint: `http://127.0.0.1:8130/mcp`.

Tools:

- `prospect.acceptance.discover_schema`
- `prospect.acceptance.submit_artifact`
- `prospect.acceptance.get_proposal`

The service uses the official Python MCP SDK. Stdio compatibility remains available through
`./prospect mcp`.

## Typed Verdicts

- `evidence_attached`: perturbing the gene moves the selected frozen program enough to attach causal-driver evidence.
- `associative_only`: the gene is in the input, but does not meet the causal-driver rule in this assay.
- `contradicted`: a comparable explicit causal-driver claim is refuted by the selected assay.
- `not_assayed`: the frozen substrate cannot test the gene.

Unknown genes and sparse comparator coverage become `not_assayed`, never silent failures or
contradictions.
