"""Receipt schema v0 documentation and emitter conformance."""
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RECEIPT_SCHEMA.md"
SCHEMA = ROOT / "receipt" / "receipt_schema_v0.json"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"


def _schema() -> dict:
    return json.loads(SCHEMA.read_text())


def _receipts(path: Path = RECEIPTS) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_receipt_schema_v0_is_written_and_names_the_boundary():
    schema = _schema()
    doc = DOC.read_text()

    assert schema["$id"] == "prospect.receipt.v0"
    assert schema["title"] == "Prospect Receipt v0"
    for field in [
        "claim",
        "evidence",
        "artifacts",
        "conditions",
        "verification_requirements",
        "state_diff",
        "submitter_identity",
        "replay_metadata",
        "status",
    ]:
        assert field in schema["required"]
        assert f"`{field}`" in doc
    assert "Activity < Receipt < Proposal < Review < Verification < Accepted < State" in doc
    assert "human_signature_required" in doc
    assert "verified" not in doc.lower()


def test_receipt_emitter_outputs_schema_v0_receipts_without_state_mutation(tmp_path):
    before = RECEIPTS.read_text()
    out_dir = tmp_path / "receipts"
    proc = subprocess.run(
        [sys.executable, "-m", "receipt.emit", "--no-bridge", "--out-dir", str(out_dir)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )
    assert proc.returncode == 0, proc.stderr

    schema = _schema()
    validator = Draft202012Validator(schema)
    receipts = _receipts(out_dir / "receipts.jsonl")
    assert len(receipts) >= 6
    for receipt in receipts:
        errors = sorted(validator.iter_errors(receipt), key=lambda err: list(err.path))
        assert not errors, "\n".join(error.message for error in errors)
        assert receipt["schema_version"] == "prospect.receipt.v0"
        assert receipt["status"] in schema["properties"]["status"]["enum"]
        assert receipt["state_diff"]["model_can_apply"] is False
        assert receipt["replay_metadata"]["command"]
    assert RECEIPTS.read_text() == before


if __name__ == "__main__":
    test_receipt_schema_v0_is_written_and_names_the_boundary()
    import tempfile
    test_receipt_emitter_outputs_schema_v0_receipts_without_state_mutation(Path(tempfile.mkdtemp()))
    print("PASS: receipt schema spec")
