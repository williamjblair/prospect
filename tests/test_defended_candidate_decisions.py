"""Decision ledger for defended-discovery candidates."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.defended_candidate_decisions import (
    build_defended_candidate_decisions,
    write_defended_candidate_decisions,
)


def _string_values(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _string_values(value)


def test_decision_ledger_demotes_pggt1b_without_overclaiming():
    packet = build_defended_candidate_decisions()
    first = packet["candidate_decisions"][0]

    assert packet["phase"] == "defended_candidate_decision_ledger"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["pre_registration_id"] == "prereg_9f31fbf1e6c1cf10"
    assert first["gene"] == "PGGT1B"
    assert first["rank"] == 1
    assert first["decision"] == "not_cleared_full_bar"
    assert first["typed_status"] == "evidence_attached"
    assert first["disposition"] == "demote_and_advance"
    assert first["missing_required_rung"] == (
        "comparable activation-transcriptome or activation-marker primary T-cell screen"
    )
    assert first["why_not_contradicted"] == (
        "the frozen comparators do not refute PGGT1B; they fail to supply the required comparable replication rung"
    )


def test_decision_ledger_holds_rank_5_candidate():
    packet = build_defended_candidate_decisions()

    assert packet["decided_count"] == 4
    assert packet["remaining_candidate_count"] == 13
    assert packet["next_candidate"] is None
    assert packet["held_candidate"] == {
        "rank": 5,
        "gene": "CCDC22",
            "typed_status": "evidence_attached",
            "defended_discovery_status": "computational_bar_cleared_pending_human_key",
            "evidence_packet": "examples/data/ccdc22_defended_evidence.json",
            "evidence_packet_id": "ccdc22_defended_d215ebad7b4f0355",
            "disposition": "hold_and_deepen",
            "orthogonal_public_dataset_count": 7,
        }
    assert packet["campaign_state"] == "candidate_hold_pending_human_key"
    assert packet["completion_status"] == "computational_bar_cleared_pending_human_key"


def test_decision_ledger_links_frozen_evidence_and_kill_state():
    packet = build_defended_candidate_decisions()
    first = packet["candidate_decisions"][0]

    assert first["evidence_packet"] == "examples/data/pggt1b_defended_evidence.json"
    assert first["evidence_packet_id"] == "pggt1b_defended_efa0475e4521d8a4"
    assert first["scored_public_dataset_count"] == 10
    assert first["kill_results"] == {
        "technical_confound": "survives_current_frozen_evidence",
        "essentiality_or_proliferation_artifact": "survives_current_frozen_evidence",
        "batch_or_dataset_specificity": "not_cleared",
        "alternative_mechanism": "survives_current_frozen_evidence",
    }
    assert first["decision_rule"] == (
        "advance when a candidate does not clear every pre-registered rung; do not rewrite the bar"
    )
    second = packet["candidate_decisions"][1]
    assert second["gene"] == "RCC1L"
    assert second["rank"] == 2
    assert second["evidence_packet_id"] == "rcc1l_defended_b83b31c038fb08ab"
    assert second["missing_required_rung"] == (
        "independent primary T-cell support, real-world hook, and specific activation mechanism"
    )
    third = packet["candidate_decisions"][2]
    assert third["gene"] == "MCAT"
    assert third["rank"] == 3
    assert third["evidence_packet"] == "examples/data/mcat_defended_evidence.json"
    assert third["evidence_packet_id"] == "mcat_defended_0758073ad35881b2"
    assert third["missing_required_rung"] == (
        "independent primary T-cell support, real-world hook, and specific activation mechanism"
    )
    assert third["why_not_contradicted"] == (
        "the frozen comparators do not refute MCAT; they show the candidate lacks required independent support and hook"
    )
    assert third["kill_results"] == {
        "technical_confound": "survives_current_frozen_evidence",
        "essentiality_or_proliferation_artifact": "survives_current_frozen_evidence",
        "batch_or_dataset_specificity": "not_cleared",
        "alternative_mechanism": "not_cleared",
    }
    fourth = packet["candidate_decisions"][3]
    assert fourth["gene"] == "RWDD2B"
    assert fourth["rank"] == 4
    assert fourth["evidence_packet"] == "examples/data/rwdd2b_defended_evidence.json"
    assert fourth["evidence_packet_id"] == "rwdd2b_defended_25462753f98f662f"
    assert fourth["missing_required_rung"] == (
        "independent primary T-cell support, real-world hook, specific activation mechanism, and non-activation artifact kill"
    )
    assert fourth["why_not_contradicted"] == (
        "the frozen comparators do not refute RWDD2B; they show the candidate lacks required independent support and mechanism"
    )
    assert fourth["kill_results"] == {
        "technical_confound": "survives_current_frozen_evidence",
        "essentiality_or_proliferation_artifact": "not_cleared",
        "batch_or_dataset_specificity": "not_cleared",
        "alternative_mechanism": "not_cleared",
    }


def test_decision_ledger_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "defended_candidate_decisions.json"
    out_doc = tmp_path / "DEFENDED_CANDIDATE_DECISIONS.md"

    packet = write_defended_candidate_decisions(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("defended_decisions_")
    assert "PGGT1B" in doc
    assert "RCC1L" in doc
    assert "MCAT" in doc
    assert "RWDD2B" in doc
    assert "CCDC22" in doc
    assert "not cleared full bar" in doc
    assert "computational bar cleared, pending human key" in doc
    assert "demote and advance" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_decision_ledger_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "defended-candidate-decisions"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "defended_candidate_decisions.json" in proc.stdout
