"""Whole-frontier discovery campaign tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.discovery_campaign import build_discovery_campaign, write_discovery_campaign


def test_discovery_campaign_ranks_the_whole_frontier():
    packet = build_discovery_campaign(limit=50)
    counts = packet["filter_counts"]
    rows = packet["candidates"]

    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["replayability"] == "attested"
    assert packet["candidate_set_id"].startswith("discovery_")
    assert packet["reproduce_command"] == "./prospect discovery-campaign"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert counts == {
        "frontier_genes": 11526,
        "condition_specific_regulator": 3463,
        "noncanonical_condition_specific": 3440,
        "non_artifact_non_activation": 3302,
        "on_target_stimulated": 3175,
        "strong_stimulated_effect": 60,
        "rest_ceiling": 44,
        "collectri_absent": 40,
        "cell_type_specific_replogle": 18,
    }
    assert len(rows) == 18
    assert rows[0]["rank"] == 1
    assert rows[0]["gene"] == "PGGT1B"
    assert rows[0]["stim_max_de"] == 3014
    assert rows[0]["known_regulon_targets"] == 0
    assert rows[0]["standard_t_cell_annotation"] is False
    assert rows[0]["cross_cell_type"] == "cell-type-specific"
    assert all(row["status"] == "evidence_attached" for row in rows)
    assert all(row["known_regulon_targets"] == 0 for row in rows)
    assert all(row["standard_t_cell_annotation"] is False for row in rows)
    assert all(row["trust_boundary"] == "proposal_only" for row in rows)


def test_discovery_campaign_records_refusals_and_sources():
    packet = build_discovery_campaign(limit=50)

    assert packet["source_artifacts"] == {
        "frontier_backbone": "examples/data/atlas_backbone.json",
        "replogle_k562": "examples/data/replogle_k562_de.csv",
        "replogle_rpe1": "examples/data/replogle_rpe1_de.csv",
        "collectri": "examples/data/collectri_human.csv",
        "standard_t_cell_annotations": "loop.find_surprises.CANON",
    }
    assert packet["refusal_counts"]["not_condition_specific"] == 8063
    assert packet["refusal_counts"]["standard_t_cell_annotation"] == 23
    assert packet["refusal_counts"]["artifact_or_activation_module"] == 138
    assert packet["refusal_counts"]["not_on_target_stimulated"] == 127
    assert packet["refusal_counts"]["weak_stimulated_effect"] == 3115
    assert packet["refusal_counts"]["rest_above_ceiling"] == 16
    assert packet["refusal_counts"]["collectri_present"] == 4
    assert packet["refusal_counts"]["non_immune_transfer_effect"] == 22
    assert packet["phase"] == "phase_1_novelty_at_scale"
    assert "hypothesis" in packet["claim"].lower()
    assert "human CD4+ T-cell activation" in packet["claim"]


def test_discovery_campaign_writes_packet_csv_and_markdown(tmp_path):
    out_json = tmp_path / "discovery_campaign.json"
    out_csv = tmp_path / "discovery_candidates.csv"
    out_doc = tmp_path / "DISCOVERY_CAMPAIGN.md"

    packet = write_discovery_campaign(out_json=out_json, out_csv=out_csv, out_doc=out_doc, limit=50)
    doc = out_doc.read_text()
    text = json.dumps(packet).lower() + doc.lower()

    assert packet["candidates"][0]["gene"] == "PGGT1B"
    assert "Phase 1 discovery campaign" in doc
    assert "11,526" in doc
    assert "18" in doc
    assert "computation over released data, not wet-lab or clinical truth" in doc
    assert "PGGT1B" in out_csv.read_text()
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text
    assert "\u2014" not in doc


def test_discovery_campaign_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "discovery-campaign"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "discovery_campaign.json" in proc.stdout


if __name__ == "__main__":
    test_discovery_campaign_ranks_the_whole_frontier()
    test_discovery_campaign_records_refusals_and_sources()
    test_discovery_campaign_writes_packet_csv_and_markdown(Path("/tmp/prospect-discovery-campaign-test"))
    test_discovery_campaign_runs_from_cli()
    print("PASS: discovery campaign")
