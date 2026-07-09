"""Official MCP SDK parity tests for the hosted acceptance connector."""
from __future__ import annotations

import http.client
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from receipt.acceptance_service import evaluate_submission
from receipt.causal_bridge import claude_science_submission_request
from examples.receipt_bridge_client import McpClient

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get(port: int, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.request("GET", path)
    response = connection.getresponse()
    text = response.read().decode()
    connection.close()
    return response.status, text


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    body = json.dumps(payload)
    connection.request("POST", path, body=body, headers={"content-type": "application/json"})
    response = connection.getresponse()
    text = response.read().decode()
    connection.close()
    return response.status, json.loads(text)


def _start(port: int, data_dir: Path) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            str(ROOT / "prospect"),
            "serve-acceptance",
            "--port",
            str(port),
            "--data-dir",
            str(data_dir),
            "--public-url",
            f"http://127.0.0.1:{port}",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for _ in range(60):
        try:
            if _get(port, "/health")[0] == 200:
                return process
        except OSError:
            pass
        time.sleep(0.1)
    process.terminate()
    stdout, stderr = process.communicate(timeout=5)
    raise AssertionError(f"service did not become ready\nstdout={stdout}\nstderr={stderr}")


def _stop(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _stdio_submit(request: dict) -> dict:
    bundle = {**request, "text": request["input_text"]}
    bundle.pop("input_text")
    client = McpClient()
    try:
        client.call("initialize")
        response = client.call(
            "tools/call",
            {
                "name": "prospect.receipt.submit_artifact",
                "arguments": {"bundle": bundle},
            },
        )
    finally:
        client.close()
    return response["structuredContent"]


async def _exercise_mcp(url: str, request: dict) -> dict:
    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            assert initialized.serverInfo.name == "prospect_acceptance_service"

            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert names == {
                "prospect.acceptance.discover_schema",
                "prospect.acceptance.submit_artifact",
                "prospect.acceptance.get_proposal",
                "prospect.receipt.submit_artifact",
            }

            schema = await session.call_tool("prospect.acceptance.discover_schema", {})
            assert schema.isError is False
            assert schema.structuredContent["schema_version"] == "prospect.receipt.v1"
            assert schema.structuredContent["accepted_default"] is False
            assert schema.structuredContent["artifact_hash_policy"] == {
                "submitted_input": "service_computed",
                "frozen_substrate": "service_computed",
                "supplemental_descriptors": "self_declared_until_fetched",
            }

            submitted = await session.call_tool("prospect.acceptance.submit_artifact", request)
            assert submitted.isError is False
            result = submitted.structuredContent
            assert result["accepted"] is False
            assert result["next"] == "human_signature_required"
            assert result["proposal_url"].startswith("http://")
            assert "state_url" not in result

            fetched = await session.call_tool(
                "prospect.acceptance.get_proposal",
                {"proposal_id": result["proposal_id"]},
            )
            assert fetched.isError is False
            assert fetched.structuredContent["proposal_id"] == result["proposal_id"]
            assert fetched.structuredContent["receipt"]["receipt_id"] == result["receipt"]["receipt_id"]
            return result


async def _exercise_alias(url: str, request: dict) -> dict:
    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "prospect.receipt.submit_artifact",
                {
                    "bundle": request,
                    "filename": request["filename"],
                    "source_name": request["producer"],
                },
            )
            assert result.isError is False
            return result.structuredContent


async def _exercise_alias_bundle(url: str, bundle: dict) -> dict:
    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "prospect.receipt.submit_artifact",
                {"bundle": bundle},
            )
            assert result.isError is False
            return result.structuredContent


def test_direct_http_and_official_mcp_return_identical_ids(tmp_path):
    port = _free_port()
    process = _start(port, tmp_path)
    request = {
        "input_text": "IL7R\nCCR7\nPD-1\nNOTGENE",
        "filename": "genes.txt",
        "producer": "external_team",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "publish_to_ledger": False,
    }
    try:
        direct = evaluate_submission(request)
        status, http_result = _post(port, "/submit", request)
        assert status == 200
        mcp_result = anyio.run(_exercise_mcp, f"http://127.0.0.1:{port}/mcp", request)
        alias_result = anyio.run(_exercise_alias, f"http://127.0.0.1:{port}/mcp", request)

        assert {
            direct["proposal_id"],
            http_result["proposal_id"],
            mcp_result["proposal_id"],
            alias_result["proposal_id"],
        } == {direct["proposal_id"]}
        assert {
            direct["receipt"]["receipt_id"],
            http_result["receipt"]["receipt_id"],
            mcp_result["receipt"]["receipt_id"],
            alias_result["receipt"]["receipt_id"],
        } == {direct["receipt"]["receipt_id"]}
        assert http_result["proposal_url"].startswith(f"http://127.0.0.1:{port}/proposal/")
        assert mcp_result["proposal_url"].startswith(f"http://127.0.0.1:{port}/proposal/")

        status, ledger = _get(port, "/ledger.json")
        assert status == 200
        parsed = json.loads(ledger)
        assert parsed["submission_count"] == 0
        assert parsed["total_event_count"] == 3
    finally:
        _stop(process)


def test_raw_mcp_post_without_accept_header_is_judge_friendly(tmp_path):
    port = _free_port()
    process = _start(port, tmp_path)
    try:
        status, payload = _post(
            port,
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "judge-curl", "version": "1"},
                },
            },
        )
        assert status == 200
        assert payload["result"]["serverInfo"]["name"] == "prospect_acceptance_service"
        assert payload["result"]["capabilities"]["tools"] == {"listChanged": False}
    finally:
        _stop(process)


def test_receipt_alias_preserves_bundle_metadata_and_ledger_opt_in(tmp_path):
    port = _free_port()
    process = _start(port, tmp_path)
    bundle = {
        "text": "VAV1",
        "filename": "external_result.txt",
        "producer": "openresearch_style_external_producer",
        "claim_mode": "associative_signature",
        "publish_to_ledger": True,
    }
    try:
        result = anyio.run(
            _exercise_alias_bundle,
            f"http://127.0.0.1:{port}/mcp",
            bundle,
        )
        assert result["accepted"] is False
        assert result["next"] == "human_signature_required"
        assert result["receipt"]["producer"]["name"] == bundle["producer"]
        assert result["normalized_input"]["input_kind"] == "gene_list"
        assert result["normalized_input"]["filename"] == bundle["filename"]

        status, ledger_text = _get(port, "/ledger.json")
        assert status == 200
        ledger = json.loads(ledger_text)
        assert ledger["submission_count"] == 1
        assert ledger["by_producer"] == {bundle["producer"]: 1}
        assert ledger["recent"][0]["proposal_id"] == result["proposal_id"]
    finally:
        _stop(process)


def test_real_claude_science_export_has_one_identity_across_all_transports(tmp_path):
    port = _free_port()
    process = _start(port, tmp_path)
    request = claude_science_submission_request()
    try:
        direct = evaluate_submission(request)
        status, http_result = _post(port, "/submit", request)
        assert status == 200
        remote_mcp = anyio.run(_exercise_mcp, f"http://127.0.0.1:{port}/mcp", request)
        stdio_mcp = _stdio_submit(request)

        proposal_ids = {
            direct["proposal_id"],
            http_result["proposal_id"],
            remote_mcp["proposal_id"],
            stdio_mcp["proposal_id"],
        }
        receipt_ids = {
            direct["receipt"]["receipt_id"],
            http_result["receipt"]["receipt_id"],
            remote_mcp["receipt"]["receipt_id"],
            stdio_mcp["receipt"]["receipt_id"],
        }
        assert proposal_ids == {"proposal_3d6906d35b270017"}
        assert receipt_ids == {"rcpt_7a2a6b4a3fae9084"}
        assert direct["prospect"]["typed_status_counts"] == {
            "genes": 52,
            "drivers": 12,
            "evidence_attached": 12,
            "passengers": 25,
            "associative_only": 25,
            "contradicted": 0,
            "not_assayed": 15,
        }
        assert {item["name"] for item in direct["receipt"]["artifacts"]} == {
            "signature_genes.json",
            "responder_DE_CD8.csv",
            "responder_DE_all.csv",
            "provenance.json",
            "marson_de_full.csv",
        }
    finally:
        _stop(process)


def test_judge_clients_use_official_hosted_connector_for_two_producers(tmp_path):
    port = _free_port()
    process = _start(port, tmp_path)
    url = f"http://127.0.0.1:{port}/mcp"
    capture_path = tmp_path / "claude_science_connector_run.json"
    try:
        claude = subprocess.run(
            [
                sys.executable,
                str(ROOT / "examples" / "claude_science_connector_client.py"),
                "--url",
                url,
                "--capture",
                str(capture_path),
                "--json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
        external = subprocess.run(
            [sys.executable, str(ROOT / "examples" / "prospect_connector_client.py"), "--case", "openresearch", "--url", url, "--json"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
        assert claude.returncode == 0, claude.stderr
        assert external.returncode == 0, external.stderr
        claude_result = json.loads(claude.stdout)
        external_result = json.loads(external.stdout)
        assert claude_result["transport"] == "streamable_http"
        assert claude_result["proposal_id"] == "proposal_3d6906d35b270017"
        assert claude_result["typed_status_counts"]["genes"] == 52
        capture = json.loads(capture_path.read_text())
        capture_body = {key: value for key, value in capture.items() if key != "capture_id"}
        expected_capture_id = "connector_run_" + __import__("hashlib").sha256(
            json.dumps(capture_body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        ).hexdigest()[:16]
        assert claude_result["capture_id"] == expected_capture_id == capture["capture_id"]
        assert capture["tool"] == "prospect.acceptance.submit_artifact"
        assert capture["originating_client"] == "examples/claude_science_connector_client.py"
        assert capture["originating_claude_science_ui_call"] is False
        assert capture["response"]["proposal_id"] == claude_result["proposal_id"]
        assert capture["response"]["accepted"] is False
        assert external_result["transport"] == "streamable_http"
        assert external_result["producer"] == "openresearch_style_bundle"
        assert external_result["typed_status_counts"]["evidence_attached"] == 1
        assert external_result["accepted"] is False
    finally:
        _stop(process)
