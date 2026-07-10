"""HTTP contracts for the production Prospect acceptance service."""
from __future__ import annotations

import http.client
import json
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request(
    port: int,
    method: str,
    path: str,
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, str, dict[str, str]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    body = json.dumps(payload) if payload is not None else None
    request_headers = dict(headers or {})
    if payload is not None:
        request_headers.setdefault("content-type", "application/json")
    connection.request(method, path, body=body, headers=request_headers)
    response = connection.getresponse()
    text = response.read().decode()
    response_headers = {key.lower(): value for key, value in response.getheaders()}
    connection.close()
    return response.status, text, response_headers


def _start_service(port: int, data_dir: Path, *extra: str) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            str(ROOT / "prospect"),
            "serve-acceptance",
            "--port",
            str(port),
            "--data-dir",
            str(data_dir),
            *extra,
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for _ in range(60):
        try:
            status, _, _ = _request(port, "GET", "/health")
            if status == 200:
                return process
        except OSError:
            pass
        time.sleep(0.1)
    process.terminate()
    stdout, stderr = process.communicate(timeout=5)
    raise AssertionError(f"service did not become ready\nstdout={stdout}\nstderr={stderr}")


def _stop_service(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def test_http_submit_returns_shareable_proposal(tmp_path):
    port = _free_port()
    process = _start_service(port, tmp_path)
    try:
        status, text, _ = _request(
            port,
            "POST",
            "/submit",
            {
                "input_text": "IL7R\nCCR7\nPD-1\nNOTGENE",
                "filename": "genes.txt",
                "producer": "external_team",
                "claim_mode": "associative_signature",
                "publish_to_ledger": True,
            },
            {"x-forwarded-proto": "https"},
        )
        assert status == 200, text
        result = json.loads(text)
        assert result["accepted"] is False
        assert result["next"] == "human_signature_required"
        assert result["proposal_id"].startswith("proposal_")
        assert result["proposal_url"].startswith(f"https://127.0.0.1:{port}/proposal/")
        assert "state_id" not in result
        assert "state_url" not in result
        assert result["producer_identity_status"] == "self_declared"
        assert result["prospect"]["typed_status_counts"] == {
            "genes": 4,
            "drivers": 1,
            "evidence_attached": 1,
            "passengers": 2,
            "associative_only": 2,
            "contradicted": 0,
            "not_assayed": 1,
        }

        path = urlparse(result["proposal_url"]).path
        status, page, _ = _request(
            port,
            "GET",
            path,
            headers={"x-forwarded-proto": "https"},
        )
        assert status == 200
        assert "Prospect proposal" in page
        assert "accepted=false" in page
        assert "human_signature_required" in page
        assert result["receipt"]["receipt_id"] in page
        assert result["replay_command"] in page
        assert "Bound artifacts" in page

        status, _, _ = _request(port, "GET", f"/proposal/{result['proposal_id']}.json")
        assert status == 200

        status, ledger_text, _ = _request(port, "GET", "/ledger.json")
        assert status == 200
        ledger = json.loads(ledger_text)
        assert ledger["submission_count"] == 1
        assert ledger["proposal_count"] == 1
        assert ledger["recent"][0]["proposal_id"] == result["proposal_id"]
        assert ledger["recent"][0]["producer"] == "external_team"
    finally:
        _stop_service(process)


def test_http_explicit_driver_claim_can_earn_contradicted(tmp_path):
    port = _free_port()
    process = _start_service(port, tmp_path)
    try:
        status, text, _ = _request(
            port,
            "POST",
            "/submit",
            {
                "input_text": "PD-1",
                "filename": "driver.txt",
                "producer": "review_team",
                "claim_mode": "explicit_driver_claim",
                "claim_context": {
                    "cell_type": "primary human CD4+ T cells",
                    "condition": "strongest",
                    "phenotype": "activation_transcriptome",
                    "source": "submitted causal claim",
                },
            },
        )
        assert status == 200, text
        result = json.loads(text)
        assert result["comparability"]["status"] == "comparable"
        assert result["verdicts"][0]["typed_status"] == "contradicted"
        assert result["accepted"] is False
    finally:
        _stop_service(process)


def test_health_reports_frozen_hashes_and_writable_sqlite(tmp_path):
    port = _free_port()
    process = _start_service(port, tmp_path)
    try:
        status, text, _ = _request(port, "GET", "/health")
        assert status == 200
        health = json.loads(text)
        assert health["ok"] is True
        assert health["accepted"] is False
        assert health["signed_root"] == "root_a8b0dcdd4024e12f"
        assert health["storage"]["writable"] is True
        assert health["tables"]["acceptance_events"] == 0
        assert set(health["data_hashes"]) == {
            "marson_cd4_activation",
            "replogle_k562",
            "replogle_rpe1",
            "gse278572_manifest",
            "gse271788_manifest",
            "gse271788_target_reach",
        }
        assert all(len(item["sha256"]) == 64 for item in health["data_hashes"].values())
    finally:
        _stop_service(process)


def test_request_gene_and_exact_origin_limits(tmp_path):
    port = _free_port()
    allowed = "https://prospect.example"
    process = _start_service(
        port,
        tmp_path,
        "--max-request-bytes",
        "300",
        "--max-genes",
        "2",
        "--cors-origin",
        allowed,
    )
    try:
        status, text, headers = _request(
            port,
            "POST",
            "/submit",
            {"input_text": "IL7R", "filename": "genes.txt"},
            {"origin": allowed},
        )
        assert status == 200, text
        assert headers["access-control-allow-origin"] == allowed

        status, _, headers = _request(port, "GET", "/health")
        assert status == 200
        assert headers["access-control-allow-origin"] == allowed

        status, _, headers = _request(port, "OPTIONS", "/submit")
        assert status == 204
        assert headers["access-control-allow-origin"] == allowed

        status, text, _ = _request(
            port,
            "POST",
            "/submit",
            {"input_text": "IL7R"},
            {"origin": "https://attacker.example"},
        )
        assert status == 403
        assert json.loads(text)["error"] == "origin_not_allowed"

        status, text, _ = _request(
            port,
            "POST",
            "/submit",
            {"input_text": "IL7R\nCCR7\nPD-1", "filename": "genes.txt"},
        )
        assert status == 413
        assert "maximum is 2" in json.loads(text)["error"]

        status, text, _ = _request(
            port,
            "POST",
            "/submit",
            {"input_text": "X" * 400, "filename": "genes.txt"},
        )
        assert status == 413
        assert json.loads(text)["error"] == "request_too_large"
    finally:
        _stop_service(process)
