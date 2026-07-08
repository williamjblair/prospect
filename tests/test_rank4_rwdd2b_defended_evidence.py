"""RWDD2B rank-4 defended-evidence packet tests."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.rwdd2b_defended_evidence import (
    build_rwdd2b_defended_evidence,
    write_rwdd2b_defended_evidence,
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


def test_rwdd2b_packet_uses_frozen_rank_4_rows():
    packet = build_rwdd2b_defended_evidence()

    assert packet["phase"] == "rank_4_rwdd2b_defended_evidence"
    assert packet["gene"] == "RWDD2B"
    assert packet["candidate_rank"] == 4
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["pre_registration_id"] == "prereg_9f31fbf1e6c1cf10"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert packet["source_packets"] == {
        "cross_validation": "examples/data/cross_validation.json",
        "decision_ledger": "examples/data/defended_candidate_decisions.json",
        "discovery_campaign": "examples/data/discovery_campaign.json",
    }


def test_rwdd2b_packet_records_support_and_missing_rungs():
    packet = build_rwdd2b_defended_evidence()
    evidence = {row["source"]: row for row in packet["scored_evidence"]}
    failures = {row["rung"]: row for row in packet["clearance_failures"]}

    assert evidence["marson_frontier"]["status"] == "computationally_reproduced"
    assert evidence["marson_frontier"]["summary"] == "720 stimulated DE genes, 190 Rest DE genes"
    assert evidence["replogle_specificity"]["summary"] == "K562 1; RPE1 None"
    assert evidence["primary_t_cell_screen_support"]["summary"] == (
        "no supporting Shifrut or Schmidt primary T-cell hit in the frozen cross-validation packet"
    )
    assert evidence["string_network"]["summary"] == "no STRING partners attached in frozen packet"
    assert evidence["dice_expression"]["summary"] == "activated CD4 mean TPM 7.941"
    assert failures["independent_primary_t_cell_support"]["reason"] == (
        "RWDD2B has no supporting hit in Shifrut 2018 and Schmidt remains an orthogonal cytokine-production phenotype"
    )
    assert failures["real_world_hook"]["reason"] == (
        "the bounded Open Targets overlay has no selected immune or hematologic context for RWDD2B"
    )
    assert failures["specific_mechanism"]["reason"] == (
        "no STRING partners are attached, so the frozen packet does not state a specific stimulated CD4+ activation mechanism"
    )


def test_rwdd2b_packet_declares_not_cleared_and_advances():
    packet = build_rwdd2b_defended_evidence()
    kills = {row["kill_id"]: row for row in packet["kill_attempts"]}

    assert packet["defended_discovery_status"] == "not_cleared_full_bar"
    assert packet["decision_recommendation"] == "demote_and_advance"
    assert packet["next_candidate"] == {
        "rank": 5,
        "gene": "CCDC22",
        "required_next_packet": "rank_5_ccdc22_defended_evidence",
    }
    assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
    assert kills["essentiality_or_proliferation_artifact"]["result"] == "not_cleared"
    assert kills["batch_or_dataset_specificity"]["result"] == "not_cleared"
    assert kills["alternative_mechanism"]["result"] == "not_cleared"


def test_rwdd2b_packet_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "rwdd2b_defended_evidence.json"
    out_doc = tmp_path / "RWDD2B_DEFENDED_EVIDENCE.md"

    packet = write_rwdd2b_defended_evidence(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("rwdd2b_defended_")
    assert "RWDD2B" in doc
    assert "not cleared full bar" in doc
    assert "no STRING partners attached" in doc
    assert "CCDC22" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_rwdd2b_defended_evidence_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "rwdd2b-defended-evidence"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "rwdd2b_defended_evidence.json" in proc.stdout
