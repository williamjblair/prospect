"""Endgame fixed-bar result tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.defended_discovery_endgame_result import (
    build_defended_discovery_endgame_result,
    write_defended_discovery_endgame_result,
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


def test_endgame_result_scores_all_locked_candidates():
    packet = build_defended_discovery_endgame_result()

    assert packet["phase"] == "defended_discovery_endgame_result"
    assert packet["pre_registration_id"] == "endgame_prereg_cc12f4edc74c23b1"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["candidate_count"] == 18
    assert packet["cleared_count"] == 1
    assert packet["outcome"] == "defended_lead"
    assert packet["lead_candidate"]["gene"] == "PGGT1B"
    assert packet["lead_candidate"]["decision"] == "clears_fixed_bar_pending_human_key"
    assert [row["rank"] for row in packet["candidate_decisions"]] == list(range(1, 19))
    assert packet["candidate_decisions"][0]["gene"] == "PGGT1B"
    assert packet["candidate_decisions"][-1]["gene"] == "ZC3H12A"


def test_endgame_result_treats_rpe1_noncoverage_as_context_not_failure():
    packet = build_defended_discovery_endgame_result()

    assert packet["non_blocking_not_assayed"] == [
        {
            "rung": "cell_type_specificity",
            "typed_detail": "rpe1_not_assayed",
            "affected_candidates": 18,
            "basis": "RPE1 coverage is sparse in the frozen Replogle comparator, so missing RPE1 rows are not_assayed context.",
        }
    ]
    assert all(
        not any(block["typed_detail"] == "rpe1_not_assayed" for block in row["blocking_rungs"])
        for row in packet["candidate_decisions"]
    )
    assert all(
        any(ctx["typed_detail"] == "rpe1_not_assayed" for ctx in row["not_assayed_context"])
        for row in packet["candidate_decisions"]
    )


def test_endgame_result_preserves_support_without_overclaiming():
    packet = build_defended_discovery_endgame_result()
    by_gene = {row["gene"]: row for row in packet["candidate_decisions"]}

    assert by_gene["PGGT1B"]["independent_primary_t_cell_support"] == ["shifrut_2018_1107"]
    assert by_gene["PGGT1B"]["decision"] == "clears_fixed_bar_pending_human_key"
    assert by_gene["PGGT1B"]["blocking_rungs"] == []
    assert by_gene["PGGT1B"]["orthogonal_public_dataset_count"] >= 5
    assert by_gene["CCDC22"]["independent_primary_t_cell_support"] == ["shifrut_2018_1107"]
    assert by_gene["LETM2"]["independent_primary_t_cell_support"] == ["shifrut_2018_1109"]
    assert by_gene["RCC1L"]["independent_primary_t_cell_support"] == []
    assert by_gene["PGGT1B"]["real_world_hook"]["status"] == "evidence_attached"
    assert by_gene["CCDC22"]["real_world_hook"]["status"] == "evidence_attached"
    assert by_gene["RCC1L"]["real_world_hook"]["status"] == "not_cleared"
    assert by_gene["CCDC22"]["decision"] == "not_selected_after_rank1_lead"
    assert "rank 1 PGGT1B is retained first" in by_gene["CCDC22"]["decision_basis"]


def test_endgame_result_records_real_kill_outcomes_for_each_candidate():
    packet = build_defended_discovery_endgame_result()
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
    by_gene = {row["gene"]: row for row in packet["candidate_decisions"]}
    assert by_gene["RWDD2B"]["kill_attempts"][1]["result"] == "not_cleared"
    assert by_gene["LETM2"]["blocking_rungs"][0]["typed_detail"] == "k562_not_assayed"
    assert by_gene["TNNC1"]["blocking_rungs"][0]["typed_detail"] == "k562_not_assayed"


def test_endgame_result_writes_clean_outputs(tmp_path):
    out_json = tmp_path / "defended_discovery_endgame_result.json"
    out_doc = tmp_path / "DEFENDED_DISCOVERY_ENDGAME_RESULT.md"

    packet = write_defended_discovery_endgame_result(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_strings(packet)) + "\n" + doc

    assert packet["ledger_id"].startswith("endgame_result_")
    assert "PGGT1B is retained as the rank-1 proposal-only lead worth testing" in doc
    assert "PGGT1B clears the fixed bar" not in doc
    assert "RPE1 non-coverage is retained as not_assayed context" in doc
    assert "PGGT1B" in doc
    assert "ZC3H12A" in doc
    assert "\u2014" not in text
    assert ("Generated" + " with") not in text
    assert ("Co-" + "Authored-By") not in text


def test_endgame_result_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "defended-discovery-endgame-result"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "defended_discovery_endgame_result.json" in proc.stdout
