"""One-page judge handout artifact tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.judge_handout import build_handout, write_handout


def test_judge_handout_summarizes_current_winning_path_without_overclaiming():
    handout = build_handout()

    assert handout["title"] == "Prospect one-page judge handout"
    assert handout["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert handout["repo_url"] == "https://github.com/williamjblair/prospect"
    assert handout["signed_root"] == "root_a8b0dcdd4024e12f"
    assert handout["readiness"] == "submission_ready_for_human_upload"
    assert handout["trust_boundary"]["model_in_trust_path"] == "no"
    assert handout["trust_boundary"]["accepted_state"] == "human_signed_replayable_root"
    assert handout["counts"]["public_artifacts"] == 20
    assert handout["counts"]["claude_probe_rows"] == 8
    assert handout["counts"]["assay_operations_candidates"] == 5
    assert handout["counts"]["substrate_replay_rows"] == 377
    assert "record_demo_video" in handout["human_only_actions"]
    assert "submit_project_form" in handout["human_only_actions"]
    assert "wet_lab_execution" in handout["human_only_actions"]
    assert "verified" not in json.dumps(handout).lower()
    assert "true" not in json.dumps(handout).lower()


def test_judge_handout_writes_print_friendly_markdown(tmp_path):
    out_doc = tmp_path / "JUDGE_HANDOUT.md"

    handout = write_handout(out_doc=out_doc)

    doc = out_doc.read_text()
    assert handout["title"] in doc
    assert "Five-minute judge path" in doc
    assert "What Prospect proves" in doc
    assert "What remains human-only" in doc
    assert "./prospect final-check" in doc
    assert "/data/final_submission_audit.json" in doc
    assert "/data/release_manifest.json" in doc
    assert "Prospect proves computation over released data, not wet-lab or clinical truth." in doc
    assert "verified" not in json.dumps(handout).lower()


def test_judge_handout_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "judge-handout"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "JUDGE_HANDOUT.md" in proc.stdout


if __name__ == "__main__":
    test_judge_handout_summarizes_current_winning_path_without_overclaiming()
    test_judge_handout_writes_print_friendly_markdown(Path("/tmp/prospect-judge-handout-test"))
    test_judge_handout_runs_from_prospect_cli()
    print("PASS: judge handout")
