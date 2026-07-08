"""Campaign pressure summary tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.campaign_pressure_summary import build_summary, write_summary


def test_campaign_pressure_summary_accounts_for_model_pressure_without_acceptance():
    summary = build_summary()

    assert summary["title"] == "Campaign pressure summary"
    assert summary["status"] == "evidence_attached"
    assert summary["trust_boundary"] == "proposal_only"
    assert summary["acceptance"] is False
    assert summary["accepted_state_mutations"] == 0
    assert summary["model_in_trust_path"] == "no"
    assert summary["counts"]["campaign_candidates"] == 20
    assert summary["counts"]["deterministic_review_rows"] == 20
    assert summary["counts"]["claude_probe_rows"] == 20
    assert summary["counts"]["aligned_rows"] == 6
    assert summary["counts"]["more_aggressive_rows"] == 11
    assert summary["counts"]["more_cautious_rows"] == 3
    assert summary["counts"]["triage_rows"] == 11
    assert summary["counts"]["gate_probe_rows"] == 11
    assert summary["gate_recommendations"] == {
        "add_control": 4,
        "gate_sufficient": 6,
        "lower_priority": 1,
    }
    assert summary["gate_probe_coverage"]["coverage_status"] == "complete"
    assert summary["gate_probe_coverage"]["returned_decisions"] == 11
    assert summary["gate_probe_coverage"]["requested_limit"] == 11
    assert summary["gate_probe_coverage"]["missing_decisions"] == 0
    assert summary["closed_recommendations"] == ["add_control", "gate_sufficient", "lower_priority"]
    assert summary["pressure_accounting"][0]["gene"] == "PGGT1B"
    assert summary["pressure_accounting"][0]["pressure_result"] == "aligned_with_deterministic_review"
    assert summary["pressure_accounting"][1]["gene"] == "RCC1L"
    assert summary["pressure_accounting"][1]["pressure_result"] == "converted_to_assay_gate"
    assert summary["pressure_accounting"][1]["gate_recommendation"] == "gate_sufficient"
    by_gene = {row["gene"]: row for row in summary["pressure_accounting"]}
    assert by_gene["SNAP29"]["pressure_result"] == "model_more_cautious"
    assert "accepted state" in summary["boundary_statement"]
    assert "verified" not in json.dumps(summary).lower()
    assert "true" not in json.dumps(summary).lower()


def test_campaign_pressure_summary_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_pressure_summary.json"
    out_doc = tmp_path / "CAMPAIGN_PRESSURE_SUMMARY.md"

    write_summary(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "evidence_attached"
    assert data["counts"]["claude_probe_rows"] == 20
    assert data["gate_recommendations"]["gate_sufficient"] == 6
    assert data["gate_probe_coverage"]["coverage_status"] == "complete"
    assert "Campaign pressure summary" in doc
    assert "proposal only" in doc
    assert "Coverage status: `complete`" in doc
    assert "accepted state" in doc
    assert "./prospect campaign-pressure" in doc


def test_campaign_pressure_summary_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "campaign-pressure"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "campaign_pressure_summary.json" in proc.stdout


if __name__ == "__main__":
    test_campaign_pressure_summary_accounts_for_model_pressure_without_acceptance()
    test_campaign_pressure_summary_writes_json_and_markdown(Path("/tmp/prospect-campaign-pressure-test"))
    test_campaign_pressure_summary_runs_from_prospect_cli()
    print("PASS: campaign pressure summary")
