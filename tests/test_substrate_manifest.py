"""Tests for manifest-based, non-collapsing multi-substrate evidence."""
from __future__ import annotations

from copy import deepcopy

import pytest

from receipt.acceptance_service import evaluate_submission
from receipt.schema import receipt_id_for
from receipt.substrate_manifest import list_substrates


def _request(evidence_mode: str) -> dict:
    return {
        "input_text": "FOXP1\nMED12\nIL7R",
        "filename": "genes.txt",
        "producer": "external_team",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "evidence_mode": evidence_mode,
    }


def test_six_manifests_are_content_addressed_and_replayable():
    manifests = list_substrates()

    assert len(manifests) == 6
    assert {row["substrate_id"] for row in manifests} == {
        "marson_cd4_activation",
        "replogle_k562",
        "replogle_rpe1",
        "orcs_primary_tcell",
        "gse278572_cd4_context",
        "weinstock_freimer_activated_cd4_ko",
    }
    assert all(row["replay"] for row in manifests)
    assert all(row["artifacts"] for row in manifests)
    assert all(
        len(artifact["sha256"]) == 64
        for row in manifests
        for artifact in row["artifacts"]
    )


def test_primary_only_preserves_existing_receipt_identity():
    result = evaluate_submission({
        "input_text": "IL7R\nCCR7\nPD-1\nNOTGENE",
        "filename": "genes.txt",
        "producer": "hackathon_team",
    })

    assert result["evidence_mode"] == "primary_only"
    assert result["receipt"]["receipt_id"] == "rcpt_480889b8bf8064b7"
    assert result["proposal_id"] == "proposal_8d210583ea0be79b"
    assert len(result["consulted_substrates"]) == 1
    assert len(result["dataset_verdicts"]) == 4


def test_all_frozen_keeps_primary_counts_and_returns_per_dataset_rows():
    primary = evaluate_submission(_request("primary_only"))
    result = evaluate_submission(_request("all_frozen"))
    by_key = {(row["gene"], row["substrate_id"]): row for row in result["dataset_verdicts"]}

    assert result["prospect"]["typed_status_counts"] == primary["prospect"]["typed_status_counts"]
    assert result["receipt"]["receipt_id"] != primary["receipt"]["receipt_id"]
    assert len(result["consulted_substrates"]) == 6
    assert len(result["dataset_verdicts"]) == 18
    assert by_key[("MED12", "weinstock_freimer_activated_cd4_ko")]["typed_status"] == "evidence_attached"
    assert by_key[("MED12", "weinstock_freimer_activated_cd4_ko")]["comparability"] == "orthogonal_activation_context"
    assert by_key[("MED12", "gse278572_cd4_context")]["typed_status"] == "evidence_attached"
    assert by_key[("IL7R", "weinstock_freimer_activated_cd4_ko")]["typed_status"] == "not_assayed"
    assert not any(
        row["typed_status"] == "contradicted" and row["substrate_id"] != "marson_cd4_activation"
        for row in result["dataset_verdicts"]
    )
    assert {row["name"] for row in result["receipt"]["artifacts"]} >= {
        "target_reach.csv",
        "source_manifest.json",
        "gse278572_comparator.json",
    }


def test_receipt_binds_manifest_and_dataset_evidence_mutations():
    result = evaluate_submission(_request("all_frozen"))
    receipt = result["receipt"]
    mutated = deepcopy(receipt)
    mutated["replay_metadata"]["request"]["dataset_verdicts"][0]["magnitude"] = 999999

    assert receipt_id_for(mutated) != receipt["receipt_id"]


def test_invalid_evidence_mode_fails_clearly():
    with pytest.raises(ValueError, match="evidence_mode"):
        evaluate_submission(_request("collapsed_consensus"))
