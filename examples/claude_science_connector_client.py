#!/usr/bin/env python3
"""Submit the real Claude Science export through the Prospect connector."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.receipt_bridge_client import McpClient
from receipt.causal_bridge import claude_science_submission_request

EXPORT = ROOT / "examples" / "data" / "claude_science_real_export"


async def _remote_call(url: str, request: dict[str, Any]) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    # mcp is only needed for the hosted (--url) path; importing it lazily keeps
    # the offline `--json` path working on a partial install (no mcp/anyio).
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            schema = await session.call_tool("prospect.acceptance.discover_schema", {})
            submitted = await session.call_tool(
                "prospect.acceptance.submit_artifact",
                request,
            )
            if submitted.isError:
                raise RuntimeError("hosted connector rejected the Claude Science artifact")
            return (
                {
                    "server": initialized.serverInfo.name,
                    "frontier_root": schema.structuredContent["signed_root"],
                },
                [tool.name for tool in tools.tools],
                submitted.structuredContent,
            )


def _write_capture(path: Path, *, url: str, request: dict[str, Any], response: dict[str, Any]) -> str:
    body = {
        "schema_version": "prospect.connector.run.v1",
        "capture_scope": "prospect_example_client_submission_of_real_claude_science_export",
        "originating_client": "examples/claude_science_connector_client.py",
        "originating_claude_science_ui_call": False,
        "transport": "streamable_http",
        "endpoint": url,
        "tool": "prospect.acceptance.submit_artifact",
        "request": request,
        "response": response,
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    capture_id = "connector_run_" + hashlib.sha256(encoded).hexdigest()[:16]
    payload = {"capture_id": capture_id, **body}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return capture_id


def run(url: str = "", capture_path: Path | None = None) -> dict[str, Any]:
    if url:
        import anyio

        request = claude_science_submission_request()
        init, tools, submit = anyio.run(_remote_call, url, request)
        server = init["server"]
        frontier_root = init["frontier_root"]
        capture_id = _write_capture(capture_path, url=url, request=request, response=submit) if capture_path else ""
    else:
        if capture_path:
            raise ValueError("--capture requires --url so the artifact records an official MCP call")
        client = McpClient()
        try:
            initialized = client.call("initialize")
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
        server = initialized["serverInfo"]["name"]
        frontier_root = schema["manifest"]["frontier_root"]
        tools = [tool["name"] for tool in tools_result["tools"]]
        capture_id = ""
    provenance = json.loads((EXPORT / "provenance.json").read_text())
    counts = submit["prospect"]["typed_status_counts"]
    return {
        "server": server,
        "transport": "streamable_http" if url else "stdio",
        "frontier_root": frontier_root,
        "tools": tools,
        "producer": "claude_science",
        "real_export": provenance["source"]["real_export"],
        "accepted": submit["accepted"],
        "next": submit["next"],
        "proposal_id": submit["proposal_id"],
        "receipt_id": submit["receipt"]["receipt_id"],
        "capture_id": capture_id,
        "typed_status_counts": counts,
        "evidence_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "evidence_attached"
        ][:3],
        "contradiction_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "contradicted"
        ][:3],
        "passenger_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "associative_only"
        ][:3],
        "not_assayed_examples": [
            v for v in submit["verdicts"] if v["typed_status"] == "not_assayed"
        ][:3],
        "session_caveat": provenance["session_caveat"],
        "ceiling": submit["prospect"]["ceiling"],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="examples/claude_science_connector_client.py")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--url", default="", help="official Streamable HTTP MCP endpoint")
    parser.add_argument("--capture", type=Path, help="write a content-addressed connector run artifact")
    args = parser.parse_args(argv)
    summary = run(args.url, args.capture)
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
