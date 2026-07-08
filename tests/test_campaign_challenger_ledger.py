"""Campaign challenger ledger tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.campaign_challenger_ledger import build_ledger, write_ledger


def test_campaign_challenger_ledger_reconciles_shipped_packets_without_acceptance():
    ledger = build_ledger()

    assert ledger["title"] == "Campaign challenger ledger"
    assert ledger["status"] == "evidence_attached"
    assert ledger["trust_boundary"] == "frozen_join_over_committed_packets"
    assert ledger["accepted_state_mutation"] == "none"
    assert ledger["model_in_trust_path"] == "no"
    assert ledger["method"]["replay_command"] == "./prospect campaign-challenger"
    assert ledger["public_artifact"] == "/data/campaign_challenger_ledger.json"
    assert ledger["counts"] == {
        "campaign_rows": 20,
        "current_primary_panel_rows": 5,
        "recommended_primary_panel_rows": 5,
        "primary_panel_challenges": 1,
        "replacement_candidates": 2,
        "retain_primary_panel": 4,
        "promote_if_capacity": 2,
        "contextual_priority": 1,
        "hold_for_review": 4,
        "demote_or_control": 8,
        "challenge_primary_panel": 1,
    }

    assert ledger["current_primary_panel"] == ["PGGT1B", "RCC1L", "MCAT", "RWDD2B", "CCDC22"]
    assert ledger["recommended_primary_panel"] == ["PGGT1B", "RCC1L", "MCAT", "CCDC22", "CYB5RL"]
    assert ledger["panel_delta"] == {
        "remove": ["RWDD2B"],
        "add": ["CYB5RL"],
        "changed": "yes",
    }

    rows = {row["gene"]: row for row in ledger["rows"]}
    assert rows["RWDD2B"]["challenger_action"] == "challenge_primary_panel"
    assert rows["RWDD2B"]["current_primary_panel"] == "yes"
    assert rows["RWDD2B"]["donor_replay_class"] == "donor_fragile"
    assert rows["RWDD2B"]["gate_recommendation"] == "lower_priority"
    assert rows["RWDD2B"]["recommended_change"] == "remove_from_primary_panel"
    assert rows["CYB5RL"]["challenger_action"] == "promote_if_capacity"
    assert rows["CYB5RL"]["recommended_change"] == "add_to_primary_panel"
    assert rows["CYB5RL"]["donor_replay_class"] == "donor_supported"
    assert rows["CYB5RL"]["gate_recommendation"] == "gate_sufficient"
    assert rows["SCO2"]["challenger_action"] == "contextual_priority"
    assert rows["SCO2"]["disease_overlay_class"] == "immune_or_hematologic_genetic_context"

    text = json.dumps(ledger).lower()
    assert "verified" not in text
    assert "true" not in text


def test_campaign_challenger_ledger_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_challenger_ledger.json"
    out_doc = tmp_path / "CAMPAIGN_CHALLENGER_LEDGER.md"

    write_ledger(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["recommended_primary_panel"] == ["PGGT1B", "RCC1L", "MCAT", "CCDC22", "CYB5RL"]
    assert "Campaign challenger ledger" in doc
    assert "RWDD2B" in doc
    assert "CYB5RL" in doc
    assert "No accepted state changes" in doc
    assert "./prospect campaign-challenger" in doc


def test_campaign_challenger_ledger_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "campaign-challenger"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "campaign_challenger_ledger.json" in proc.stdout


if __name__ == "__main__":
    test_campaign_challenger_ledger_reconciles_shipped_packets_without_acceptance()
    test_campaign_challenger_ledger_writes_json_and_markdown(Path("/tmp/prospect-campaign-challenger-ledger-test"))
    test_campaign_challenger_ledger_runs_from_prospect_cli()
    print("PASS: campaign challenger ledger")
