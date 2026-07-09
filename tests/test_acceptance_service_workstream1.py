"""Production acceptance service contracts."""
import http.client
import json
import socket
import subprocess
import time
from pathlib import Path

from receipt.acceptance_service import build_submission_result
from services.prospect_acceptance_service import AcceptanceStore

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
    for _ in range(40):
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


def test_acceptance_store_persists_states_and_public_ledger(tmp_path):
    store = AcceptanceStore(tmp_path)
    result = build_submission_result("IL7R\nCCR7\nPD-1", filename="genes.txt", source_name="external_team")

    stored = store.store_result(result)
    reloaded = AcceptanceStore(tmp_path).get(stored["state_id"])
    ledger = AcceptanceStore(tmp_path).ledger()

    assert reloaded["state_id"] == stored["state_id"]
    assert reloaded["accepted"] is False
    assert reloaded["next"] == "human_signature_required"
    assert ledger["submission_count"] == 1
    assert ledger["by_producer"]["external_team"] == 1
    assert ledger["typed_status_counts"]["evidence_attached"] == 1
    assert ledger["typed_status_counts"]["associative_only"] == 1
    assert ledger["typed_status_counts"]["contradicted"] == 1
    assert ledger["recent"][0]["producer"] == "external_team"
    assert ledger["recent"][0]["input_kind"] == "gene_list"
    assert ledger["recent"][0]["gene_count"] == 3
    assert reloaded["ledger_entry"]["next"] == "human_signature_required"


def test_http_state_survives_restart_and_ledger_is_shareable(tmp_path):
    port = _free_port()
    proc = _start_service(port, tmp_path)
    try:
        status, text = _post(port, "/submit", {
            "text": "IL7R\nCCR7\nPD-1\nNOTGENE",
            "filename": "genes.txt",
            "source_name": "external_team",
        })
        assert status == 200, text
        result = json.loads(text)
        state_url = result["state_url"]
        assert state_url.startswith(f"http://127.0.0.1:{port}/state/")
    finally:
        _stop_service(proc)

    proc = _start_service(port, tmp_path)
    try:
        state_path = "/" + state_url.split("/", 3)[3]
        status, page = _get(port, state_path)
        assert status == 200
        assert "Prospect acceptance result" in page
        assert "accepted=false" in page
        assert "human_signature_required" in page
        assert "Producer: <code>external_team</code>" in page

        status, ledger_text = _get(port, "/ledger.json")
        assert status == 200
        ledger = json.loads(ledger_text)
        assert ledger["submission_count"] == 1
        assert ledger["typed_status_counts"]["not_assayed"] == 1
        assert ledger["recent"][0]["state_url"] == state_url
        assert ledger["recent"][0]["producer"] == "external_team"

        status, ledger_page = _get(port, "/ledger")
        assert status == 200
        assert "Prospect acceptance ledger" in ledger_page
        assert "Recent submissions" in ledger_page
        assert "external_team" in ledger_page
        assert "not_assayed" in ledger_page

        status, guide_page = _get(port, "/guide")
        assert status == 200
        assert "Run your own claim through Prospect" in guide_page
        assert f"http://127.0.0.1:{port}/submit" in guide_page
        assert "prospect.acceptance.submit_artifact" in guide_page
    finally:
        _stop_service(proc)


def test_http_mcp_acceptance_tools_discover_submit_and_fetch_verdict(tmp_path):
    port = _free_port()
    proc = _start_service(port, tmp_path)
    try:
        status, init_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert status == 200
        initialized = json.loads(init_text)["result"]
        assert initialized["serverInfo"]["name"] == "prospect_acceptance_service"
        assert initialized["capabilities"]["tools"] == {}

        status, list_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        assert status == 200
        names = [tool["name"] for tool in json.loads(list_text)["result"]["tools"]]
        assert "prospect.acceptance.discover_schema" in names
        assert "prospect.acceptance.submit_artifact" in names
        assert "prospect.acceptance.get_verdict" in names

        status, schema_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "prospect.acceptance.discover_schema", "arguments": {}},
        })
        assert status == 200
        schema_payload = json.loads(schema_text)["result"]["structuredContent"]
        assert schema_payload["accepted_default"] is False
        assert "human_signature_required" in schema_payload["next_steps"]

        status, submit_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "prospect.acceptance.submit_artifact",
                "arguments": {
                    "text": "IL7R\nCCR7\nPD-1\nNOTGENE",
                    "filename": "genes.txt",
                    "source_name": "external_team",
                },
            },
        })
        assert status == 200
        submitted = json.loads(submit_text)["result"]["structuredContent"]
        assert submitted["accepted"] is False
        assert submitted["next"] == "human_signature_required"

        status, verdict_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "prospect.acceptance.get_verdict",
                "arguments": {"state_id": submitted["state_id"]},
            },
        })
        assert status == 200
        fetched = json.loads(verdict_text)["result"]["structuredContent"]
        assert fetched["state_id"] == submitted["state_id"]
        assert fetched["prospect"]["typed_status_counts"]["genes"] == 4
    finally:
        _stop_service(proc)


def test_http_service_rate_limits_submissions_without_state_mutation(tmp_path):
    port = _free_port()
    proc = _start_service(port, tmp_path, "--rate-limit", "2", "--rate-window", "60")
    try:
        for gene in ["IL7R", "CCR7"]:
            status, text = _post(port, "/submit", {"text": gene, "filename": "genes.txt"})
            assert status == 200, text
        status, text = _post(port, "/submit", {"text": "PD-1", "filename": "genes.txt"})
        assert status == 429
        payload = json.loads(text)
        assert payload["accepted"] is False
        assert payload["error"] == "rate_limited"
        assert payload["next"] == "retry_later"

        status, ledger_text = _get(port, "/ledger.json")
        assert status == 200
        assert json.loads(ledger_text)["submission_count"] == 2
    finally:
        _stop_service(proc)


def test_identifier_aliases_and_messy_inputs_type_honestly():
    result = build_submission_result(
        "symbol,score\nCD127,1.0\nIL-7R,0.9\nPD-L1,0.2\nENSMUSG00000000001,0.1\n",
        filename="markers.csv",
        source_name="messy_team",
    )

    genes = [row["gene"] for row in result["normalized_input"]["genes"]]
    statuses = {row["gene"]: row["typed_status"] for row in result["verdicts"]}

    assert genes == ["IL7R", "CD274", "ENSMUSG00000000001"]
    assert result["normalized_input"]["submitted_items"] == 4
    assert any("duplicate gene ignored: IL7R" in warning for warning in result["warnings"])
    assert statuses["IL7R"] == "evidence_attached"
    assert statuses["ENSMUSG00000000001"] == "not_assayed"


def test_acceptance_service_container_files_are_present():
    dockerfile = ROOT / "Dockerfile.acceptance"
    fly_config = ROOT / "fly.acceptance.toml"

    assert dockerfile.exists()
    assert "PROSPECT_ACCEPTANCE_DATA_DIR" in dockerfile.read_text()
    assert "PROSPECT_ACCEPTANCE_CORS_ORIGIN" in dockerfile.read_text()
    assert "/health" in dockerfile.read_text()
    assert fly_config.exists()
    assert "internal_port = 8130" in fly_config.read_text()
    assert "PROSPECT_ACCEPTANCE_CORS_ORIGIN" in fly_config.read_text()
    assert "/health" in fly_config.read_text()
