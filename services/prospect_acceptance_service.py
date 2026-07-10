#!/usr/bin/env python3
"""Production HTTP and MCP service for Prospect proposal evaluation."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import threading
import time
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
import uvicorn

from receipt.acceptance_service import clear_error, evaluate_submission
from receipt.substrate_manifest import list_substrates

DEFAULT_DATA_DIR = ROOT / "var" / "acceptance_service"
DEFAULT_MAX_REQUEST_BYTES = 1_000_000
DEFAULT_MAX_GENES = 5_000
PROPOSAL_ID = re.compile(r"^proposal_[a-f0-9]{16}$")
CEILING = "Computation over released data, not wet-lab or clinical truth."
DATASETS = {
    "marson_cd4_activation": ROOT / "examples" / "data" / "marson_de_full.csv",
    "replogle_k562": ROOT / "examples" / "data" / "replogle_k562_de.csv",
    "replogle_rpe1": ROOT / "examples" / "data" / "replogle_rpe1_de.csv",
    "gse278572_manifest": ROOT / "examples" / "data" / "gse278572" / "source_manifest.json",
    "gse271788_manifest": ROOT / "examples" / "data" / "gse271788" / "source_manifest.json",
    "gse271788_target_reach": ROOT / "examples" / "data" / "gse271788" / "target_reach.csv",
}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SubmissionLimitError(ValueError):
    """Raised when a public submission exceeds a configured service limit."""


class AcceptanceStore:
    """SQLite store with immutable proposals and append-only event tables."""

    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "acceptance.sqlite3"
        self._lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id TEXT PRIMARY KEY,
                    receipt_id TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS submission_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL REFERENCES proposals(proposal_id),
                    producer TEXT NOT NULL,
                    producer_identity_status TEXT NOT NULL CHECK(producer_identity_status = 'self_declared'),
                    input_kind TEXT NOT NULL,
                    gene_count INTEGER NOT NULL,
                    warning_count INTEGER NOT NULL,
                    typed_status_counts_json TEXT NOT NULL,
                    published INTEGER NOT NULL CHECK(published IN (0, 1)),
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS submission_events_public
                    ON submission_events(published, event_id);
                CREATE TABLE IF NOT EXISTS acceptance_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL REFERENCES proposals(proposal_id),
                    receipt_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _validate_id(proposal_id: str) -> str:
        if not PROPOSAL_ID.fullmatch(proposal_id):
            raise ValueError("invalid proposal id")
        return proposal_id

    @staticmethod
    def _proposal_payload(result: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(result)
        payload["accepted"] = False
        payload["next"] = "human_signature_required"
        proposal_id = str(payload.get("proposal_id") or "")
        payload["proposal_url"] = f"/proposal/{proposal_id}"
        payload.pop("state_id", None)
        payload.pop("state_url", None)
        payload.pop("created_at", None)
        payload.pop("ledger_entry", None)
        payload.pop("submission_event_id", None)
        payload.pop("publish_to_ledger", None)
        payload.pop("published_to_ledger", None)
        return payload

    def store_result(
        self,
        result: dict[str, Any],
        *,
        publish_to_ledger: bool | None = None,
    ) -> dict[str, Any]:
        requested_publish = bool(result.get("publish_to_ledger", False))
        requested_url = str(result.get("proposal_url") or "")
        payload = self._proposal_payload(result)
        proposal_id = self._validate_id(str(payload.get("proposal_id") or ""))
        receipt_id = str((payload.get("receipt") or {}).get("receipt_id") or "")
        if not receipt_id:
            raise ValueError("proposal receipt_id is required")
        if payload.get("accepted") is not False:
            raise ValueError("public submissions must remain accepted=false")

        producer_record = (payload.get("receipt") or {}).get("producer") or {}
        producer = str(producer_record.get("name") or "external")
        producer_identity_status = str(producer_record.get("identity_status") or "self_declared")
        if producer_identity_status != "self_declared":
            raise ValueError("producer identity must be self_declared")
        normalized = payload.get("normalized_input") or {}
        counts = (payload.get("prospect") or {}).get("typed_status_counts") or {}
        published = requested_publish if publish_to_ledger is None else bool(publish_to_ledger)
        created_at = _utc_now()
        payload_json = _canonical_json(payload)

        with self._lock, self._connect() as connection:
            existing = connection.execute(
                "SELECT receipt_id, payload_json FROM proposals WHERE proposal_id = ?",
                (proposal_id,),
            ).fetchone()
            if existing:
                if existing["receipt_id"] != receipt_id or existing["payload_json"] != payload_json:
                    raise ValueError("proposal id already exists with different immutable content")
            else:
                connection.execute(
                    "INSERT INTO proposals(proposal_id, receipt_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                    (proposal_id, receipt_id, payload_json, created_at),
                )
            cursor = connection.execute(
                """
                INSERT INTO submission_events(
                    proposal_id, producer, producer_identity_status, input_kind,
                    gene_count, warning_count, typed_status_counts_json, published, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal_id,
                    producer,
                    producer_identity_status,
                    str(normalized.get("input_kind") or "unknown"),
                    int(normalized.get("unique_genes") or len(payload.get("verdicts") or [])),
                    len(payload.get("warnings") or []),
                    _canonical_json(counts),
                    1 if published else 0,
                    created_at,
                ),
            )
            event_id = int(cursor.lastrowid)

        response = deepcopy(payload)
        response["created_at"] = created_at
        response["submission_event_id"] = event_id
        response["published_to_ledger"] = published
        response["producer_identity_status"] = "self_declared"
        if requested_url.startswith(("http://", "https://")):
            response["proposal_url"] = requested_url
        return response

    def get(self, proposal_id: str) -> dict[str, Any] | None:
        proposal_id = self._validate_id(proposal_id)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json, created_at FROM proposals WHERE proposal_id = ?",
                (proposal_id,),
            ).fetchone()
        if not row:
            return None
        result = json.loads(row["payload_json"])
        result["created_at"] = row["created_at"]
        result["accepted"] = False
        result["next"] = "human_signature_required"
        return result

    def table_counts(self) -> dict[str, int]:
        with self._connect() as connection:
            return {
                table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("proposals", "submission_events", "acceptance_events")
            }

    def storage_status(self) -> dict[str, Any]:
        probe = self.data_dir / ".write_probe"
        try:
            probe.write_text("ok\n")
            probe.unlink()
            with self._connect() as connection:
                connection.execute("SELECT 1").fetchone()
            return {"writable": True, "database": self.db_path.name}
        except OSError as exc:
            return {"writable": False, "database": self.db_path.name, "error": str(exc)}

    def ledger(self) -> dict[str, Any]:
        status_counts: Counter[str] = Counter()
        by_producer: Counter[str] = Counter()
        recent: list[dict[str, Any]] = []
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT e.*, p.receipt_id
                FROM submission_events e
                JOIN proposals p USING(proposal_id)
                WHERE e.published = 1
                ORDER BY e.event_id ASC
                """
            ).fetchall()
            proposal_count = int(
                connection.execute(
                    "SELECT COUNT(DISTINCT proposal_id) FROM submission_events WHERE published = 1"
                ).fetchone()[0]
            )
            total_event_count = int(connection.execute("SELECT COUNT(*) FROM submission_events").fetchone()[0])

        for row in rows:
            counts = json.loads(row["typed_status_counts_json"])
            for key in ("evidence_attached", "associative_only", "contradicted", "not_assayed"):
                status_counts[key] += int(counts.get(key, 0) or 0)
            by_producer[row["producer"]] += 1
            recent.append(
                {
                    "event_id": row["event_id"],
                    "proposal_id": row["proposal_id"],
                    "proposal_url": f"/proposal/{row['proposal_id']}",
                    "receipt_id": row["receipt_id"],
                    "producer": row["producer"],
                    "producer_identity_status": row["producer_identity_status"],
                    "created_at": row["created_at"],
                    "input_kind": row["input_kind"],
                    "gene_count": row["gene_count"],
                    "warning_count": row["warning_count"],
                    "accepted": False,
                    "next": "human_signature_required",
                    "typed_status_counts": counts,
                }
            )
        typed_total = sum(status_counts.values())
        passenger_or_contradicted = status_counts["associative_only"] + status_counts["contradicted"]
        return {
            "submission_count": len(rows),
            "proposal_count": proposal_count,
            "total_event_count": total_event_count,
            "accepted": False,
            "next": "human_signature_required",
            "producer_identity": "self_declared",
            "typed_status_counts": dict(status_counts),
            "passenger_or_contradicted": {
                "count": passenger_or_contradicted,
                "denominator": typed_total,
                "rate": round(passenger_or_contradicted / typed_total, 4) if typed_total else 0,
            },
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


def _schema_payload() -> dict[str, Any]:
    return {
        "name": "Prospect receipt v1 acceptance service",
        "schema_version": "prospect.receipt.v1",
        "signed_root": "root_a8b0dcdd4024e12f",
        "accepted_default": False,
        "next": "human_signature_required",
        "producer_identity": "self_declared",
        "artifact_hash_policy": {
            "submitted_input": "service_computed",
            "frozen_substrate": "service_computed",
            "supplemental_descriptors": "self_declared_until_fetched",
        },
        "input_shapes": ["signature_json", "de_csv", "ranked_markers", "plain_gene_list"],
        "claim_modes": ["associative_signature", "explicit_driver_claim"],
        "evidence_modes": ["primary_only", "all_frozen"],
        "typed_statuses": ["evidence_attached", "associative_only", "contradicted", "not_assayed"],
        "substrates_path": "/substrates",
        "substrates": list_substrates(),
        "public_path": "/proposal/{proposal_id}",
        "ceiling": CEILING,
    }


def _normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    request = dict(payload.get("bundle") or {}) if isinstance(payload.get("bundle"), dict) else {}
    request.update({key: value for key, value in payload.items() if key != "bundle" and value is not None})
    if "input_text" not in request and "text" in request:
        request["input_text"] = request["text"]
    if "producer" not in request and "source_name" in request:
        request["producer"] = request["source_name"]
    request.setdefault("filename", "submission.txt")
    request.setdefault("producer", "external")
    request.setdefault("substrate_id", "marson_cd4_activation")
    request.setdefault("claim_mode", "associative_signature")
    request.setdefault("claim_context", {})
    request.setdefault("evidence_mode", "primary_only")
    request.setdefault("publish_to_ledger", False)
    return request


def _enforce_input_limits(request: dict[str, Any], max_request_bytes: int) -> None:
    text = str(request.get("input_text") or request.get("text") or "")
    if len(text.encode()) > max_request_bytes:
        raise SubmissionLimitError(f"submitted artifact exceeds {max_request_bytes} bytes")


def _evaluate_and_store(
    payload: dict[str, Any],
    *,
    store: AcceptanceStore,
    max_request_bytes: int,
    max_genes: int,
) -> dict[str, Any]:
    request = _normalize_request(payload)
    _enforce_input_limits(request, max_request_bytes)
    result = evaluate_submission(request)
    gene_count = int((result.get("normalized_input") or {}).get("unique_genes") or 0)
    if gene_count > max_genes:
        raise SubmissionLimitError(f"submission contains {gene_count} unique genes; maximum is {max_genes}")
    return store.store_result(result, publish_to_ledger=bool(request.get("publish_to_ledger", False)))


def _base_url(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    scheme = forwarded_proto if forwarded_proto in {"http", "https"} else request.url.scheme
    host = request.headers.get("x-forwarded-host", "").split(",", 1)[0].strip() or request.headers.get("host", "")
    return f"{scheme}://{host}" if host else ""


def _with_public_url(result: dict[str, Any], base_url: str) -> dict[str, Any]:
    public = deepcopy(result)
    path = f"/proposal/{public['proposal_id']}"
    public["proposal_url"] = base_url.rstrip("/") + path if base_url else path
    public["replay_command"] = f"python receipt/replay_proposal.py {public['proposal_url']}.json"
    public.pop("state_id", None)
    public.pop("state_url", None)
    public["accepted"] = False
    public["next"] = "human_signature_required"
    return public


def _error_payload(exc: Exception) -> dict[str, Any]:
    payload = clear_error(exc)
    payload["accepted"] = False
    payload["ceiling"] = CEILING
    return payload


def _render_proposal_page(result: dict[str, Any]) -> str:
    counts = (result.get("prospect") or {}).get("typed_status_counts") or {}
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('gene') or ''))}</td>"
        f"<td>{html.escape(str(row.get('typed_status') or ''))}</td>"
        f"<td>{html.escape(str(row.get('condition') or ''))}</td>"
        f"<td>{html.escape(str(row.get('n_total_de_genes') if row.get('n_total_de_genes') is not None else ''))}</td>"
        f"<td>{html.escape(str(row.get('reason') or ''))}</td>"
        "</tr>"
        for row in (result.get("verdicts") or [])[:500]
    )
    artifacts = "\n".join(
        f"<li><code>{html.escape(str(item.get('name') or 'artifact'))}</code>: <code>{html.escape(str(item.get('sha256') or ''))}</code></li>"
        for item in ((result.get("receipt") or {}).get("artifacts") or [])
    )
    dataset_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('gene') or ''))}</td>"
        f"<td>{html.escape(str(row.get('substrate_id') or ''))}</td>"
        f"<td>{html.escape(str(row.get('typed_status') or ''))}</td>"
        f"<td>{html.escape(str(row.get('comparability') or ''))}</td>"
        f"<td>{html.escape(str(row.get('magnitude') if row.get('magnitude') is not None else ''))}</td>"
        f"<td>{html.escape(str(row.get('reason') or ''))}</td>"
        "</tr>"
        for row in (result.get("dataset_verdicts") or [])[:3000]
    )
    receipt_id = str((result.get("receipt") or {}).get("receipt_id") or "")
    producer = ((result.get("receipt") or {}).get("producer") or {}).get("name") or "external"
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prospect proposal</title><style>
body {{ font-family: ui-sans-serif, system-ui, sans-serif; max-width: 1080px; margin: 32px auto; padding: 0 18px; color: CanvasText; background: Canvas; }}
code, td:first-child {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0; }}
.chip {{ border: 1px solid ButtonBorder; border-radius: 5px; padding: 5px 8px; background: Field; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
th, td {{ border-top: 1px solid ButtonBorder; padding: 7px 8px; text-align: left; vertical-align: top; }}
</style></head><body>
<p><a href="/">Prospect</a> | <a href="/ledger">Public ledger</a> | <a href="/guide">Submit a claim</a></p>
<h1>Prospect proposal</h1>
<p><strong>accepted=false</strong>. next=<code>human_signature_required</code>. {CEILING}</p>
<p>Proposal: <code>{html.escape(str(result.get('proposal_id') or ''))}</code><br>
Receipt: <code>{html.escape(receipt_id)}</code><br>
Producer: <code>{html.escape(str(producer))}</code>, identity: <code>self_declared</code></p>
<div class="chips">
<span class="chip">{int(counts.get('evidence_attached', 0))} evidence_attached</span>
<span class="chip">{int(counts.get('associative_only', 0))} associative_only</span>
<span class="chip">{int(counts.get('contradicted', 0))} contradicted</span>
<span class="chip">{int(counts.get('not_assayed', 0))} not_assayed</span>
</div>
<h2>Frozen replay</h2><p><code>{html.escape(str(result.get('replay_command') or ''))}</code></p>
<h2>Bound artifacts</h2>
<p>The submitted-input and registered frozen-substrate hashes are computed by Prospect. Producer-supplied external artifact descriptors remain self_declared until fetched during human review.</p>
<ul>{artifacts}</ul>
<h2>Per-dataset evidence</h2>
<p>Evidence mode: <code>{html.escape(str(result.get('evidence_mode') or 'primary_only'))}</code>. Supplemental rows retain their own comparability and never silently upgrade the primary verdict.</p>
<table><thead><tr><th>Gene</th><th>Substrate</th><th>Status</th><th>Comparability</th><th>Magnitude</th><th>Reason</th></tr></thead><tbody>{dataset_rows}</tbody></table>
<h2>Typed verdicts</h2>
<table><thead><tr><th>Gene</th><th>Status</th><th>Condition</th><th>DE genes</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""


def _render_ledger_page(ledger: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><a href='{html.escape(item['proposal_url'])}'>{html.escape(item['proposal_id'])}</a></td>"
        f"<td>{html.escape(item['producer'])}</td>"
        f"<td>{html.escape(item['input_kind'])}</td>"
        f"<td>{item['gene_count']}</td>"
        f"<td>{html.escape(str(item['typed_status_counts']))}</td>"
        "</tr>"
        for item in ledger["recent"]
    )
    aggregate = ledger["passenger_or_contradicted"]
    rate = round(float(aggregate["rate"]) * 100, 1)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prospect public proposal ledger</title></head><body style="font-family:ui-sans-serif,system-ui,sans-serif;max-width:1080px;margin:32px auto;padding:0 18px">
<p><a href="/">Prospect</a> | <a href="/guide">Submit a claim</a> | <a href="/ledger.json">JSON</a></p>
<h1>Public proposal ledger</h1>
<p>{ledger['submission_count']} published submission events across {ledger['proposal_count']} immutable proposals. Producer identity is self_declared.</p>
<p>{rate}% of typed genes are associative_only or contradicted in published submissions. Every proposal remains accepted=false and requires a human signature before accepted state.</p>
<table style="border-collapse:collapse;width:100%"><thead><tr><th>Proposal</th><th>Producer</th><th>Input</th><th>Genes</th><th>Typed counts</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""


def _render_guide_page(base_url: str) -> str:
    base = html.escape(base_url.rstrip("/") or "http://127.0.0.1:8130")
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Submit a biology claim to Prospect</title></head><body style="font-family:ui-sans-serif,system-ui,sans-serif;max-width:920px;margin:32px auto;padding:0 18px">
<p><a href="/">Prospect</a> | <a href="/ledger">Public ledger</a></p>
<h1>Submit a biology claim to Prospect</h1>
<p>Submit a gene list, signature JSON, ranked markers, or a DE table. Prospect returns typed evidence_attached, associative_only, contradicted, or not_assayed verdicts. {CEILING}</p>
<pre style="white-space:pre-wrap">curl -s {base}/submit \\
  -H 'content-type: application/json' \\
  -d '{{"producer":"your_team","filename":"genes.txt","input_text":"IL7R\\nCCR7\\nPD-1","claim_mode":"associative_signature","publish_to_ledger":false}}'</pre>
<p>The response includes an immutable <code>proposal_url</code>. Set <code>publish_to_ledger=true</code> only when the self_declared producer may appear in the public ledger.</p>
<p>Set <code>evidence_mode=all_frozen</code> to retain per-dataset evidence and comparability from every registered substrate.</p>
<p>Prospect computes the submitted-input and registered frozen-substrate hashes. Producer-supplied external artifact descriptors remain self_declared until fetched during review.</p>
<p>Remote MCP endpoint: <code>{base}/mcp</code>. Tools: <code>prospect.acceptance.discover_schema</code>, <code>prospect.acceptance.discover_substrates</code>, <code>prospect.acceptance.submit_artifact</code>, and <code>prospect.acceptance.get_proposal</code>.</p>
</body></html>"""


class RequestPolicyMiddleware:
    """Apply exact origin and request-size policy to HTTP and MCP traffic."""

    def __init__(self, app: Any, *, allowed_origins: list[str], max_request_bytes: int):
        self.app = app
        self.allowed_origins = set(allowed_origins)
        self.max_request_bytes = max_request_bytes

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        origin = headers.get("origin", "")
        if origin and origin not in self.allowed_origins:
            await JSONResponse({"accepted": False, "error": "origin_not_allowed"}, status_code=403)(scope, receive, send)
            return
        if scope.get("method") == "OPTIONS":
            response_headers = {
                "access-control-allow-methods": "GET, POST, OPTIONS",
                "access-control-allow-headers": "content-type, mcp-protocol-version, mcp-session-id",
                "vary": "Origin",
            }
            advertised_origin = origin
            if not advertised_origin and len(self.allowed_origins) == 1:
                advertised_origin = next(iter(self.allowed_origins))
            if advertised_origin:
                response_headers["access-control-allow-origin"] = advertised_origin
            await Response(status_code=204, headers=response_headers)(scope, receive, send)
            return
        try:
            content_length = int(headers.get("content-length", "0") or 0)
        except ValueError:
            content_length = self.max_request_bytes + 1
        if content_length > self.max_request_bytes:
            await JSONResponse(
                {"accepted": False, "error": "request_too_large", "maximum_bytes": self.max_request_bytes},
                status_code=413,
            )(scope, receive, send)
            return

        if scope.get("method") == "POST" and scope.get("path") == "/mcp":
            accept = headers.get("accept", "")
            if "application/json" not in accept or "text/event-stream" not in accept:
                forwarded_headers = [
                    (key, value) for key, value in scope.get("headers", []) if key.lower() != b"accept"
                ]
                forwarded_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = {**scope, "headers": forwarded_headers}

        async def send_with_cors(message: dict[str, Any]) -> None:
            advertised_origin = origin
            if not advertised_origin and len(self.allowed_origins) == 1:
                advertised_origin = next(iter(self.allowed_origins))
            if message.get("type") == "http.response.start" and advertised_origin:
                response_headers = list(message.get("headers", []))
                response_headers.extend(
                    [(b"access-control-allow-origin", advertised_origin.encode()), (b"vary", b"Origin")]
                )
                message["headers"] = response_headers
            await send(message)

        await self.app(scope, receive, send_with_cors)


def create_application(
    *,
    store: AcceptanceStore,
    rate_limiter: RateLimiter | None = None,
    cors_origins: list[str] | None = None,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    max_genes: int = DEFAULT_MAX_GENES,
    public_base_url: str = "",
) -> Any:
    limiter = rate_limiter or RateLimiter()
    public_base_url = public_base_url.rstrip("/")
    public_host = urlparse(public_base_url).netloc
    allowed_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    if public_host:
        allowed_hosts.append(public_host)
    data_hashes = {
        dataset_id: {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256_file(path) if path.exists() else None,
            "exists": path.exists(),
        }
        for dataset_id, path in DATASETS.items()
    }
    mcp = FastMCP(
        "prospect_acceptance_service",
        instructions="Type AI-generated biology claims against frozen released substrates. All outputs remain proposals.",
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
            allowed_origins=list(cors_origins or []),
        ),
    )

    def submit(
        *,
        bundle: dict[str, Any] | None = None,
        input_text: str = "",
        text: str = "",
        filename: str = "",
        producer: dict[str, Any] | str | None = None,
        source_name: str = "",
        substrate_id: str = "",
        claim_mode: str = "",
        claim_context: dict[str, Any] | None = None,
        evidence_mode: str = "",
        citations: list[str] | None = None,
        artifacts: list[dict[str, Any]] | None = None,
        publish_to_ledger: bool | None = None,
    ) -> dict[str, Any]:
        if not limiter.allow("mcp"):
            return {"accepted": False, "error": "rate_limited", "next": "retry_later", "ceiling": CEILING}
        payload: dict[str, Any] = dict(bundle or {})
        payload.update(
            {
                "input_text": input_text or text or payload.get("input_text") or payload.get("text") or "",
                "filename": filename or payload.get("filename") or "submission.txt",
                "producer": producer or source_name or payload.get("producer") or payload.get("source_name") or "external",
                "substrate_id": substrate_id or payload.get("substrate_id") or "marson_cd4_activation",
                "claim_mode": claim_mode or payload.get("claim_mode") or "associative_signature",
                "claim_context": claim_context if claim_context is not None else payload.get("claim_context") or {},
                "evidence_mode": evidence_mode or payload.get("evidence_mode") or "primary_only",
                "citations": citations if citations is not None else payload.get("citations") or [],
                "artifacts": artifacts if artifacts is not None else payload.get("artifacts") or [],
                "publish_to_ledger": (
                    publish_to_ledger
                    if publish_to_ledger is not None
                    else bool(payload.get("publish_to_ledger", False))
                ),
            }
        )
        try:
            result = _evaluate_and_store(
                payload,
                store=store,
                max_request_bytes=max_request_bytes,
                max_genes=max_genes,
            )
            return _with_public_url(result, public_base_url)
        except Exception as exc:
            return _error_payload(exc)

    @mcp.tool(
        name="prospect.acceptance.discover_schema",
        description="Return the receipt, claim-mode, typed-status, and proposal contract.",
        structured_output=True,
    )
    def discover_schema() -> dict[str, Any]:
        return _schema_payload()

    @mcp.tool(
        name="prospect.acceptance.discover_substrates",
        description="Return frozen substrate manifests, coverage, comparability, hashes, and replay commands.",
        structured_output=True,
    )
    def discover_substrates() -> dict[str, Any]:
        return {
            "accepted": False,
            "next": "human_signature_required",
            "substrates": list_substrates(),
            "ceiling": CEILING,
        }

    @mcp.tool(
        name="prospect.acceptance.submit_artifact",
        description="Submit a gene list, signature, ranked marker table, or DE table for frozen evaluation.",
        structured_output=True,
    )
    def submit_artifact(
        input_text: str = "",
        text: str = "",
        filename: str = "",
        producer: dict[str, Any] | str | None = None,
        source_name: str = "",
        substrate_id: str = "",
        claim_mode: str = "",
        claim_context: dict[str, Any] | None = None,
        evidence_mode: str = "",
        citations: list[str] | None = None,
        artifacts: list[dict[str, Any]] | None = None,
        publish_to_ledger: bool | None = None,
        bundle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return submit(
            bundle=bundle,
            input_text=input_text,
            text=text,
            filename=filename,
            producer=producer,
            source_name=source_name,
            substrate_id=substrate_id,
            claim_mode=claim_mode,
            claim_context=claim_context,
            evidence_mode=evidence_mode,
            citations=citations,
            artifacts=artifacts,
            publish_to_ledger=publish_to_ledger,
        )

    @mcp.tool(
        name="prospect.receipt.submit_artifact",
        description="Compatibility alias for prospect.acceptance.submit_artifact.",
        structured_output=True,
    )
    def receipt_submit_artifact(
        bundle: dict[str, Any] | None = None,
        text: str = "",
        filename: str = "",
        source_name: str = "",
        publish_to_ledger: bool | None = None,
    ) -> dict[str, Any]:
        return submit(
            bundle=bundle,
            text=text,
            filename=filename,
            source_name=source_name,
            publish_to_ledger=publish_to_ledger,
        )

    @mcp.tool(
        name="prospect.acceptance.get_proposal",
        description="Fetch one immutable proposal by proposal_id.",
        structured_output=True,
    )
    def get_proposal(proposal_id: str) -> dict[str, Any]:
        try:
            result = store.get(proposal_id)
        except ValueError as exc:
            return _error_payload(exc)
        if not result:
            return {"accepted": False, "error": "proposal_not_found", "next": "check_proposal_id", "ceiling": CEILING}
        return _with_public_url(result, public_base_url)

    @mcp.custom_route("/health", methods=["GET"])
    async def health(_request: Request) -> Response:
        storage = store.storage_status()
        healthy = storage["writable"] and all(item["exists"] for item in data_hashes.values())
        return JSONResponse(
            {
                "ok": healthy,
                "accepted": False,
                "signed_root": "root_a8b0dcdd4024e12f",
                "data_hashes": data_hashes,
                "storage": storage,
                "tables": store.table_counts(),
            },
            status_code=200 if healthy else 503,
        )

    @mcp.custom_route("/substrates", methods=["GET"])
    async def substrates(_request: Request) -> Response:
        return JSONResponse({
            "accepted": False,
            "next": "human_signature_required",
            "substrates": list_substrates(),
            "ceiling": CEILING,
        })

    @mcp.custom_route("/submit", methods=["POST"])
    async def submit_http(request: Request) -> Response:
        client = request.client.host if request.client else "unknown"
        if not limiter.allow(client):
            return JSONResponse(
                {"accepted": False, "error": "rate_limited", "next": "retry_later", "ceiling": CEILING},
                status_code=429,
            )
        try:
            body = await request.body()
            if len(body) > max_request_bytes:
                raise SubmissionLimitError(f"request exceeds {max_request_bytes} bytes")
            payload = json.loads(body or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("submission body must be a JSON object")
            result = _evaluate_and_store(
                payload,
                store=store,
                max_request_bytes=max_request_bytes,
                max_genes=max_genes,
            )
            return JSONResponse(_with_public_url(result, _base_url(request)))
        except SubmissionLimitError as exc:
            return JSONResponse(_error_payload(exc), status_code=413)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            return JSONResponse(_error_payload(exc), status_code=400)

    @mcp.custom_route("/proposal/{proposal_id}", methods=["GET"])
    async def proposal_page(request: Request) -> Response:
        proposal_id = request.path_params["proposal_id"]
        wants_json = proposal_id.endswith(".json")
        if wants_json:
            proposal_id = proposal_id[:-5]
        try:
            result = store.get(proposal_id)
        except ValueError:
            result = None
        if not result:
            if wants_json:
                return JSONResponse({"accepted": False, "error": "proposal_not_found"}, status_code=404)
            return HTMLResponse("<h1>proposal not found</h1>", status_code=404)
        if wants_json:
            return JSONResponse(_with_public_url(result, _base_url(request)))
        return HTMLResponse(_render_proposal_page(_with_public_url(result, _base_url(request))))

    @mcp.custom_route("/ledger.json", methods=["GET"])
    async def ledger_json(_request: Request) -> Response:
        return JSONResponse(store.ledger())

    @mcp.custom_route("/ledger", methods=["GET"])
    async def ledger_page(_request: Request) -> Response:
        return HTMLResponse(_render_ledger_page(store.ledger()))

    @mcp.custom_route("/guide", methods=["GET"])
    async def guide(request: Request) -> Response:
        return HTMLResponse(_render_guide_page(_base_url(request)))

    @mcp.custom_route("/", methods=["GET"])
    async def root(_request: Request) -> Response:
        return HTMLResponse(
            "<h1>Prospect acceptance service</h1><p>POST /submit, connect to /mcp, or read /guide. "
            "Every result is an immutable proposal with accepted=false.</p>"
        )

    app = mcp.streamable_http_app()
    return RequestPolicyMiddleware(
        app,
        allowed_origins=cors_origins or [],
        max_request_bytes=max_request_bytes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect acceptance service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8130)
    parser.add_argument("--data-dir", default=os.environ.get("PROSPECT_ACCEPTANCE_DATA_DIR", str(DEFAULT_DATA_DIR)))
    parser.add_argument("--rate-limit", type=int, default=int(os.environ.get("PROSPECT_ACCEPTANCE_RATE_LIMIT", "0")))
    parser.add_argument("--rate-window", type=float, default=float(os.environ.get("PROSPECT_ACCEPTANCE_RATE_WINDOW", "60")))
    parser.add_argument("--cors-origin", default=os.environ.get("PROSPECT_ACCEPTANCE_CORS_ORIGIN", ""))
    parser.add_argument("--max-request-bytes", type=int, default=int(os.environ.get("PROSPECT_ACCEPTANCE_MAX_REQUEST_BYTES", str(DEFAULT_MAX_REQUEST_BYTES))))
    parser.add_argument("--max-genes", type=int, default=int(os.environ.get("PROSPECT_ACCEPTANCE_MAX_GENES", str(DEFAULT_MAX_GENES))))
    parser.add_argument("--public-url", default=os.environ.get("PROSPECT_ACCEPTANCE_PUBLIC_URL", ""))
    args = parser.parse_args(argv)
    origins = [item.strip() for item in args.cors_origin.split(",") if item.strip()]
    public_url = args.public_url.rstrip("/")
    if not public_url:
        public_url = f"http://{args.host}:{args.port}"
    app = create_application(
        store=AcceptanceStore(args.data_dir),
        rate_limiter=RateLimiter(args.rate_limit, args.rate_window),
        cors_origins=origins,
        max_request_bytes=max(1, args.max_request_bytes),
        max_genes=max(1, args.max_genes),
        public_base_url=public_url,
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning", access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
