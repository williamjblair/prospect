"""Public robustness contracts for external Prospect submissions."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import socket
import subprocess
import time
from pathlib import Path

from cli.robustness_fuzz import build_report
from receipt.acceptance_service import clear_error
from services.prospect_acceptance_service import RateLimiter

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _post(port: int, path: str, payload: dict):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    body = json.dumps(payload)
    conn.request("POST", path, body=body, headers={"content-type": "application/json"})
    res = conn.getresponse()
    text = res.read().decode()
    conn.close()
    return res.status, text


def _get(port: int, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    res = conn.getresponse()
    text = res.read().decode()
    conn.close()
    return res.status, text


def _wait_ready(port: int) -> None:
    for _ in range(50):
        try:
            status, _ = _get(port, "/health")
            if status == 200:
                return
        except OSError:
            time.sleep(0.1)
    raise AssertionError("service did not become ready")


def _start_service(port: int, data_dir: Path, *extra: str) -> subprocess.Popen:
    proc = subprocess.Popen(
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
    _wait_ready(port)
    return proc


def _stop_service(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def test_public_robustness_fuzz_report_covers_messy_real_inputs():
    report = build_report()

    assert report["case_count"] >= 100
    assert report["typed_cases"] >= 90
    assert report["clean_failures"] >= 10
    assert report["crashes"] == 0
    assert report["silent_wrong_answers"] == 0
    assert report["accepted"] is False
    assert report["next"] == "human_signature_required"
    for class_name in [
        "plain_gene_list",
        "signature_json",
        "de_table",
        "ranked_markers",
        "mixed_identifier_mapping",
        "duplicates",
        "unknown_and_nonhuman",
        "injection_strings",
        "huge_list",
        "clean_failure",
    ]:
        assert class_name in report["classes"]
    assert report["typed_status_totals"]["evidence_attached"] > 0
    assert report["typed_status_totals"]["associative_only"] > 0
    assert report["typed_status_totals"]["contradicted"] > 0
    assert report["typed_status_totals"]["not_assayed"] > 0


def test_clear_error_hides_internal_details_for_missing_data_failure(monkeypatch):
    import receipt.acceptance_service as acceptance_service

    def missing_file(_path):
        raise FileNotFoundError("missing frozen Marson data")

    monkeypatch.setattr(acceptance_service, "sha256_file", missing_file)

    try:
        acceptance_service.build_submission_result("IL7R", filename="genes.txt")
    except Exception as exc:
        payload = clear_error(exc)

    assert payload["accepted"] is False
    assert payload["next"] == "fix_submission"
    assert "missing frozen Marson data" in payload["error"]
    assert "Traceback" not in json.dumps(payload)
    assert "ANTHROPIC_API_KEY" not in json.dumps(payload)
    assert "prospect_signing_key" not in json.dumps(payload)


def test_http_bad_submission_fails_cleanly_and_does_not_mutate_state(tmp_path):
    port = _free_port()
    proc = _start_service(port, tmp_path)
    try:
        status, text = _post(port, "/submit", {"text": "sample,score\nA,1\n", "filename": "bad.csv"})
        payload = json.loads(text)

        assert status == 400
        assert payload["accepted"] is False
        assert payload["next"] == "fix_submission"
        assert "table input needs" in payload["error"]

        status, ledger_text = _get(port, "/ledger.json")
        assert status == 200
        assert json.loads(ledger_text)["submission_count"] == 0
    finally:
        _stop_service(proc)


def test_http_share_page_escapes_injection_like_gene_text(tmp_path):
    port = _free_port()
    proc = _start_service(port, tmp_path)
    try:
        status, text = _post(
            port,
            "/submit",
            {
                "text": "gene,score\n<script>alert(1)</script>,1\nPD-1,2\n",
                "filename": "markers.csv",
                "source_name": "external_team",
            },
        )
        assert status == 200, text
        result = json.loads(text)
        proposal_path = "/" + result["proposal_url"].split("/", 3)[3]

        status, page = _get(port, proposal_path)
        assert status == 200
        assert "<script>alert(1)</script>" not in page
        assert "&lt;SCRIPT&gt;ALERT(1)&lt;/SCRIPT&gt;" in page
        assert "accepted=false" in page
    finally:
        _stop_service(proc)


def test_rate_limiter_holds_under_concurrent_burst():
    limiter = RateLimiter(limit=3, window_seconds=60)

    with ThreadPoolExecutor(max_workers=8) as pool:
        decisions = list(pool.map(lambda _idx: limiter.allow("public-client"), range(8)))

    assert sum(1 for allowed in decisions if allowed) == 3
    assert sum(1 for allowed in decisions if not allowed) == 5
