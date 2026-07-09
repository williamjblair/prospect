"""Contracts for the multi-day exhaustive compute runner."""
from __future__ import annotations

import json
from pathlib import Path

from frontier.exhaustive_compute import build_preregistration

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


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


def test_frozen_exhaustive_literature_audit_hits_real_scale():
    audit = json.loads((DATA / "exhaustive_literature_audit.json").read_text())

    assert audit["accepted"] is False
    assert audit["next"] == "human_signature_required"
    assert audit["document_count"] == 10000
    assert audit["claim_count"] == 5975
    assert audit["typed_status_counts"] == {
        "contradicted": 1547,
        "evidence_attached": 1787,
        "not_assayed": 785,
        "orthogonal_phenotype": 1856,
    }
    assert audit["contradiction_rate"] == 0.2589
    assert audit["snapshot_id"] == "exhaustive_lit_snapshot_489229374d703ab1"
    assert "not the full possible Europe PMC corpus" in audit["real_scale_assessment"]


def test_frozen_exhaustive_literature_claims_include_every_pmid():
    audit = json.loads((DATA / "exhaustive_literature_audit.json").read_text())
    claim_lines = (DATA / "exhaustive_literature_claims.jsonl").read_text().splitlines()
    doc_lines = (DATA / "exhaustive_literature_documents.jsonl").read_text().splitlines()

    assert len(claim_lines) == audit["claim_count"]
    assert len(doc_lines) == audit["document_count"]
    first_claim = json.loads(claim_lines[0])
    assert {"pmid", "gene", "typed_status", "readout_comparability", "claim_sentence"} <= set(first_claim)
    assert all(json.loads(line)["accepted"] is False for line in claim_lines[:25])
