"""Real Claude Science export through the Prospect connector."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_CLIENT = ROOT / "examples" / "claude_science_connector_client.py"
GENERIC_CLIENT = ROOT / "examples" / "prospect_connector_client.py"
EXPORT = ROOT / "examples" / "data" / "claude_science_real_export"
FRONTIER_SIG = ROOT / "frontier" / "frontier.sig.json"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"


def _run_json(cmd):
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_real_claude_science_export_fixture_hashes_are_pinned():
    provenance = json.loads((EXPORT / "provenance.json").read_text())
    assert provenance["source"]["real_export"] is True
    assert provenance["source"]["fabricated"] is False
    assert provenance["claude_science_internal_review"]["status"] == "completed"
    assert "associative" in provenance["session_caveat"]
    expected = {row["name"]: row["sha256"] for row in provenance["artifacts"]}

    import hashlib

    for name, sha in expected.items():
        h = hashlib.sha256((EXPORT / name).read_bytes()).hexdigest()
        assert h == sha


def test_claude_science_connector_returns_two_typed_directions_and_no_state_write():
    before_sig = FRONTIER_SIG.read_text()
    before_receipts = RECEIPTS.read_text()

    summary = _run_json([sys.executable, str(CLAUDE_CLIENT), "--json"])

    assert summary["server"] == "prospect-receipts"
    assert summary["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert "prospect.receipt.submit_artifact" in summary["tools"]
    assert summary["producer"] == "claude_science"
    assert summary["real_export"] is True
    assert summary["accepted"] is False
    assert summary["next"] == "human_signature_required"
    assert summary["receipt_id"].startswith("rcpt_")
    assert summary["proposal_id"].startswith("proposal_")
    assert summary["typed_status_counts"] == {
        "genes": 52,
        "drivers": 12,
        "evidence_attached": 12,
        "passengers": 22,
        "associative_only": 22,
        "contradicted": 3,
        "not_assayed": 15,
    }
    assert {row["typed_status"] for row in summary["evidence_examples"]} == {"evidence_attached"}
    assert {row["typed_status"] for row in summary["contradiction_examples"]} == {"contradicted"}
    assert {row["gene"] for row in summary["contradiction_examples"]} == {"HAVCR2", "LAG3", "PDCD1"}
    assert {row["typed_status"] for row in summary["passenger_examples"]} == {"associative_only"}
    assert "Computation over released data" in summary["ceiling"]

    assert FRONTIER_SIG.read_text() == before_sig
    assert RECEIPTS.read_text() == before_receipts


def test_same_connector_accepts_second_external_producer_example():
    summary = _run_json([sys.executable, str(GENERIC_CLIENT), "--case", "openresearch", "--json"])

    assert summary["server"] == "prospect-receipts"
    assert summary["producer"] == "openresearch_style_bundle"
    assert summary["accepted"] is False
    assert summary["next"] == "human_signature_required"
    assert summary["typed_status_counts"] == {
        "genes": 1,
        "drivers": 1,
        "evidence_attached": 1,
        "passengers": 0,
        "associative_only": 0,
        "contradicted": 0,
        "not_assayed": 0,
    }
    assert summary["verdicts"][0]["gene"] == "VAV1"
    assert summary["verdicts"][0]["typed_status"] == "evidence_attached"
