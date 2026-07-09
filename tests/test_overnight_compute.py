"""Contracts for the pre-registered overnight compute run."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def _load(name: str):
    return json.loads((DATA / name).read_text())


def test_overnight_preregistration_locks_rules_before_scoring():
    packet = _load("overnight_preregistration.json")

    assert packet["phase"] == "overnight_compute_preregistration"
    assert packet["pre_registration_id"].startswith("overnight_prereg_")
    assert packet["accepted"] is False
    assert packet["anthropic_budget_usd"] == 0
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["phase_1_genome_wide_atlas_rules"]["driver_threshold"] == "strongest on-target n_total_de_genes greater than 10"
    assert packet["phase_2_literature_audit_rules"]["comparability_rules"]["contradiction_requires"].startswith("explicit driver claim")
    assert len(packet["phase_3_defended_leaderboard_rules"]["kill_attempts"]) == 5


def test_overnight_genome_wide_atlas_types_all_marson_genes():
    atlas = _load("overnight_genome_wide_atlas.json")

    assert atlas["accepted"] is False
    assert atlas["next"] == "human_signature_required"
    assert atlas["gene_count"] == 11526
    assert len(atlas["rows"]) == 11526
    assert sum(atlas["typed_status_counts"].values()) == 11526
    assert atlas["typed_status_counts"]["evidence_attached"] > 3000
    assert atlas["typed_status_counts"]["associative_only"] > 4000
    assert atlas["typed_status_counts"]["not_assayed"] > 3000
    assert atlas["content_signature"]["type"] == "sha256_content_hash_not_human_acceptance"
    assert atlas["rows"][0]["accepted"] is False


def test_overnight_literature_audit_earns_contradictions_only_for_comparable_claims():
    audit = _load("overnight_literature_audit.json")

    assert audit["accepted"] is False
    assert audit["document_count"] >= 200
    assert audit["claim_count"] >= 200
    assert audit["typed_status_counts"]["contradicted"] > 0
    assert not [row for row in audit["claims"] if row["gene"] == "CD4"]
    for row in audit["claims"]:
        if row["typed_status"] == "contradicted":
            assert row["readout_comparability"] == "comparable"
            assert row["marson_strongest_de"] is not None
            assert row["marson_strongest_de"] <= 10


def test_overnight_defended_leaderboard_keeps_outputs_proposal_only():
    leaderboard = _load("overnight_defended_leaderboard.json")

    assert leaderboard["accepted"] is False
    assert leaderboard["next"] == "human_signature_required"
    assert leaderboard["candidate_count_scored"] == 2734
    assert leaderboard["cleared_compute_bar_count"] == 3
    cleared = [
        row for row in leaderboard["leaderboard"]
        if row["leaderboard_status"] == "clears_pre_registered_compute_bar"
    ]
    assert [row["gene"] for row in cleared] == ["PGGT1B", "CCDC22", "LETM2"]
    for lead in cleared:
        assert lead["accepted"] is False
        assert lead["orthogonal_dataset_count"] >= 5
        assert all(kill["result"] == "survives_current_frozen_evidence" for kill in lead["kill_attempts"])


def test_overnight_report_states_the_ceiling_without_em_dash():
    report = (ROOT / "docs" / "OVERNIGHT_COMPUTE_REPORT.md").read_text()

    assert "Computation over released data, not wet-lab or clinical truth." in report
    assert "accepted=false" in report
    assert "\u2014" not in report
