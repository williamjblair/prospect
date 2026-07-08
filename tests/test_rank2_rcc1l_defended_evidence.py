"""RCC1L rank-2 defended-evidence packet tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.rcc1l_defended_evidence import (
    build_rcc1l_defended_evidence,
    write_rcc1l_defended_evidence,
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


def test_rcc1l_packet_uses_frozen_rank_2_rows():
    packet = build_rcc1l_defended_evidence()

    assert packet["phase"] == "rank_2_rcc1l_defended_evidence"
    assert packet["gene"] == "RCC1L"
    assert packet["candidate_rank"] == 2
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["pre_registration_id"] == "prereg_9f31fbf1e6c1cf10"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert packet["source_packets"] == {
        "cross_validation": "examples/data/cross_validation.json",
        "discovery_campaign": "examples/data/discovery_campaign.json",
        "decision_ledger": "examples/data/defended_candidate_decisions.json",
    }


def test_rcc1l_packet_records_support_and_missing_rungs():
    packet = build_rcc1l_defended_evidence()
    evidence = {row["source"]: row for row in packet["scored_evidence"]}
    failures = {row["rung"]: row for row in packet["clearance_failures"]}

    assert evidence["marson_frontier"]["status"] == "computationally_reproduced"
    assert evidence["replogle_specificity"]["status"] == "evidence_attached"
    assert evidence["schmidt_2022_orcs_2427"]["status"] == "orthogonal_phenotype"
    assert evidence["primary_t_cell_screen_support"]["status"] == "evidence_attached"
    assert evidence["primary_t_cell_screen_support"]["summary"] == (
        "no supporting Shifrut or Schmidt primary T-cell hit in the frozen cross-validation packet"
    )
    assert evidence["string_network"]["status"] == "evidence_attached"
    assert evidence["dice_expression"]["summary"] == "activated CD4 mean TPM 10.784"
    assert failures["independent_primary_t_cell_support"]["reason"] == (
        "RCC1L has no supporting hit in Shifrut 2018 and Schmidt remains an orthogonal cytokine-production phenotype"
    )
    assert failures["real_world_hook"]["reason"] == (
        "the bounded Open Targets overlay has no selected immune or hematologic context for RCC1L"
    )
    assert failures["specific_mechanism"]["reason"] == (
        "STRING context does not yet specify a direct stimulated CD4+ activation mechanism"
    )


def test_rcc1l_packet_declares_not_cleared_and_advances():
    packet = build_rcc1l_defended_evidence()
    kills = {row["kill_id"]: row for row in packet["kill_attempts"]}

    assert packet["defended_discovery_status"] == "not_cleared_full_bar"
    assert packet["decision_recommendation"] == "demote_and_advance"
    assert packet["next_candidate"] == {
        "rank": 3,
        "gene": "MCAT",
        "required_next_packet": "rank_3_mcat_defended_evidence",
    }
    assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
    assert kills["essentiality_or_proliferation_artifact"]["result"] == "survives_current_frozen_evidence"
    assert kills["batch_or_dataset_specificity"]["result"] == "not_cleared"
    assert kills["alternative_mechanism"]["result"] == "not_cleared"


def test_rcc1l_packet_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "rcc1l_defended_evidence.json"
    out_doc = tmp_path / "RCC1L_DEFENDED_EVIDENCE.md"

    packet = write_rcc1l_defended_evidence(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("rcc1l_defended_")
    assert "RCC1L" in doc
    assert "not cleared full bar" in doc
    assert "no supporting Shifrut or Schmidt primary T-cell hit" in doc
    assert "MCAT" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_rcc1l_defended_evidence_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "rcc1l-defended-evidence"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "rcc1l_defended_evidence.json" in proc.stdout
