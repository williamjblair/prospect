#!/usr/bin/env python3
"""Generic external producer client for the Prospect MCP connector."""
from __future__ import annotations

import argparse
import anyio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.receipt_bridge_client import McpClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from receipt.causal_bridge import claude_science_submission_request


def _remote_request(case: str) -> dict[str, Any]:
    if case == "claude_science":
        return claude_science_submission_request()
    return {
        "input_text": "VAV1",
        "filename": "external_claim.txt",
        "producer": "openresearch_style_bundle",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "explicit_driver_claim",
        "claim_context": {
            "cell_type": "primary human CD4+ T cells",
            "condition": "Stim48hr",
            "phenotype": "activation_transcriptome",
            "source": "generic external reproduction claim",
        },
        "publish_to_ledger": False,
    }


async def _remote_submit(url: str, case: str) -> tuple[str, dict[str, Any]]:
    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            submitted = await session.call_tool(
                "prospect.acceptance.submit_artifact",
                _remote_request(case),
            )
            if submitted.isError:
                raise RuntimeError("hosted connector rejected the external artifact")
            return initialized.serverInfo.name, submitted.structuredContent


def run(case: str, url: str = "") -> dict[str, Any]:
    if url:
        server, submit = anyio.run(_remote_submit, url, case)
    else:
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
        server = init["serverInfo"]["name"]
    producer = submit.get("producer") or (submit.get("receipt") or {}).get("producer", {}).get("name") or "external"
    return {
        "server": server,
        "transport": "streamable_http" if url else "stdio",
        "case": case,
        "producer": producer,
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
    parser.add_argument("--url", default="", help="official Streamable HTTP MCP endpoint")
    args = parser.parse_args(argv)
    summary = run(args.case, args.url)
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
