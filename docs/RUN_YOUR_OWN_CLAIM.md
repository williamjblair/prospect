# Run your own claim through Prospect

Prospect accepts a gene list, signature JSON, ranked marker table, or DE CSV. It normalizes common
symbols, aliases, and frozen Ensembl mappings, then returns typed per-gene verdicts from a frozen
perturbation evaluator. Every result is a proposal with `accepted=false` and
`next=human_signature_required`.

Ceiling: computation over released data, not wet-lab or clinical truth.

Hosted paths:

- Web: `https://prospect-sepia-six.vercel.app`
- MCP: `https://prospect-acceptance.fly.dev/mcp`
- Public ledger: `https://prospect-acceptance.fly.dev/ledger`

## Web

Open Check, choose the claim mode, paste the artifact, and submit. Associative signature is the
default. Explicit causal claim requires a source, cell type, condition, and phenotype. Only a
comparable explicit claim can earn `contradicted`.

The response links to a persistent proposal page containing the receipt, replay command, artifact
hashes, typed verdicts, and human acceptance boundary. Producer identity is self-declared. Publish
to the public ledger only when the submitter consents.

Prospect computes the submitted-input and frozen-substrate hashes. Supplemental hash descriptors
remain self-declared until fetched during human review.

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

Re-derive a saved or hosted proposal with frozen code:

```bash
python receipt/replay_proposal.py <proposal.json-or-url>
```

The replay recomputes the receipt identity and each trust-path verdict. It exits nonzero if the
receipt or a typed verdict drifted.

## MCP

Hosted Streamable HTTP endpoint: `http://127.0.0.1:8130/mcp`.

Production Streamable HTTP endpoint: `https://prospect-acceptance.fly.dev/mcp`.

Tools:

- `prospect.acceptance.discover_schema`
- `prospect.acceptance.discover_substrates`
- `prospect.acceptance.submit_artifact`
- `prospect.acceptance.get_proposal`

Set `evidence_mode` directly on `prospect.acceptance.submit_artifact`. Use `primary_only` for the
Marson causal typing substrate alone, or `all_frozen` for per-dataset evidence from every frozen
manifest. Do not place `evidence_mode` inside `claim_context`.

The service uses the official Python MCP SDK. Stdio compatibility remains available through
`./prospect mcp`.

## Typed Verdicts

- `evidence_attached`: perturbing the gene moves the selected frozen program enough to attach causal-driver evidence.
- `associative_only`: the gene is in the input, but does not meet the causal-driver rule in this assay.
- `contradicted`: a comparable explicit causal-driver claim is refuted by the selected assay.
- `not_assayed`: the frozen substrate cannot test the gene.

Unknown genes and sparse comparator coverage become `not_assayed`, never silent failures or
contradictions.

## External trial record

For a real team trial, preserve the self-declared producer label, submitted artifact SHA-256, claim
mode and context, proposal id, receipt id, typed counts, and proposal URL. Keep
`publish_to_ledger=false` unless the submitter explicitly consents to public ledger publication.
The proposal remains `accepted=false` in either case.
