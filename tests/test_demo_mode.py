"""Deterministic demo mode contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from receipt.acceptance_service import build_submission_result
from services.prospect_acceptance_service import AcceptanceStore


def test_demo_mode_writes_shareable_state_and_live_script(tmp_path):
    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "demo-mode",
            "--reset",
            "--json",
            "--data-dir",
            str(tmp_path),
            "--base-url",
            "http://demo.local",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    packet = json.loads(proc.stdout)
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["ceiling"] == "Computation over released data, not wet-lab or clinical truth."
    assert [beat["id"] for beat in packet["beats"]] == [
        "real_claude_science_export",
        "pggt1b_hypothesis",
        "run_your_own_claim",
        "honest_funnel",
    ]
    paste = packet["beats"][2]
    assert paste["proposal_url"].startswith("http://demo.local/proposal/")
    assert paste["counts"] == {
        "genes": 5,
        "drivers": 1,
        "passengers": 2,
        "contradicted": 0,
        "not_assayed": 2,
    }
    assert packet["ledger"]["submission_count"] == 1
    assert (tmp_path / "acceptance.sqlite3").exists()


def test_demo_reset_clears_acceptance_proposals(tmp_path):
    store = AcceptanceStore(tmp_path)
    store.store_result(build_submission_result("IL7R", source_name="reset_test"))
    assert store.table_counts()["proposals"] == 1

    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "demo-reset",
            "--json",
            "--data-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["accepted"] is False
    assert result["next"] == "human_signature_required"
    assert result["removed_proposals"] == 1
    assert not (tmp_path / "acceptance.sqlite3").exists()


if __name__ == "__main__":
    import tempfile

    test_demo_mode_writes_shareable_state_and_live_script(Path(tempfile.mkdtemp()))
    test_demo_reset_clears_acceptance_proposals(Path(tempfile.mkdtemp()))
    print("PASS: demo mode")
