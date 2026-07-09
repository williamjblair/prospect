"""Deploy readiness helpers for Prospect."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

LOCAL_GATE = [
    "python frontier/build.py",
    "python frontier/verify.py",
    "python receipt/emit.py",
    "cd web && python gen_data.py",
    "./prospect verify",
    "python benchmark/mutation_pack.py",
    "python tests/test_skill_parity.py",
    "python tests/test_marson.py",
    "python -m pytest tests/ -q",
    "cd web && npm run build",
]

DEPLOY_COMMANDS = [
    "cd web && vercel --prod --yes --scope constellate-dc388081",
    "fly deploy --config fly.acceptance.toml",
]


def build_checklist() -> dict[str, Any]:
    return {
        "title": "Prospect deploy readiness checklist",
        "local_gate": LOCAL_GATE,
        "deploy_commands_for_will": DEPLOY_COMMANDS,
        "acceptance_service": {
            "container": "Dockerfile.acceptance",
            "fly_config": "fly.acceptance.toml",
            "health": "/health",
            "guide": "/guide",
            "ledger": "/ledger",
            "mcp": "/mcp",
            "env": [
                "PROSPECT_ACCEPTANCE_DATA_DIR",
                "PROSPECT_ACCEPTANCE_RATE_LIMIT",
                "PROSPECT_ACCEPTANCE_RATE_WINDOW",
                "PROSPECT_ACCEPTANCE_CORS_ORIGIN",
            ],
        },
        "web_env": {
            "NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL": "set to the hosted acceptance service base URL before web deploy",
        },
        "post_deploy_smoke": "./prospect post-deploy-smoke --base-url https://<acceptance-service-host>",
        "do_not_run_here": ["vercel --prod", "fly deploy"],
    }


def _run_command(command: str) -> None:
    print(f"$ {command}")
    subprocess.run(command, cwd=ROOT, shell=True, check=True)


def checklist_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect deploy-checklist")
    parser.add_argument("--json", action="store_true", help="emit checklist as JSON")
    parser.add_argument("--run", action="store_true", help="run local non-deploying gates before printing deploy commands")
    args = parser.parse_args(argv)
    checklist = build_checklist()
    if args.run:
        for command in LOCAL_GATE:
            _run_command(command)
    if args.json:
        print(json.dumps(checklist, indent=2, sort_keys=True))
    else:
        print(checklist["title"])
        print("")
        print("Local gate:")
        for command in checklist["local_gate"]:
            print(f"- {command}")
        print("")
        print("Will deploys:")
        for command in checklist["deploy_commands_for_will"]:
            print(f"- {command}")
        print("")
        print(f"Post-deploy smoke: {checklist['post_deploy_smoke']}")
    return 0


def _request(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, str]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {} if payload is None else {"content-type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            return int(res.status), res.read().decode()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode()


def post_deploy_smoke(base_url: str, *, source_name: str = "post_deploy_smoke") -> dict[str, Any]:
    base = base_url.rstrip("/")
    health_status, _ = _request("GET", f"{base}/health")
    submit_status, submit_text = _request("POST", f"{base}/submit", {
        "source_name": source_name,
        "filename": "post_deploy_genes.txt",
        "text": "IL7R\nCCR7\nPD-1\nNOTGENE",
    })
    if submit_status != 200:
        raise RuntimeError(f"submit failed with status {submit_status}: {submit_text[:200]}")
    result = json.loads(submit_text)
    state_url = result["state_url"]
    if state_url.startswith("/"):
        state_url = base + state_url
    state_status, state_page = _request("GET", state_url)
    ledger_status, ledger_text = _request("GET", f"{base}/ledger.json")
    time.sleep(0.2)
    second_state_status, _ = _request("GET", state_url)
    return {
        "base_url": base,
        "health_status": health_status,
        "submit_status": submit_status,
        "state_status": state_status,
        "second_state_status": second_state_status,
        "ledger_status": ledger_status,
        "state_url": state_url,
        "accepted": result["accepted"],
        "next": result["next"],
        "typed_status_counts": result["prospect"]["typed_status_counts"],
        "ledger_submission_count": json.loads(ledger_text)["submission_count"] if ledger_status == 200 else None,
        "state_page_has_ceiling": "Computation over released data" in state_page,
    }


def smoke_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect post-deploy-smoke")
    parser.add_argument("--base-url", required=True, help="hosted acceptance service base URL")
    parser.add_argument("--json", action="store_true", help="emit smoke result as JSON")
    args = parser.parse_args(argv)
    result = post_deploy_smoke(args.base_url)
    ok = (
        result["health_status"] == 200
        and result["submit_status"] == 200
        and result["state_status"] == 200
        and result["second_state_status"] == 200
        and result["ledger_status"] == 200
        and result["accepted"] is False
        and result["next"] == "human_signature_required"
        and result["state_page_has_ceiling"]
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Prospect post-deploy smoke")
        print(f"base_url: {result['base_url']}")
        print(f"state_url: {result['state_url']}")
        print(f"typed_status_counts: {result['typed_status_counts']}")
        print(f"accepted={str(result['accepted']).lower()}, next={result['next']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(checklist_main(sys.argv[1:]))
