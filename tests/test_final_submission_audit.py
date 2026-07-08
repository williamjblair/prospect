"""Final submission audit artifact tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.final_submission_audit import build_audit, write_audit
from cli.submit_pack import PUBLIC_ARTIFACTS


def test_final_submission_audit_states_current_readiness_without_overclaiming():
    audit = build_audit()

    assert audit["title"] == "Prospect final submission audit"
    assert audit["readiness"] == "submission_ready_for_human_upload"
    assert audit["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert audit["repo_url"] == "https://github.com/williamjblair/prospect"
    assert audit["signed_root"] == "root_a8b0dcdd4024e12f"
    assert audit["public_artifact_count"] == len(PUBLIC_ARTIFACTS)
    assert audit["public_artifacts"] == PUBLIC_ARTIFACTS
    assert "/data/final_submission_audit.json" in audit["public_artifacts"]
    assert audit["trust_boundary"]["model_in_trust_path"] == "no"
    assert audit["trust_boundary"]["model_accepted_state_mutations"] == 0
    assert "record_demo_video" in audit["human_only_actions"]
    assert "submit_project_form" in audit["human_only_actions"]
    assert "wet_lab_execution" in audit["human_only_actions"]
    assert "verified" not in json.dumps(audit).lower()
    assert "true" not in json.dumps(audit).lower()


def test_final_submission_audit_covers_all_shipped_workstreams():
    audit = build_audit()
    shipped = {item["workstream"]: item for item in audit["shipped_workstreams"]}

    for name in [
        "submission_floor",
        "second_substrate_replay",
        "claude_campaign_pressure",
        "gladstone_assay_operations",
        "demo_and_submission_packets",
    ]:
        assert shipped[name]["state"] == "shipped"


def test_final_submission_audit_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "final_submission_audit.json"
    out_doc = tmp_path / "FINAL_SUBMISSION_AUDIT.md"

    write_audit(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["readiness"] == "submission_ready_for_human_upload"
    assert "Prospect final submission audit" in doc
    assert "Human-only actions" in doc
    assert "record_demo_video" in doc
    assert "./prospect final-check" in doc
    assert "/data/assay_operations_bundle.json" in doc


def test_final_submission_audit_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submission-audit"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "final_submission_audit.json" in proc.stdout


if __name__ == "__main__":
    test_final_submission_audit_states_current_readiness_without_overclaiming()
    test_final_submission_audit_covers_all_shipped_workstreams()
    test_final_submission_audit_writes_json_and_markdown(Path("/tmp/prospect-final-submission-audit-test"))
    test_final_submission_audit_runs_from_prospect_cli()
    print("PASS: final submission audit")
