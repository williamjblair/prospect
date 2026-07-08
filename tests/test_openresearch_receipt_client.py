"""External auto-research receipt adapter contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "examples" / "openresearch_receipt_client.py"
FRONTIER_SIG = ROOT / "frontier" / "frontier.sig.json"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"


def test_openresearch_client_submits_biology_proposal_only():
    before_sig = FRONTIER_SIG.read_text()
    before_receipts = RECEIPTS.read_text()

    proc = subprocess.run(
        [sys.executable, str(CLIENT), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)

    assert summary["producer"] == "external_auto_research"
    assert summary["domain"] == "biology"
    assert summary["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert summary["valid"] is True
    assert summary["errors"] == []
    assert summary["typed_status"] == "computationally_reproduced"
    assert summary["engine_verdict"] == "supported"
    assert summary["accepted"] is False
    assert summary["next"] == "human_signature_required"
    assert summary["human_acceptance_requires"] == [
        "frozen_replay_passes",
        "reviewer_accepts_state_delta",
        "human_ed25519_signature",
    ]
    assert summary["receipt_id"].startswith("rcpt_")
    assert summary["proposal_id"].startswith("proposal_")
    assert "VAV1" in summary["claim"]
    assert "python tests/test_marson.py" in summary["verifier_replay"]

    assert FRONTIER_SIG.read_text() == before_sig
    assert RECEIPTS.read_text() == before_receipts


if __name__ == "__main__":
    test_openresearch_client_submits_biology_proposal_only()
    print("PASS: external auto-research receipt client")
