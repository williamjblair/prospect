#!/usr/bin/env python3
"""Run the Prospect receipt bridge from outside the verifier.

The client starts `./prospect mcp`, discovers the receipt tools, validates one
existing receipt, and submits it as a proposal. The server must return
`accepted: false`; accepted state still requires the human signing path.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "receipts" / "receipts.jsonl"


class McpClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [str(ROOT / "prospect"), "mcp"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._next_id = 1

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("MCP process pipes are unavailable")
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params or {},
        }
        self._next_id += 1
        self.proc.stdin.write(json.dumps(req, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError("MCP server closed without a response: " + stderr.strip())
        res = json.loads(line)
        if "error" in res:
            raise RuntimeError(res["error"]["message"])
        return res["result"]

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)


def _load_receipt(path: Path) -> dict[str, Any]:
    text = path.read_text().strip()
    if not text:
        raise SystemExit(f"receipt file is empty: {path}")
    first = text.splitlines()[0]
    data = json.loads(first)
    if isinstance(data, dict) and "receipts" in data:
        receipts = data["receipts"]
        if not receipts:
            raise SystemExit(f"receipt bundle has no receipts: {path}")
        return receipts[0]
    if not isinstance(data, dict):
        raise SystemExit(f"receipt must be a JSON object: {path}")
    return data


def run(receipt_path: Path = DEFAULT_RECEIPT) -> dict[str, Any]:
    receipt = _load_receipt(receipt_path)
    client = McpClient()
    try:
        init = client.call("initialize")
        tools_result = client.call("tools/list")
        schema = client.call(
            "tools/call",
            {"name": "prospect.receipt.schema", "arguments": {}},
        )["structuredContent"]
        validate = client.call(
            "tools/call",
            {"name": "prospect.receipt.validate", "arguments": {"receipt": receipt}},
        )["structuredContent"]
        submit = client.call(
            "tools/call",
            {"name": "prospect.receipt.submit", "arguments": {"receipt": receipt}},
        )["structuredContent"]
    finally:
        client.close()

    tools = [tool["name"] for tool in tools_result["tools"]]
    return {
        "server": init["serverInfo"]["name"],
        "frontier_root": schema["manifest"]["frontier_root"],
        "tools": tools,
        "receipt_id": receipt.get("receipt_id", ""),
        "valid": validate["valid"],
        "errors": validate["errors"],
        "accepted": submit["accepted"],
        "next": submit.get("next", ""),
        "proposal_id": submit.get("proposal_id", ""),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="examples/receipt_bridge_client.py")
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT), help="receipt JSON or JSONL path")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    args = parser.parse_args(argv)

    summary = run(Path(args.receipt))
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print("Prospect receipt bridge client")
    print(f"server: {summary['server']}")
    print(f"frontier_root: {summary['frontier_root']}")
    print("tools:")
    for tool in summary["tools"]:
        print(f"  {tool}")
    print(f"validate: valid={str(summary['valid']).lower()}, errors={len(summary['errors'])}")
    print(
        "submit: "
        f"accepted={str(summary['accepted']).lower()}, "
        f"next={summary['next']}, "
        f"proposal_id={summary['proposal_id']}"
    )


if __name__ == "__main__":
    main()
