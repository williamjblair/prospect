#!/usr/bin/env python3
"""One-command HTTP service for Prospect acceptance checks."""
from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))

from receipt.acceptance_service import build_submission_result, clear_error
from receipt.causal_bridge import submit_bundle
from receipt.mcp_server import _tool_schema, _text_result

STATE: dict[str, dict[str, Any]] = {}


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, sort_keys=True).encode()
    handler.send_response(status)
    handler.send_header("content-type", "application/json")
    handler.send_header("content-length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, status: int, body: str) -> None:
    data = body.encode()
    handler.send_response(status)
    handler.send_header("content-type", "text/html; charset=utf-8")
    handler.send_header("content-length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _store_result(result: dict[str, Any]) -> dict[str, Any]:
    state_id = result.get("state_id")
    if not state_id:
        rid = ((result.get("receipt") or {}).get("receipt_id") or result.get("receipt_id") or "submission")
        state_id = "state_" + str(rid).replace("receipt_", "")[:24]
        result["state_id"] = state_id
        result["state_url"] = f"/state/{state_id}"
    STATE[state_id] = result
    return result


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("content-length", "0"))
    if length <= 0:
        return {}
    return json.loads(handler.rfile.read(length).decode())


def _render_state_page(result: dict[str, Any]) -> str:
    counts = result["prospect"]["typed_status_counts"]
    rows = "\n".join(
        f"<tr><td>{html.escape(v['gene'])}</td><td>{html.escape(v['typed_status'])}</td>"
        f"<td>{html.escape(v.get('condition') or '')}</td><td>{html.escape(str(v.get('n_total_de_genes')))}</td>"
        f"<td>{html.escape(v['reason'])}</td></tr>"
        for v in result["verdicts"][:200]
    )
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Prospect acceptance result</title>
<style>
body {{ font-family: ui-sans-serif, system-ui, sans-serif; max-width: 1040px; margin: 32px auto; padding: 0 18px; color: CanvasText; background: Canvas; }}
code, td:first-child {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0; }}
.chip {{ border: 1px solid ButtonBorder; border-radius: 6px; padding: 5px 8px; background: Field; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
th, td {{ border-top: 1px solid ButtonBorder; padding: 7px 8px; text-align: left; vertical-align: top; }}
</style></head>
<body>
<p><a href="/">Prospect</a></p>
<h1>Prospect acceptance result</h1>
<p>accepted=false. next=human_signature_required. Computation over released data, not wet-lab or clinical truth.</p>
<p>Receipt: <code>{html.escape(result['receipt']['receipt_id'])}</code></p>
<div class="chips">
<span class="chip">{counts['drivers']} drivers</span>
<span class="chip">{counts['passengers']} associative_only passengers</span>
<span class="chip">{counts['contradicted']} contradicted driver claims</span>
<span class="chip">{counts['not_assayed']} not_assayed</span>
</div>
<h2>Typed verdicts</h2>
<table><thead><tr><th>gene</th><th>status</th><th>condition</th><th>DE</th><th>reason</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""


def _mcp_response(req: dict[str, Any]) -> dict[str, Any]:
    method = req.get("method")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req.get("id"), "result": {"tools": _tool_schema()}}
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name != "prospect.receipt.submit_artifact":
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result({"accepted": False, "error": "unsupported HTTP tool"}, True)}
        bundle = args.get("bundle") or {}
        try:
            result = submit_bundle(bundle)
            _store_result(result)
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(result)}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(clear_error(exc), True)}
    return {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32601, "message": "method not found"}}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            _json_response(self, 200, {"ok": True})
            return
        if self.path.startswith("/state/"):
            state_id = self.path.rsplit("/", 1)[-1]
            result = STATE.get(state_id)
            if not result:
                _html_response(self, 404, "<h1>state not found</h1>")
                return
            _html_response(self, 200, _render_state_page(result))
            return
        _html_response(self, 200, "<h1>Prospect acceptance service</h1><p>POST /submit with text, filename, source_name.</p>")

    def do_POST(self) -> None:
        try:
            payload = _read_json(self)
            if self.path == "/submit":
                result = build_submission_result(
                    str(payload.get("text") or ""),
                    filename=str(payload.get("filename") or "submission.txt"),
                    source_name=str(payload.get("source_name") or "external"),
                )
                _store_result(result)
                _json_response(self, 200, result)
                return
            if self.path == "/mcp":
                _json_response(self, 200, _mcp_response(payload))
                return
            _json_response(self, 404, {"error": "unknown endpoint"})
        except Exception as exc:
            _json_response(self, 400, clear_error(exc))

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect acceptance service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8130)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Prospect acceptance service listening on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
