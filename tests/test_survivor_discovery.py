"""Survivor discovery packet contracts."""
from __future__ import annotations

import json
from pathlib import Path

from frontier.survivor_discovery import build_survivor_discovery

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_survivor_discovery_keeps_three_distinct_hypotheses():
    packet = build_survivor_discovery()

    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["source_counts"]["atlas_genes"] == 11526
    assert packet["source_counts"]["leaderboard_candidates_scored"] == 2734
    assert packet["source_counts"]["survivors"] == 3
    assert [row["gene"] for row in packet["survivors"]] == ["PGGT1B", "CCDC22", "LETM2"]
    assert "no settled module" in packet["what_is_not_claimed"]


def test_survivor_discovery_survivors_have_kill_and_assay_records():
    packet = build_survivor_discovery()

    for row in packet["survivors"]:
        assert row["typed_status"] == "evidence_attached"
        assert row["accepted"] is False
        assert row["orthogonal_dataset_count"] >= 5
        assert len(row["kill_attempts"]) == 5
        assert all(kill["result"] == "survives_current_frozen_evidence" for kill in row["kill_attempts"])
        assert "CRISPRi knockdown" in row["falsifiable_experiment"]["intervention"]
        assert "refutes_if" in row["falsifiable_experiment"]


def test_survivor_discovery_mechanisms_are_gene_specific():
    packet = build_survivor_discovery()
    by_gene = {row["gene"]: row for row in packet["survivors"]}

    assert "small-GTPase" in by_gene["PGGT1B"]["mechanism"]
    assert "COMMD" in by_gene["CCDC22"]["mechanism"]
    assert "weaker" in by_gene["LETM2"]["mechanism"]
    assert by_gene["PGGT1B"]["strongest_de"] == 3014
    assert by_gene["CCDC22"]["strongest_de"] == 619
    assert by_gene["LETM2"]["strongest_de"] == 386


def test_survivor_discovery_written_artifacts_are_proposal_only():
    packet = json.loads((DATA / "survivor_discovery.json").read_text())
    doc = (ROOT / "docs" / "SURVIVOR_DISCOVERY.md").read_text()

    assert packet["accepted"] is False
    assert "accepted=false" in doc
    assert "Computation over released data, not wet-lab or clinical truth." in doc
    assert "settled module" in doc
    assert "/data/survivor_discovery.json" in doc
    assert "\u2014" not in doc
