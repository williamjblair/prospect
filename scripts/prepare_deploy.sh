#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ACCEPTANCE_URL="${NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL:-https://<acceptance-service-host>}"
SIGNED_STATE=(
  frontier/nodes.jsonl
  frontier/edges.jsonl
  frontier/contradictions.jsonl
  frontier/open.jsonl
  frontier/findings.jsonl
  frontier/frontier.sig.json
)

state_digest() {
  python - "${SIGNED_STATE[@]}" <<'PY'
import hashlib
import pathlib
import sys

digest = hashlib.sha256()
for raw_path in sys.argv[1:]:
    path = pathlib.Path(raw_path)
    digest.update(raw_path.encode("ascii"))
    digest.update(b"\0")
    digest.update(path.read_bytes())
    digest.update(b"\0")
print(digest.hexdigest())
PY
}

SIGNED_STATE_BEFORE="$(state_digest)"

echo "Checking the immutable signed frontier"
./prospect verify

echo "Regenerating proposal and public data"
python receipt/emit.py
(cd web && python gen_data.py)

SIGNED_STATE_AFTER="$(state_digest)"
if [[ "$SIGNED_STATE_BEFORE" != "$SIGNED_STATE_AFTER" ]]; then
  echo "Refusing deployment preparation: signed frontier state changed" >&2
  exit 1
fi

echo "Running Prospect gate"
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
(cd web && npm run typecheck)
(cd web && npm run build)
docker build -f Dockerfile.acceptance -t prospect-acceptance:local .

echo ""
echo "Prepared. Will runs deploy commands:"
echo "export NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL=${ACCEPTANCE_URL}"
echo 'cd web && vercel --prod --yes --scope "$VERCEL_SCOPE"'
echo "fly deploy --config fly.acceptance.toml"
echo "./prospect post-deploy-smoke --base-url ${ACCEPTANCE_URL}"
