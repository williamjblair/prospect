# Prospect deploy readiness

This prepares deploys. It does not deploy from Codex.

## Local gate

```bash
./prospect deploy-checklist --run
```

The command regenerates the local derived surfaces, runs the full local gate, builds the web app, then prints the deploy commands for Will.

## Web deploy

Set the hosted acceptance service URL before the web build:

```bash
export NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL=https://<acceptance-service-host>
cd web && vercel --prod --yes --scope constellate-dc388081
```

## Acceptance service deploy

The service is containerized by `Dockerfile.acceptance` and `fly.acceptance.toml`.

```bash
fly deploy --config fly.acceptance.toml
```

Required service env:

- `PROSPECT_ACCEPTANCE_DATA_DIR`
- `PROSPECT_ACCEPTANCE_RATE_LIMIT`
- `PROSPECT_ACCEPTANCE_RATE_WINDOW`
- `PROSPECT_ACCEPTANCE_CORS_ORIGIN`

The service exposes:

- `/health`
- `/guide`
- `/ledger`
- `/ledger.json`
- `/state/<state_id>`
- `/mcp`

## Post-deploy smoke

```bash
./prospect post-deploy-smoke --base-url https://<acceptance-service-host>
```

The smoke submits a real gene-list proposal, opens the returned state page twice, checks `/ledger.json`, and confirms the result remains `accepted=false` with `human_signature_required`.
