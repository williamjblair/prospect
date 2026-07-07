"""MCP bridge tests for Prospect receipts.

The MCP surface is deliberately narrow: expose the receipt contract, validate a
receipt, and accept submissions only as proposals. It must not move accepted
state or claim that model activity becomes state by itself.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from receipt.mcp_server import handle_request


def test_mcp_lists_receipt_tools():
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    res = handle_request(req)
    tools = {t["name"]: t for t in res["result"]["tools"]}

    assert "prospect.receipt.schema" in tools
    assert "prospect.receipt.validate" in tools
    assert "prospect.receipt.submit" in tools
    assert tools["prospect.receipt.submit"]["inputSchema"]["required"] == ["receipt"]


def test_mcp_validate_and_submit_never_accepts_state():
    receipt = json.loads(open(os.path.join(ROOT, "receipts", "receipts.jsonl")).readline())
    validate_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "prospect.receipt.validate", "arguments": {"receipt": receipt}},
    }
    validate_res = handle_request(validate_req)

    assert validate_res["result"]["isError"] is False
    assert validate_res["result"]["structuredContent"]["valid"] is True

    submit_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "prospect.receipt.submit", "arguments": {"receipt": receipt}},
    }
    submit_res = handle_request(submit_req)

    assert submit_res["result"]["isError"] is False
    assert submit_res["result"]["structuredContent"]["accepted"] is False
    assert submit_res["result"]["structuredContent"]["next"] == "human_signature_required"


def test_prospect_mcp_stdio_roundtrip():
    payload = {"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {}}
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "mcp"],
        input=json.dumps(payload) + "\n",
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    res = json.loads(proc.stdout.strip())
    assert res["id"] == 4
    assert len(res["result"]["tools"]) == 3


if __name__ == "__main__":
    test_mcp_lists_receipt_tools()
    test_mcp_validate_and_submit_never_accepts_state()
    test_prospect_mcp_stdio_roundtrip()
    print("PASS: receipt MCP bridge")
