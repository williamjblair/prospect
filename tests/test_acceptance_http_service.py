"""HTTP service contract for the Prospect acceptance layer."""
import http.client
import json
import socket
import subprocess
import time
from pathlib import Path

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


def test_http_submit_state_page_and_mcp_roundtrip():
    port = _free_port()
    proc = subprocess.Popen(
        [str(ROOT / "prospect"), "serve-acceptance", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        for _ in range(30):
            try:
                status, _ = _get(port, "/health")
                if status == 200:
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise AssertionError("service did not become ready")

        status, text = _post(port, "/submit", {
            "text": "IL7R\nCCR7\nPD-1\nNOTGENE",
            "filename": "genes.txt",
            "source_name": "external_team",
        })
        assert status == 200, text
        result = json.loads(text)
        assert result["accepted"] is False
        assert result["next"] == "human_signature_required"
        assert result["prospect"]["typed_status_counts"]["drivers"] == 1
        assert result["prospect"]["typed_status_counts"]["passengers"] == 1
        assert result["prospect"]["typed_status_counts"]["contradicted"] == 1
        assert result["prospect"]["typed_status_counts"]["not_assayed"] == 1

        status, page = _get(port, result["state_url"])
        assert status == 200
        assert "Prospect acceptance result" in page
        assert "accepted=false" in page
        assert "human_signature_required" in page
        assert "Computation over released data" in page

        status, mcp_text = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        })
        assert status == 200
        tools = json.loads(mcp_text)["result"]["tools"]
        assert "prospect.receipt.submit_artifact" in [tool["name"] for tool in tools]

        status, mcp_submit = _post(port, "/mcp", {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "prospect.receipt.submit_artifact",
                "arguments": {"bundle": {"text": "IL7R\nCCR7", "filename": "genes.txt"}},
            },
        })
        assert status == 200
        payload = json.loads(mcp_submit)["result"]["structuredContent"]
        assert payload["accepted"] is False
        assert payload["state_url"].startswith("/state/")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
