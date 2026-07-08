"""Gladstone assay operations bundle tests."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.assay_operations import build_assay_operations_bundle, write_assay_operations_bundle


def test_assay_operations_bundle_turns_lab_packet_into_operational_rows():
    bundle = build_assay_operations_bundle(limit=5)
    rows = bundle["candidates"]
    pg = rows[0]

    assert bundle["title"] == "Gladstone assay operations bundle"
    assert bundle["status"] == "evidence_attached"
    assert bundle["trust_boundary"] == "proposal_only"
    assert bundle["accepted_state_mutations"] == 0
    assert bundle["scope"] == "wet-lab planning, not accepted biological state"
    assert len(rows) == 5
    assert pg["gene"] == "PGGT1B"
    assert pg["queue"] == "primary_assay_queue"
    assert "orthogonal CRISPRi guide" in pg["assay_steps"][0]
    assert "activation-marker flow cytometry" in pg["readouts"]["primary"]
    assert "non-targeting guide" in pg["controls"]["negative"]
    assert "VAV1" in pg["controls"]["positive"]
    assert "stimulated program shift" in pg["expected_positive_result"]
    assert "Rest-only" in pg["weakening_result"]
    assert "failed on-target knockdown" in pg["rejection_result"]
    assert "orthogonal knockdown" in pg["missing_evidence_before_acceptance"]
    assert "/data/lab_packet.json" in pg["replay_links"]
    assert "/data/pggt1b_deep_dive.json" in pg["replay_links"]
    assert "verified" not in json.dumps(bundle).lower()
    assert "true" not in json.dumps(bundle).lower()


def test_assay_operations_bundle_rows_are_complete():
    bundle = build_assay_operations_bundle(limit=5)

    for row in bundle["candidates"]:
        assert row["status"] == "evidence_attached"
        assert row["trust_boundary"] == "proposal_only"
        assert row["intervention"] == "CRISPRi knockdown"
        assert len(row["assay_steps"]) >= 5
        assert len(row["decision_gates"]) >= 3
        assert row["expected_positive_result"]
        assert row["weakening_result"]
        assert row["rejection_result"]
        assert row["missing_evidence_before_acceptance"]
        assert "/data/frontier.json" in row["replay_links"]
        assert "/data/judge_packet.json" in row["replay_links"]


def test_assay_operations_bundle_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "assay_operations_bundle.json"
    out_csv = tmp_path / "assay_operations_bundle.csv"
    out_doc = tmp_path / "ASSAY_OPERATIONS_BUNDLE.md"

    write_assay_operations_bundle(out_json=out_json, out_csv=out_csv, out_doc=out_doc, limit=5)

    data = json.loads(out_json.read_text())
    csv_rows = list(csv.DictReader(out_csv.open()))
    doc = out_doc.read_text()
    assert data["candidates"][0]["gene"] == "PGGT1B"
    assert csv_rows[0]["gene"] == "PGGT1B"
    assert csv_rows[0]["queue"] == "primary_assay_queue"
    assert "Gladstone assay operations bundle" in doc
    assert "evidence_attached" in doc
    assert "proposal only" in doc
    assert "failed on-target knockdown" in doc


def test_assay_operations_bundle_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "assay-ops"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "assay_operations_bundle.json" in proc.stdout


if __name__ == "__main__":
    test_assay_operations_bundle_turns_lab_packet_into_operational_rows()
    test_assay_operations_bundle_rows_are_complete()
    test_assay_operations_bundle_writes_json_csv_and_markdown(Path("/tmp/prospect-assay-ops-test"))
    test_assay_operations_bundle_runs_from_prospect_cli()
    print("PASS: Gladstone assay operations bundle")
