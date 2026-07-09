"""Contracts for the exhaustive coverage expansion runner."""
from __future__ import annotations

from frontier.exhaustive_coverage import build_preregistration


def test_exhaustive_coverage_preregistration_locks_source_and_scale():
    packet = build_preregistration()

    assert packet["phase"] == "exhaustive_coverage_expansion_preregistration"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["anthropic_budget_usd"] == 0
    assert packet["gene_universe"]["gene_count"] == 11526
    assert packet["target_scale"] == "all 11,526 genes in the current frozen atlas"


def test_exhaustive_coverage_preregistration_keeps_noncoverage_honest():
    packet = build_preregistration()
    rules = packet["coverage_rules"]

    assert rules["covered"].startswith("NCBI maps")
    assert rules["mapped_no_tcell_rows"].startswith("NCBI maps")
    assert rules["unmapped"].startswith("NCBI does not map")
    assert rules["noncoverage_policy"] == "noncoverage is never a contradiction"
    assert "resume" in packet["checkpoint_contract"]["resume_rule"]
