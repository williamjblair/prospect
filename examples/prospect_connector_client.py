#!/usr/bin/env python3
"""Generic external producer client for the Prospect MCP connector."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.receipt_bridge_client import McpClient


def run(case: str) -> dict[str, Any]:
    client = McpClient()
    try:
        init = client.call("initialize")
        submit = client.call(
            "tools/call",
            {
                "name": "prospect.receipt.submit_artifact",
                "arguments": {"bundle": {"case": case}},
            },
        )["structuredContent"]
    finally:
        client.close()
    return {
        "server": init["serverInfo"]["name"],
        "case": case,
        "producer": submit["producer"],
        "accepted": submit["accepted"],
        "next": submit["next"],
        "proposal_id": submit["proposal_id"],
        "receipt_id": submit["receipt"]["receipt_id"],
        "typed_status_counts": submit["prospect"]["typed_status_counts"],
        "verdicts": submit["verdicts"],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="examples/prospect_connector_client.py")
    parser.add_argument("--case", choices=["claude_science", "openresearch"], default="openresearch")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args(argv)
    summary = run(args.case)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print("Prospect generic connector client")
    print(f"case: {summary['case']}")
    print(f"producer: {summary['producer']}")
    print(f"accepted={str(summary['accepted']).lower()}, next={summary['next']}")
    print(f"typed_status_counts: {summary['typed_status_counts']}")
    print(f"receipt_id: {summary['receipt_id']}")


if __name__ == "__main__":
    main()
