"""Lab writeback and contradiction receipt contract."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data" / "lab_writeback_receipt.json"
DOC = ROOT / "docs" / "LAB_WRITEBACK_RECEIPT.md"
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"
SCHEMA_DOC = ROOT / "docs" / "RECEIPT_SCHEMA.md"
SCHEMA_JSON = ROOT / "receipt" / "receipt_schema_v0.json"


def _packet() -> dict:
    return json.loads(DATA.read_text())


def test_lab_writeback_packet_specifies_same_shape_for_confirming_and_refuting_receipts():
    packet = _packet()

    assert packet["title"] == "Lab writeback receipt"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["receipt_kind"] == "lab_writeback"
    assert packet["return_shape_required"] == [
        "executed_protocol",
        "assay_readout",
        "affected_claims",
        "reviewer_signature",
        "state_diff",
    ]

    receipts = packet["return_receipts"]
    assert [r["outcome"] for r in receipts] == ["confirming", "refuting"]
    assert {r["typed_status"] for r in receipts} == {"independently_reanalyzed", "contradicted"}

    keyset = set(receipts[0])
    for receipt in receipts:
        assert set(receipt) == keyset
        assert receipt["accepted"] is False
        assert receipt["state_diff"]["model_can_apply"] is False
        assert receipt["state_diff"]["effect"] == "proposal_only_no_state_mutation"
        assert receipt["reviewer_signature"]["required"] is True
        assert receipt["reviewer_signature"]["present"] is False
        assert receipt["affected_claims"][0]["gene"] == "PGGT1B"


def test_later_contradiction_is_a_first_class_proposal_not_an_overwrite():
    packet = _packet()
    rule = packet["contradiction_rule"]

    assert rule["title"] == "Contradiction as proposal"
    assert rule["accepted_claim_mutation"] == "never_overwrite"
    assert rule["new_object"] == "receipt"
    assert rule["required_status"] == "contradicted"
    assert rule["accepted"] is False
    assert rule["next"] == "human_signature_required"


def test_lab_writeback_is_documented_and_exposed_to_web_data():
    doc = DOC.read_text()
    schema_doc = SCHEMA_DOC.read_text()
    schema = json.loads(SCHEMA_JSON.read_text())
    data = json.loads(FRONTIER.read_text())
    source = PAGE.read_text()

    for phrase in [
        "Lab writeback receipt",
        "executed_protocol",
        "assay_readout",
        "affected_claims",
        "reviewer_signature",
        "Contradiction as proposal",
        "never_overwrite",
    ]:
        assert phrase in doc
    for field in ["executed_protocol", "assay_readout", "affected_claims", "reviewer_signature"]:
        assert f"`{field}`" in schema_doc
        assert field in schema["properties"]

    assert data["lab_writeback_receipt"]["receipt_kind"] == "lab_writeback"
    assert "LabWritebackCard" in source
    assert "Contradiction as proposal" in source
    assert "never_overwrite" in source


def test_lab_writeback_cli_rebuilds_packet_without_accepting_state():
    proc = subprocess.run(
        [sys.executable, "-m", "receipt.writeback", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    assert "lab writeback receipt ok" in proc.stdout
    assert "accepted=false" in proc.stdout


if __name__ == "__main__":
    test_lab_writeback_packet_specifies_same_shape_for_confirming_and_refuting_receipts()
    test_later_contradiction_is_a_first_class_proposal_not_an_overwrite()
    test_lab_writeback_is_documented_and_exposed_to_web_data()
    test_lab_writeback_cli_rebuilds_packet_without_accepting_state()
    print("PASS: lab writeback")
