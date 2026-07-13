# Reproducibility

Prospect's core science runs from a bare clone with no API key, no cloud access, and no large-file
download. Everything below was captured from a fresh clone on a clean machine, in a clean virtual
environment, at commit `6720a80`. The offline suite is frozen code over committed data, so the same
result holds on any machine.

## The exact steps

```bash
git clone https://github.com/williamjblair/prospect.git
cd prospect
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

Then the ten offline commands, each of which reads only committed inputs:

```bash
./prospect verify
./prospect reliability-benchmark
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python examples/claude_science_connector_client.py --json
python examples/receipt_bridge_client.py --json
./prospect claude-science
./prospect demo-mode --reset
python -m pytest tests/ -q
```

## What the fresh clone produced

| Command | Result |
|---|---|
| `./prospect verify` | `verified 53485 objects · 0 drift`, frontier root `root_a8b0dcdd4024e12f`, EXACT-lane PASS |
| `./prospect reliability-benchmark` | reproduces 46/96 = 47.9% [CI 38 to 58], famous 63.9% vs 7.0% (p 0.0001), calibration; rewrites the packet with no git diff |
| `python benchmark/mutation_pack.py` | `0` false admissions, clean recall `10/10`, PASS |
| `python tests/test_skill_parity.py` | PASS (skill mirrors the engine, 0 mismatch) |
| `python tests/test_marson.py` | PASS |
| `python examples/claude_science_connector_client.py --json` | PASS: the real 52-gene split over the stdio MCP, `accepted=false` |
| `python examples/receipt_bridge_client.py --json` | PASS: receipt bridge over the stdio MCP |
| `./prospect claude-science` | PASS: regenerates the Claude Science acceptance demo |
| `./prospect demo-mode --reset` | PASS: builds a shareable proposal packet, local sqlite only |
| `python -m pytest tests/ -q` | `221 passed` |

No command reaches S3, figshare, an API, or an environment secret. The connector clients spawn the
local `./prospect mcp` stdio server, which imports only the standard library and this repo. A fresh
clone auto-generates its own signing key, so the committed signed root is verified by re-derivation,
never re-signed.

## CI runs the same path

`.github/workflows/ci.yml` checks out a clean tree, installs `requirements.txt`, and runs
`./prospect verify`, `python benchmark/mutation_pack.py`, `python tests/test_skill_parity.py`,
`python tests/test_marson.py`, and `python -m pytest tests/ -q` (which exercises the connector and
demo-mode paths), plus the `web/` typecheck and build. The gate is the same bar a judge would hit
from a clone.
