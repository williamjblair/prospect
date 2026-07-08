"""Submit-smoke production endpoint checks."""
import json
import os
import subprocess
import sys
from urllib.error import HTTPError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cli.submit_pack import PUBLIC_ARTIFACTS
from cli.submit_smoke import run_checks


class FakeResponse:
    def __init__(self, body: str):
        self.body = body.encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def _opener(payloads):
    def open_url(url, timeout=0):
        path = "/" + url.split("/", 3)[3] if "://" in url else url
        if path not in payloads:
            raise HTTPError(url, 404, "missing fixture", hdrs=None, fp=None)
        body = payloads[path]
        if isinstance(body, str):
            return FakeResponse(body)
        return FakeResponse(json.dumps(body))
    return open_url


def _current_payloads():
    payloads = {
        "/": "<html><title>Prospect</title><body>Prospect</body></html>",
        "/data/judge_packet.json": {
            "frontier_root": "root_a8b0dcdd4024e12f",
            "gate_commands": [
                "./prospect final-check",
                "./prospect submit-smoke",
                "./prospect submit-pack",
                "./prospect demo-pack",
            ],
            "public_data": PUBLIC_ARTIFACTS,
            "receipt_bridge_demo": {"next": "human_signature_required"},
        },
        "/data/campaign_gate_probe.json": {
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "rows": [{}, {}, {}, {}],
        },
        "/data/campaign_pressure_summary.json": {
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "accepted_state_mutations": 0,
            "counts": {"claude_probe_rows": 8, "triage_rows": 4},
        },
        "/data/transfer_replay_packet.json": {
            "status": "computationally_reproduced",
            "accepted_state_mutation": "none",
            "counts": {"t_cell_regulators_compared": 377},
        },
        "/data/substrate_replay_packet.json": {
            "status": "computationally_reproduced",
            "accepted_state_mutation": "none",
            "counts": {"t_cell_regulators_compared": 377},
            "datasets": [{}, {}, {}],
        },
        "/data/lab_packet.json": {
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "candidates": [{}, {}, {}, {}, {}],
        },
        "/data/receipt_bridge/receipt_manifest.json": {
            "frontier_root": "root_a8b0dcdd4024e12f",
            "receipt_count": 6,
            "mcp_command": "./prospect mcp",
        },
    }
    for artifact in PUBLIC_ARTIFACTS:
        payloads.setdefault(artifact, {"artifact": artifact})
    return payloads


def test_submit_smoke_accepts_current_public_payload_shapes():
    payloads = _current_payloads()

    result = run_checks("https://example.test", opener=_opener(payloads))

    assert result.ok is True
    assert len(result.checks) == 9
    assert any(check.name == "judge packet" for check in result.checks)
    assert any(
        check.name == "public artifacts" and check.detail == f"{len(PUBLIC_ARTIFACTS)} public artifacts reachable"
        for check in result.checks
    )


def test_submit_smoke_rejects_missing_public_artifact():
    payloads = _current_payloads()
    payloads.pop("/data/agent_campaign.json")

    result = run_checks("https://example.test", opener=_opener(payloads))

    assert result.ok is False
    assert any(
        check.name == "public artifacts" and "missing /data/agent_campaign.json" in check.detail
        for check in result.checks
        if not check.ok
    )


def test_submit_smoke_rejects_judge_public_data_drift():
    payloads = _current_payloads()
    payloads["/data/judge_packet.json"] = {
        **payloads["/data/judge_packet.json"],
        "public_data": [path for path in PUBLIC_ARTIFACTS if path != "/data/lab_packet.json"],
    }

    result = run_checks("https://example.test", opener=_opener(payloads))

    assert result.ok is False
    assert any(
        check.name == "judge packet" and "public data drift" in check.detail
        for check in result.checks
        if not check.ok
    )


def test_submit_smoke_rejects_wrong_frontier_root():
    payloads = {
        "/": "<html><body>Prospect</body></html>",
        "/data/judge_packet.json": {
            "frontier_root": "root_bad",
            "gate_commands": ["./prospect final-check"],
            "public_data": ["/data/transfer_replay_packet.json"],
        },
    }

    result = run_checks("https://example.test", opener=_opener(payloads))

    assert result.ok is False
    assert any("frontier root" in check.detail for check in result.checks if not check.ok)


def test_submit_smoke_rejects_stale_judge_gate_commands():
    payloads = {
        "/": "<html><body>Prospect</body></html>",
        "/data/judge_packet.json": {
            "frontier_root": "root_a8b0dcdd4024e12f",
            "gate_commands": ["./prospect final-check"],
            "public_data": ["/data/transfer_replay_packet.json"],
        },
    }

    result = run_checks("https://example.test", opener=_opener(payloads))

    assert result.ok is False
    assert any("missing demo-pack gate" in check.detail for check in result.checks if not check.ok)


def test_submit_smoke_cli_is_discoverable():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submit-smoke", "--help"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "production submission smoke" in proc.stdout
    assert "--base-url" in proc.stdout


if __name__ == "__main__":
    test_submit_smoke_accepts_current_public_payload_shapes()
    test_submit_smoke_rejects_missing_public_artifact()
    test_submit_smoke_rejects_judge_public_data_drift()
    test_submit_smoke_rejects_wrong_frontier_root()
    test_submit_smoke_rejects_stale_judge_gate_commands()
    test_submit_smoke_cli_is_discoverable()
    print("PASS: submit smoke")
