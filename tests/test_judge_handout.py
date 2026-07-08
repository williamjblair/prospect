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
    assert handout["counts"]["campaign_rows"] == 20
    assert handout["counts"]["disease_overlay_rows"] == 20
    assert handout["counts"]["disease_overlay_context_rows"] == 10
    assert handout["counts"]["lab_packet_rows"] == 5
    assert handout["counts"]["endgame_candidates"] == 18
    assert handout["counts"]["endgame_cleared"] == 0
    assert handout["counts"]["endgame_with_t_cell_support"] == 4
    assert handout["counts"]["endgame_rpe1_not_assayed"] == 18
    assert "sign the frontier root" in handout["human_only_actions"]
    assert "accept a submitted receipt" in handout["human_only_actions"]
    assert "wet-lab execution" in handout["human_only_actions"]
    assert "verified" not in json.dumps(handout).lower()


def test_judge_handout_writes_print_friendly_markdown(tmp_path):
    out_doc = tmp_path / "JUDGE_HANDOUT.md"

    handout = write_handout(out_doc=out_doc)

    doc = out_doc.read_text()
    assert handout["title"] in doc
    assert "Five-minute judge path" in doc
    assert "What Prospect proves" in doc
    assert "What remains human-only" in doc
    assert "./prospect verify" in doc
    assert "/data/disease_genetics_overlay.json" in doc
    assert "/data/lab_packet.json" in doc
    assert "/data/defended_discovery_endgame_exhaustion.json" in doc
    assert "./prospect defended-discovery-endgame-exhaustion" in doc
    assert "18 locked candidates" in doc
    assert "0 cleared the pre-registered bar" in doc
    assert "Prospect proves computation over released data, not wet-lab or clinical truth." in doc
    # No cut surface leaks back in.
    for cut in ["final_submission_audit", "gladstone_pilot_design", "campaign_challenger", "release_manifest"]:
        assert cut not in doc
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
    test_judge_handout_summarizes_the_kept_surface_without_overclaiming()
    test_judge_handout_writes_print_friendly_markdown(Path("/tmp/prospect-judge-handout-test"))
    test_judge_handout_runs_from_prospect_cli()
    print("PASS: judge handout")
