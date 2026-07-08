"""External receipt bridge client demo contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "examples" / "receipt_bridge_client.py"
FRONTIER_SIG = ROOT / "frontier" / "frontier.sig.json"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"


def test_receipt_bridge_client_roundtrip_is_proposal_only():
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

    assert summary["server"] == "prospect-receipts"
    assert summary["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert summary["tools"] == [
        "prospect.receipt.schema",
        "prospect.receipt.validate",
        "prospect.receipt.submit",
        "prospect.receipt.submit_artifact",
    ]
    assert summary["valid"] is True
    assert summary["accepted"] is False
    assert summary["next"] == "human_signature_required"
    assert summary["receipt_id"].startswith("rcpt_")
    assert summary["proposal_id"].startswith("proposal_")

    assert FRONTIER_SIG.read_text() == before_sig
    assert RECEIPTS.read_text() == before_receipts


if __name__ == "__main__":
    test_receipt_bridge_client_roundtrip_is_proposal_only()
    print("PASS: receipt bridge client")
