#!/usr/bin/env python3
"""One-command HTTP service for Prospect acceptance checks."""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

from receipt.acceptance_service import build_submission_result, clear_error
from receipt.causal_bridge import submit_bundle
from receipt.mcp_server import _tool_schema, _text_result

DEFAULT_DATA_DIR = ROOT / "var" / "acceptance_service"


class AcceptanceStore:
    """Disk-backed public proposal store for acceptance-service results."""

    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.states_dir = self.data_dir / "states"
        self._lock = threading.Lock()
        self.states_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, state_id: str) -> Path:
        safe = "".join(ch for ch in state_id if ch.isalnum() or ch in {"_", "-"})
        if not safe or safe != state_id:
            raise ValueError("invalid state id")
        return self.states_dir / f"{safe}.json"

    def store_result(self, result: dict[str, Any]) -> dict[str, Any]:
        state_id = result.get("state_id")
        if not state_id:
            rid = ((result.get("receipt") or {}).get("receipt_id") or result.get("receipt_id") or "submission")
            state_id = "state_" + str(rid).replace("receipt_", "")[:24]
            result["state_id"] = state_id
            result["state_url"] = f"/state/{state_id}"
        result.setdefault("state_url", f"/state/{state_id}")
        result["accepted"] = False
        result["next"] = "human_signature_required"
        path = self._state_path(str(state_id))
        tmp = path.with_suffix(".json.tmp")
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with self._lock:
            tmp.write_text(payload)
            tmp.replace(path)
        return result

    def get(self, state_id: str) -> dict[str, Any] | None:
        path = self._state_path(state_id)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def ledger(self) -> dict[str, Any]:
        status_counts: Counter[str] = Counter()
        by_producer: Counter[str] = Counter()
        recent: list[dict[str, Any]] = []
        for path in sorted(self.states_dir.glob("*.json")):
            try:
                result = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            counts = ((result.get("prospect") or {}).get("typed_status_counts") or {})
            for key in ["evidence_attached", "associative_only", "contradicted", "not_assayed"]:
                status_counts[key] += int(counts.get(key, 0) or 0)
            producer = (
                ((result.get("receipt") or {}).get("producer") or {}).get("name")
                or result.get("producer")
                or "external"
            )
            by_producer[str(producer)] += 1
            recent.append({
                "state_id": result.get("state_id"),
                "state_url": result.get("state_url"),
                "receipt_id": ((result.get("receipt") or {}).get("receipt_id")),
                "producer": producer,
                "accepted": False,
                "next": "human_signature_required",
                "typed_status_counts": counts,
            })
        return {
            "submission_count": len(recent),
            "accepted": False,
            "next": "human_signature_required",
            "typed_status_counts": dict(status_counts),
            "by_producer": dict(by_producer),
            "recent": recent[-50:],
        }


class RateLimiter:
    def __init__(self, limit: int = 0, window_seconds: float = 60):
        self.limit = max(0, limit)
        self.window_seconds = max(1.0, float(window_seconds))
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        if self.limit <= 0:
            return True
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = [stamp for stamp in self._hits.get(key, []) if stamp >= cutoff]
            if len(hits) >= self.limit:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


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


def _store(handler: BaseHTTPRequestHandler) -> AcceptanceStore:
    return handler.server.store  # type: ignore[attr-defined]


def _rate_limiter(handler: BaseHTTPRequestHandler) -> RateLimiter:
    return handler.server.rate_limiter  # type: ignore[attr-defined]


def _store_result(result: dict[str, Any], store: AcceptanceStore) -> dict[str, Any]:
    return store.store_result(result)


def _host_base_url(handler: BaseHTTPRequestHandler) -> str:
    host = handler.headers.get("host", "")
    if not host:
        return ""
    return f"http://{host}"


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


def _render_ledger_page(ledger: dict[str, Any]) -> str:
    rows = "\n".join(
        f"<tr><td><a href='{html.escape(item['state_url'])}'>{html.escape(str(item['state_id']))}</a></td>"
        f"<td>{html.escape(str(item['producer']))}</td>"
        f"<td>{html.escape(str((item.get('typed_status_counts') or {}).get('evidence_attached', 0)))}</td>"
        f"<td>{html.escape(str((item.get('typed_status_counts') or {}).get('associative_only', 0)))}</td>"
        f"<td>{html.escape(str((item.get('typed_status_counts') or {}).get('contradicted', 0)))}</td>"
        f"<td>{html.escape(str((item.get('typed_status_counts') or {}).get('not_assayed', 0)))}</td></tr>"
        for item in ledger["recent"]
    )
    counts = ledger["typed_status_counts"]
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Prospect acceptance ledger</title>
<style>
body {{ font-family: ui-sans-serif, system-ui, sans-serif; max-width: 1040px; margin: 32px auto; padding: 0 18px; color: CanvasText; background: Canvas; }}
code, td:first-child {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
th, td {{ border-top: 1px solid ButtonBorder; padding: 7px 8px; text-align: left; vertical-align: top; }}
</style></head>
<body>
<p><a href="/">Prospect</a></p>
<h1>Prospect acceptance ledger</h1>
<p>accepted=false for submitted proposals until frozen replay passes and a human signature accepts state.</p>
<p>{ledger['submission_count']} submissions. {counts.get('evidence_attached', 0)} evidence_attached, {counts.get('associative_only', 0)} associative_only, {counts.get('contradicted', 0)} contradicted, {counts.get('not_assayed', 0)} not_assayed.</p>
<table><thead><tr><th>state</th><th>producer</th><th>drivers</th><th>passengers</th><th>contradicted</th><th>not_assayed</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""


def _schema_payload() -> dict[str, Any]:
    return {
        "name": "Prospect acceptance receipt v0",
        "accepted_default": False,
        "next_steps": ["frozen_replay_passes", "reviewer_accepts_state_delta", "human_signature_required"],
        "input_shapes": ["signature_json", "de_csv", "ranked_markers", "plain_gene_list"],
        "typed_statuses": ["evidence_attached", "associative_only", "contradicted", "not_assayed"],
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        "tools": ["prospect.acceptance.submit_artifact", "prospect.acceptance.get_verdict"],
    }


def _acceptance_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "prospect.acceptance.discover_schema",
            "description": "Return the Prospect acceptance receipt shape and typed-status contract.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "prospect.acceptance.submit_artifact",
            "description": "Submit a gene list, signature JSON, or DE table and receive a typed driver/passenger verdict.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "filename": {"type": "string"},
                    "source_name": {"type": "string"},
                    "bundle": {"type": "object"},
                },
                "additionalProperties": True,
            },
        },
        {
            "name": "prospect.acceptance.get_verdict",
            "description": "Fetch a stored Prospect acceptance verdict by state_id.",
            "inputSchema": {
                "type": "object",
                "properties": {"state_id": {"type": "string"}},
                "required": ["state_id"],
                "additionalProperties": False,
            },
        },
        *_tool_schema(),
    ]


def _rate_limited_error() -> dict[str, Any]:
    return {
        "accepted": False,
        "error": "rate_limited",
        "next": "retry_later",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
    }


def _mcp_response(req: dict[str, Any], store: AcceptanceStore, rate_limiter: RateLimiter, client_key: str) -> dict[str, Any]:
    method = req.get("method")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "prospect_acceptance_service", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req.get("id"), "result": {"tools": _acceptance_tool_schema()}}
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "prospect.acceptance.discover_schema":
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(_schema_payload())}
        if name == "prospect.acceptance.get_verdict":
            result = store.get(str(args.get("state_id") or ""))
            if not result:
                return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result({"accepted": False, "error": "state_not_found"}, True)}
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(result)}
        if name not in {"prospect.acceptance.submit_artifact", "prospect.receipt.submit_artifact"}:
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result({"accepted": False, "error": "unsupported HTTP tool"}, True)}
        if not rate_limiter.allow(client_key):
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(_rate_limited_error(), True)}
        try:
            if name == "prospect.acceptance.submit_artifact":
                bundle = args.get("bundle") or {}
                if isinstance(args.get("text"), str):
                    result = build_submission_result(
                        args["text"],
                        filename=str(args.get("filename") or "submission.txt"),
                        source_name=str(args.get("source_name") or "external"),
                    )
                else:
                    result = submit_bundle(bundle)
            else:
                result = submit_bundle(args.get("bundle") or {})
            _store_result(result, store)
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(result)}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": req.get("id"), "result": _text_result(clear_error(exc), True)}
    return {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32601, "message": "method not found"}}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            _json_response(self, 200, {"ok": True})
            return
        if path == "/ledger.json":
            _json_response(self, 200, _store(self).ledger())
            return
        if path == "/ledger":
            _html_response(self, 200, _render_ledger_page(_store(self).ledger()))
            return
        if path.startswith("/state/"):
            state_id = path.rsplit("/", 1)[-1]
            if state_id.endswith(".json"):
                state_id = state_id[:-5]
                result = _store(self).get(state_id)
                if not result:
                    _json_response(self, 404, {"accepted": False, "error": "state_not_found"})
                    return
                _json_response(self, 200, result)
                return
            result = _store(self).get(state_id)
            if not result:
                _html_response(self, 404, "<h1>state not found</h1>")
                return
            _html_response(self, 200, _render_state_page(result))
            return
        _html_response(
            self,
            200,
            "<h1>Prospect acceptance service</h1><p>POST /submit with text, filename, source_name. Use /mcp for connector tools and /ledger for submitted proposal state.</p>",
        )

    def do_POST(self) -> None:
        try:
            payload = _read_json(self)
            path = urlparse(self.path).path
            if path == "/submit":
                if not _rate_limiter(self).allow(self.client_address[0]):
                    _json_response(self, 429, _rate_limited_error())
                    return
                result = build_submission_result(
                    str(payload.get("text") or ""),
                    filename=str(payload.get("filename") or "submission.txt"),
                    source_name=str(payload.get("source_name") or "external"),
                )
                _store_result(result, _store(self))
                _json_response(self, 200, result)
                return
            if path == "/mcp":
                _json_response(self, 200, _mcp_response(payload, _store(self), _rate_limiter(self), self.client_address[0]))
                return
            _json_response(self, 404, {"error": "unknown endpoint"})
        except Exception as exc:
            _json_response(self, 400, clear_error(exc))

    def log_message(self, fmt: str, *args: Any) -> None:
        event = {
            "remote": self.client_address[0],
            "method": self.command,
            "path": self.path,
            "message": fmt % args,
        }
        print(json.dumps(event, sort_keys=True), file=sys.stderr)


class AcceptanceHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        *,
        store: AcceptanceStore,
        rate_limiter: RateLimiter,
    ):
        super().__init__(server_address, handler_class)
        self.store = store
        self.rate_limiter = rate_limiter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect acceptance service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8130)
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("PROSPECT_ACCEPTANCE_DATA_DIR", str(DEFAULT_DATA_DIR)),
        help="directory for persisted public acceptance states",
    )
    parser.add_argument("--rate-limit", type=int, default=int(os.environ.get("PROSPECT_ACCEPTANCE_RATE_LIMIT", "0")))
    parser.add_argument("--rate-window", type=float, default=float(os.environ.get("PROSPECT_ACCEPTANCE_RATE_WINDOW", "60")))
    args = parser.parse_args(argv)
    server = AcceptanceHTTPServer(
        (args.host, args.port),
        Handler,
        store=AcceptanceStore(Path(args.data_dir)),
        rate_limiter=RateLimiter(args.rate_limit, args.rate_window),
    )
    print(f"Prospect acceptance service listening on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
