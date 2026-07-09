# Prospect deploy readiness

Prospect has two deployable surfaces: the static web app and the canonical acceptance service. Deploy only after the local gate and service tests pass.

`./scripts/prepare_deploy.sh` never rebuilds or signs accepted frontier state. It hashes the five
signed frontier inputs and `frontier.sig.json` before and after regenerating proposal receipts and
public data, and stops if any signed-state byte changes. The expected root remains
`root_a8b0dcdd4024e12f`.

## Acceptance service contract

The service exposes:

- `POST /submit` for JSON submissions.
- `GET /proposal/<proposal_id>` and the matching `.json` representation.
- `GET /ledger` and `/ledger.json` for submissions whose sender set `publish_to_ledger=true`.
- `POST /mcp` as the official MCP SDK Streamable HTTP endpoint.
- `GET /health` with frozen substrate hashes, SQLite write status, and table counts.

Producer identity is self_declared. A sender must opt in before its submission event appears in the public ledger. Proposals are immutable, submission events are append-only, and acceptance events are stored separately.

## Local service check

```bash
python -m pytest \
  tests/test_acceptance_http_service.py \
  tests/test_acceptance_service_workstream1.py \
  tests/test_acceptance_http_mcp_sdk.py -q

docker build -f Dockerfile.acceptance -t prospect-acceptance .
docker run --rm -p 8130:8130 \
  -e PROSPECT_ACCEPTANCE_PUBLIC_URL=http://127.0.0.1:8130 \
  -e PROSPECT_ACCEPTANCE_CORS_ORIGIN=http://127.0.0.1:8125 \
  -v prospect_acceptance_data:/data \
  prospect-acceptance
```

Check health and submit one private proposal:

```bash
curl -fsS http://127.0.0.1:8130/health
curl -fsS http://127.0.0.1:8130/submit \
  -H 'content-type: application/json' \
  -d '{"producer":"deploy_smoke","filename":"genes.txt","input_text":"IL7R\nCCR7\nPD-1","claim_mode":"associative_signature","publish_to_ledger":false}'
```

The response must contain a `/proposal/` URL, `accepted=false`, and `human_signature_required`.

## Complete local preparation

```bash
./scripts/prepare_deploy.sh
```

This runs the complete secret-free gate, TypeScript checking, the static web build, and the
acceptance-service container build. It prints the human-run deployment commands but does not run
them.

## Fly deployment

Create the app and persistent volume once, then deploy:

```bash
fly apps create prospect-acceptance
fly volumes create prospect_acceptance_data --region sjc --size 1 --app prospect-acceptance
fly deploy --config fly.acceptance.toml
```

Production configuration:

- `PROSPECT_ACCEPTANCE_DATA_DIR=/data`
- `PROSPECT_ACCEPTANCE_PUBLIC_URL=https://prospect-acceptance.fly.dev`
- `PROSPECT_ACCEPTANCE_CORS_ORIGIN=https://prospect-sepia-six.vercel.app`
- `PROSPECT_ACCEPTANCE_MAX_REQUEST_BYTES=1000000`
- `PROSPECT_ACCEPTANCE_MAX_GENES=5000`
- `PROSPECT_ACCEPTANCE_RATE_LIMIT=120`
- `PROSPECT_ACCEPTANCE_RATE_WINDOW=60`

The CORS origin is exact. Add another explicit comma-separated origin only when a second deployed client requires it. Do not use `*`.

## Web deployment

Build the web app with the service URL configured:

```bash
export NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL=https://prospect-acceptance.fly.dev
cd web
vercel --prod --yes --scope "$VERCEL_SCOPE"
```

## Live smoke

```bash
curl -fsS https://prospect-acceptance.fly.dev/health
curl -fsS https://prospect-acceptance.fly.dev/ledger.json
```

Then use an official MCP client against `https://prospect-acceptance.fly.dev/mcp` and confirm the only tools are schema discovery, artifact submission, proposal retrieval, and the receipt submission compatibility alias. Direct Python, HTTP, and MCP submissions of the same request must return identical receipt and proposal IDs.

Finally, open a returned HTTPS proposal URL twice and confirm it survives refresh, includes artifact hashes and the replay command, and remains `accepted=false`.
