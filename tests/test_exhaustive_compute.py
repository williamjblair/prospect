"""Contracts for the multi-day exhaustive compute runner."""
from __future__ import annotations

from frontier.exhaustive_compute import build_preregistration


def test_exhaustive_preregistration_sets_scale_and_trust_boundary():
    packet = build_preregistration()

    assert packet["phase"] == "exhaustive_compute_preregistration"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["anthropic_budget_usd"] == 0
    assert packet["pre_registration_id"].startswith("exhaustive_prereg_")
    assert packet["target_scale"]["literature_records"].startswith("target thousands")


def test_exhaustive_preregistration_pins_typed_status_and_comparability():
    packet = build_preregistration()
    ladder = packet["typed_status_ladder"]
    rules = packet["literature_audit_rules"]

    assert set(ladder) == {"evidence_attached", "contradicted", "orthogonal_phenotype", "not_assayed"}
    assert ladder["contradicted"].startswith("explicit causal activation-driver claim")
    assert "Cytokine" not in rules["comparability_rule"]
    assert "comparable" in rules["contradiction_rule"]
    assert len(rules["query_plan"]) >= 25


def test_exhaustive_preregistration_checkpoint_contract_is_resumable():
    packet = build_preregistration()
    checkpoint = packet["checkpoint_contract"]

    assert checkpoint["state_path"] == "output/exhaustive_compute/literature_state.json"
    assert checkpoint["documents_jsonl"].endswith("literature_documents.jsonl")
    assert checkpoint["claims_jsonl"].endswith("literature_claims.jsonl")
    assert "resume" in checkpoint["resume_rule"]
    assert "at most the current Europe PMC page" in checkpoint["crash_loss_bound"]


def test_exhaustive_preregistration_keeps_known_survivors_as_baseline():
    packet = build_preregistration()
    day3 = packet["day_3_rules"]

    assert day3["known_survivor_baseline"] == ["PGGT1B", "CCDC22", "LETM2"]
    assert "without relabeling the known three as new" in day3["freshness_rule"]
    assert len(day3["kill_attempts"]) == 5
