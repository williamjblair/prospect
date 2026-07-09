"""One-page judge handout artifact tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.judge_handout import build_handout, write_handout
from cli.submit_pack import PUBLIC_ARTIFACTS


def test_judge_handout_summarizes_the_kept_surface_without_overclaiming():
    handout = build_handout()

    assert handout["title"] == "Prospect one-page judge handout"
    assert handout["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert handout["repo_url"] == "https://github.com/williamjblair/prospect"
    assert handout["signed_root"] == "root_a8b0dcdd4024e12f"
    assert handout["trust_boundary"]["model_in_trust_path"] == "no"
    assert handout["trust_boundary"]["accepted_state"] == "human_signed_replayable_root"
    assert handout["trust_boundary"]["model_accepted_state_mutations"] == 0
    assert handout["counts"]["public_artifacts"] == len(PUBLIC_ARTIFACTS)
    assert handout["counts"]["findings"] >= 3
    assert handout["counts"]["claude_science_drivers"] == 12
    assert handout["counts"]["claude_science_passengers"] == 22
    assert handout["counts"]["claude_science_contradicted"] == 3
    assert handout["counts"]["claude_science_not_assayed"] == 15
    assert handout["counts"]["substrate_after_not_assayed"] == 5
    assert handout["counts"]["pggt1b_novelty_downgraded"] is True
    assert handout["counts"]["pggt1b_wet_lab_minimum_donors"] >= 3
    assert handout["counts"]["pggt1b_orthogonal_public_datasets"] >= 5
    assert "sign the frontier root" in handout["human_only_actions"]
    assert "accept a submitted receipt" in handout["human_only_actions"]
    assert "wet-lab execution" in handout["human_only_actions"]
    assert "Reproducible is not verified." in handout["one_line"]


def test_judge_handout_writes_print_friendly_markdown(tmp_path):
    out_doc = tmp_path / "JUDGE_HANDOUT.md"

    handout = write_handout(out_doc=out_doc)

    doc = out_doc.read_text()
    assert handout["title"] in doc
    assert "Five-minute judge path" in doc
    assert "What Prospect proves" in doc
    assert "What remains human-only" in doc
    assert "./prospect verify" in doc
    assert "./prospect demo-mode --reset" in doc
    assert "/data/substrate_coverage_report.json" in doc
    assert "/data/pggt1b_defended_evidence.json" in doc
    assert "./prospect substrate-coverage" in doc
    assert "./prospect pggt1b-defended-evidence" in doc
    assert "ORCS primary T-cell context reduces uncovered Sade-Feldman genes to 5" in doc
    assert "PGGT1B novelty downgraded against prior art" in doc
    assert "Real Claude Science signature" in doc
    assert "driver/passenger/contradicted" in doc
    assert "Prospect proves computation over released data, not wet-lab or clinical truth." in doc
    # No cut surface leaks back in.
    for cut in ["discovery_campaign", "lab_packet", "disease_genetics_overlay", "overnight", "exhaustive", "survivor"]:
        assert cut not in doc
    assert "verified biology" not in doc.lower()


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
    test_judge_handout_summarizes_the_kept_surface_without_overclaiming()
    test_judge_handout_writes_print_friendly_markdown(Path("/tmp/prospect-judge-handout-test"))
    test_judge_handout_runs_from_prospect_cli()
    print("PASS: judge handout")
