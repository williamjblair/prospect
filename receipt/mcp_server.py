"""A tiny MCP-compatible stdio bridge for Prospect receipts.

This exposes Prospect's receipt boundary as tools an external workbench can
call. The submit tool returns a proposal result only. It never signs, mutates,
or moves accepted state.
"""
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

from receipt.bridge import contract, manifest, validate_receipt

PROTOCOL_VERSION = "2025-11-25"


def _text_result(payload: dict[str, Any], is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}],
        "structuredContent": payload,
        "isError": is_error,
    }


def _tool_schema() -> list[dict[str, Any]]:
    receipt_schema = {
        "type": "object",
        "properties": {"receipt": {"type": "object", "description": "A Prospect receipt object"}},
        "required": ["receipt"],
        "additionalProperties": False,
    }
    return [
        {
            "name": "prospect.receipt.schema",
            "title": "Prospect receipt contract",
            "description": "Return the Prospect receipt contract and current frontier manifest.",
            "inputSchema": {"type": "object", "additionalProperties": False},
        },
        {
            "name": "prospect.receipt.validate",
            "title": "Validate a Prospect receipt",
            "description": "Validate receipt shape, typed status, replay fields, and acceptance fields.",
            "inputSchema": receipt_schema,
        },
        {
            "name": "prospect.receipt.submit",
            "title": "Submit a receipt proposal",
            "description": "Submit a receipt as a proposal only. This never moves accepted state.",
            "inputSchema": receipt_schema,
        },
    ]


def _call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "prospect.receipt.schema":
        return _text_result({"contract": contract(), "manifest": manifest()})
    if name == "prospect.receipt.validate":
        receipt = args.get("receipt")
        errors = validate_receipt(receipt) if isinstance(receipt, dict) else ["receipt must be an object"]
        return _text_result({"valid": not errors, "errors": errors}, bool(errors))
    if name == "prospect.receipt.submit":
        receipt = args.get("receipt")
        errors = validate_receipt(receipt) if isinstance(receipt, dict) else ["receipt must be an object"]
        if errors:
            return _text_result({"accepted": False, "errors": errors}, True)
        rid = receipt.get("receipt_id", "")
        proposal_id = "proposal_" + hashlib.sha256(str(rid).encode()).hexdigest()[:16]
        return _text_result({
            "accepted": False,
            "proposal_id": proposal_id,
            "receipt_id": rid,
            "next": "human_signature_required",
            "reason": "MCP submission records a proposal only; Prospect accepted state requires the human signing path.",
        })
    return _text_result({"error": f"unknown tool: {name}"}, True)


def _response(req: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req.get("id"), "result": result}


def _error(req: dict[str, Any], code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": code, "message": message}}


def handle_request(req: dict[str, Any]) -> dict[str, Any] | None:
    method = req.get("method")
    if method == "initialize":
        return _response(req, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "prospect-receipts", "version": "0.1.0"},
        })
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return _response(req, {"tools": _tool_schema()})
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name", "")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            return _error(req, -32602, "arguments must be an object")
        return _response(req, _call_tool(name, args))
    return _error(req, -32601, f"method not found: {method}")


def serve(stdin=sys.stdin, stdout=sys.stdout) -> None:
    for line in stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
        except Exception as exc:
            req = {"id": None}
            res = _error(req, -32700, str(exc))
        if res is None:
            continue
        stdout.write(json.dumps(res, separators=(",", ":")) + "\n")
        stdout.flush()


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
