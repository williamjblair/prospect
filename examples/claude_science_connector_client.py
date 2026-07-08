#!/usr/bin/env python3
"""Submit the real Claude Science export through the Prospect connector."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.receipt_bridge_client import McpClient


def run() -> dict[str, Any]:
    client = McpClient()
    try:
        init = client.call("initialize")
        tools_result = client.call("tools/list")
        schema = client.call(
            "tools/call",
            {"name": "prospect.receipt.schema", "arguments": {}},
        )["structuredContent"]
        submit = client.call(
            "tools/call",
            {
                "name": "prospect.receipt.submit_artifact",
                "arguments": {"bundle": {"case": "claude_science"}},
            },
        )["structuredContent"]
    finally:
        client.close()
    counts = submit["prospect"]["typed_status_counts"]
    return {
        "server": init["serverInfo"]["name"],
        "frontier_root": schema["manifest"]["frontier_root"],
        "tools": [tool["name"] for tool in tools_result["tools"]],
        "producer": submit["producer"],
        "real_export": submit["real_export"],
        "accepted": submit["accepted"],
        "next": submit["next"],
        "proposal_id": submit["proposal_id"],
        "receipt_id": submit["receipt"]["receipt_id"],
        "typed_status_counts": counts,
        "evidence_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "evidence_attached"
        ][:3],
        "contradiction_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "contradicted"
        ][:3],
        "not_assayed_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "not_assayed"
        ][:3],
        "session_caveat": submit["claude_science"]["session_caveat"],
        "ceiling": submit["prospect"]["ceiling"],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="examples/claude_science_connector_client.py")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args(argv)
    summary = run()
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print("Prospect Claude Science connector")
    print(f"frontier_root: {summary['frontier_root']}")
    print(f"producer: {summary['producer']}, real_export={str(summary['real_export']).lower()}")
    print(f"accepted={str(summary['accepted']).lower()}, next={summary['next']}")
    print("typed status counts:")
    for key, value in summary["typed_status_counts"].items():
        print(f"  {key}: {value}")
    print(f"receipt_id: {summary['receipt_id']}")


if __name__ == "__main__":
    main()
