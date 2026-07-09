"""Rank-1 PGGT1B decision under the endgame pre-registration."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.rank1_pggt1b_endgame_decision import (
    build_rank1_pggt1b_endgame_decision,
    write_rank1_pggt1b_endgame_decision,
)


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _strings(value)


def test_pggt1b_endgame_decision_uses_committed_preregistration():
    packet = build_rank1_pggt1b_endgame_decision()

    assert packet["phase"] == "rank_1_pggt1b_endgame_decision"
    assert packet["gene"] == "PGGT1B"
    assert packet["rank"] == 1
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["pre_registration_id"] == "endgame_prereg_cc12f4edc74c23b1"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["decision"] == "clears_fixed_bar_pending_human_key"
    assert packet["next_candidate"] is None


def test_pggt1b_endgame_decision_records_exact_failed_rungs():
    packet = build_rank1_pggt1b_endgame_decision()
    rungs = {row["rung"]: row for row in packet["bar_rungs"]}

    assert rungs["novel_driver"]["status"] == "evidence_attached"
    assert rungs["zero_drift_reproducibility"]["status"] == "computationally_reproduced"
    assert rungs["cell_type_specificity"]["status"] == "evidence_attached"
    assert rungs["cell_type_specificity"]["typed_detail"] == "k562_specific_rpe1_not_assayed"
    assert rungs["five_frozen_orthogonal_public_datasets"]["status"] == "evidence_attached"
    assert rungs["readout_comparability"]["status"] == "evidence_attached"
    assert "Schmidt" in rungs["readout_comparability"]["basis"]
    assert rungs["falsifiable_experiment"]["status"] == "evidence_attached"


def test_pggt1b_endgame_decision_keeps_kills_distinct_from_missing_rungs():
    packet = build_rank1_pggt1b_endgame_decision()
    kills = {row["kill_id"]: row for row in packet["kill_attempts"]}

    assert len(kills) == 5
    assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
    assert kills["essentiality_or_proliferation_artifact"]["result"] == "survives_current_frozen_evidence"
    assert kills["batch_or_donor_effect"]["result"] == "survives_current_frozen_evidence"
    assert kills["reverse_causality_or_passenger_marker"]["result"] == "survives_current_frozen_evidence"
    assert kills["better_alternative_mechanism"]["result"] == "survives_current_frozen_evidence"
    assert packet["why_not_discovery"] == [
        "No human key has accepted PGGT1B into frontier state.",
        "This is computation over released data, not wet-lab or clinical truth.",
    ]


def test_pggt1b_endgame_decision_freezes_source_hashes_and_writes_clean_outputs(tmp_path):
    out_json = tmp_path / "pggt1b_endgame_decision.json"
    out_doc = tmp_path / "PGGT1B_ENDGAME_DECISION.md"

    packet = write_rank1_pggt1b_endgame_decision(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_strings(packet)) + "\n" + doc

    assert packet["decision_id"].startswith("pggt1b_endgame_")
    assert all(row["sha256"] for row in packet["frozen_sources"])
    assert "retained as the rank-1 proposal-only lead" in doc
    assert "clears the fixed bar" not in doc
    assert "RPE1 is not_assayed context, not a failed rung" in doc
    assert "Shifrut" in doc
    assert "Next candidate: `none`" in doc
    assert "\u2014" not in text
    assert ("Generated" + " with") not in text
    assert ("Co-" + "Authored-By") not in text


def test_pggt1b_endgame_decision_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "pggt1b-endgame-decision"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "pggt1b_endgame_decision.json" in proc.stdout
