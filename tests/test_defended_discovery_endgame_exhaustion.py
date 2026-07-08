"""Endgame exhaustion ledger tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.defended_discovery_endgame_exhaustion import (
    build_defended_discovery_endgame_exhaustion,
    write_defended_discovery_endgame_exhaustion,
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


def test_endgame_exhaustion_scores_all_locked_candidates():
    packet = build_defended_discovery_endgame_exhaustion()

    assert packet["phase"] == "defended_discovery_endgame_exhaustion"
    assert packet["pre_registration_id"] == "endgame_prereg_eb5b25712a2a0355"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["candidate_count"] == 18
    assert packet["cleared_count"] == 0
    assert packet["outcome"] == "honest_exhaustion"
    assert [row["rank"] for row in packet["candidate_decisions"]] == list(range(1, 19))
    assert packet["candidate_decisions"][0]["gene"] == "PGGT1B"
    assert packet["candidate_decisions"][-1]["gene"] == "ZC3H12A"


def test_endgame_exhaustion_records_common_hard_blockers():
    packet = build_defended_discovery_endgame_exhaustion()

    assert packet["common_blockers"] == [
        {
            "rung": "cell_type_specificity",
            "typed_detail": "rpe1_not_assayed",
            "affected_candidates": 18,
        }
    ]
    assert all(
        any(block["typed_detail"] == "rpe1_not_assayed" for block in row["blocking_rungs"])
        for row in packet["candidate_decisions"]
    )
    assert packet["candidate_decisions"][0]["blocking_rungs"][0]["rung"] == "cell_type_specificity"


def test_endgame_exhaustion_preserves_support_without_overclaiming():
    packet = build_defended_discovery_endgame_exhaustion()
    by_gene = {row["gene"]: row for row in packet["candidate_decisions"]}

    assert by_gene["PGGT1B"]["independent_primary_t_cell_support"] == ["shifrut_2018_1107"]
    assert by_gene["CCDC22"]["independent_primary_t_cell_support"] == ["shifrut_2018_1107"]
    assert by_gene["LETM2"]["independent_primary_t_cell_support"] == ["shifrut_2018_1109"]
    assert by_gene["RCC1L"]["independent_primary_t_cell_support"] == []
    assert by_gene["PGGT1B"]["real_world_hook"]["status"] == "evidence_attached"
    assert by_gene["CCDC22"]["real_world_hook"]["status"] == "evidence_attached"
    assert by_gene["RCC1L"]["real_world_hook"]["status"] == "not_cleared"
    assert by_gene["CCDC22"]["decision"] == "not_cleared_full_bar"
    assert "prior rank-5 packet" in by_gene["CCDC22"]["decision_basis"]


def test_endgame_exhaustion_records_kill_outcomes_for_each_candidate():
    packet = build_defended_discovery_endgame_exhaustion()
    for row in packet["candidate_decisions"]:
        kills = {kill["kill_id"]: kill for kill in row["kill_attempts"]}
        assert set(kills) == {
            "technical_confound",
            "essentiality_or_proliferation_artifact",
            "batch_or_donor_effect",
            "reverse_causality_or_passenger_marker",
            "better_alternative_mechanism",
        }
        assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
        assert kills["batch_or_donor_effect"]["result"] in {
            "survives_current_frozen_evidence",
            "not_cleared",
        }


def test_endgame_exhaustion_writes_clean_outputs(tmp_path):
    out_json = tmp_path / "defended_discovery_endgame_exhaustion.json"
    out_doc = tmp_path / "DEFENDED_DISCOVERY_ENDGAME_EXHAUSTION.md"

    packet = write_defended_discovery_endgame_exhaustion(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_strings(packet)) + "\n" + doc

    assert packet["ledger_id"].startswith("endgame_exhaustion_")
    assert "0 candidates cleared" in doc
    assert "RPE1 specificity is not_assayed for 18 of 18 candidates" in doc
    assert "PGGT1B" in doc
    assert "ZC3H12A" in doc
    assert "\u2014" not in text
    assert ("Generated" + " with") not in text
    assert ("Co-" + "Authored-By") not in text


def test_endgame_exhaustion_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "defended-discovery-endgame-exhaustion"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "defended_discovery_endgame_exhaustion.json" in proc.stdout
