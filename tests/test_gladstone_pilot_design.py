"""Gladstone pilot design artifact tests."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gladstone_pilot_design import build_pilot_design, write_pilot_design


def test_pilot_design_turns_assay_ops_into_bench_plan():
    packet = build_pilot_design()
    pg = packet["candidates"][0]

    assert packet["title"] == "Gladstone pilot design"
    assert packet["status"] == "evidence_attached"
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["accepted_state_mutations"] == 0
    assert packet["model_in_trust_path"] == "no"
    assert packet["source_artifact"] == "examples/data/assay_operations_bundle.json"
    assert packet["sample_plan"]["sample"] == "primary human CD4+ T cells"
    assert packet["sample_plan"]["donor_replicates"] == 3
    assert packet["sample_plan"]["culture_arms"] == 90
    assert packet["sample_plan"]["conditions"] == ["Rest", "Stim8hr", "Stim48hr"]
    assert packet["controls"]["negative"] == ["non-targeting guide", "safe-harbor guide", "unstimulated matched culture"]
    assert packet["controls"]["positive"] == ["VAV1", "LAT", "CD3E"]
    assert len(packet["candidates"]) == 5
    assert pg["gene"] == "PGGT1B"
    assert pg["queue"] == "primary_assay_queue"
    assert pg["primary_question"].startswith("Does PGGT1B")
    assert "orthogonal knockdown" in pg["qc_before_interpretation"][0]
    assert "stimulated program shift" in pg["promote_if"]
    assert "Rest-only" in pg["weaken_if"]
    assert "failed on-target knockdown" in pg["reject_if"]
    assert "/data/assay_operations_bundle.json" in pg["replay_links"]
    assert "/data/pggt1b_deep_dive.json" in pg["replay_links"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_pilot_design_rows_keep_acceptance_gate_explicit():
    packet = build_pilot_design()

    for row in packet["candidates"]:
        assert row["status"] == "evidence_attached"
        assert row["trust_boundary"] == "proposal_only"
        assert row["acceptance_gate"] == "replay follow-up evidence through frozen checks, then require human signature"
        assert row["missing_evidence_before_acceptance"]
        assert row["decision_record"] == "proposal-only pilot row, not accepted biological state"


def test_pilot_design_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "gladstone_pilot_design.json"
    out_csv = tmp_path / "gladstone_pilot_design.csv"
    out_doc = tmp_path / "GLADSTONE_PILOT_DESIGN.md"

    write_pilot_design(out_json=out_json, out_csv=out_csv, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    csv_rows = list(csv.DictReader(out_csv.open()))
    doc = out_doc.read_text()
    assert data["sample_plan"]["culture_arms"] == 90
    assert csv_rows[0]["gene"] == "PGGT1B"
    assert csv_rows[0]["queue"] == "primary_assay_queue"
    assert "Gladstone pilot design" in doc
    assert "90 culture arms" in doc
    assert "proposal only" in doc
    assert "human signature" in doc


def test_pilot_design_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "pilot-design"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "gladstone_pilot_design.json" in proc.stdout


if __name__ == "__main__":
    test_pilot_design_turns_assay_ops_into_bench_plan()
    test_pilot_design_rows_keep_acceptance_gate_explicit()
    test_pilot_design_writes_json_csv_and_markdown(Path("/tmp/prospect-pilot-design-test"))
    test_pilot_design_runs_from_prospect_cli()
    print("PASS: Gladstone pilot design")
