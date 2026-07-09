#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ACCEPTANCE_URL="${NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL:-https://<acceptance-service-host>}"

echo "Regenerating frozen public data"
python frontier/build.py
python frontier/verify.py
python receipt/emit.py
(cd web && python gen_data.py)

echo "Running Prospect gate"
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
(cd web && npm run build)

echo ""
echo "Prepared. Will runs deploy commands:"
echo "export NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL=${ACCEPTANCE_URL}"
echo "cd web && vercel --prod --yes --scope constellate-dc388081"
echo "fly deploy --config fly.acceptance.toml"
echo "./prospect post-deploy-smoke --base-url ${ACCEPTANCE_URL}"
