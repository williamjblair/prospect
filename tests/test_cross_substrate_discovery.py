"""Cross-substrate discovery packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.cross_substrate_discovery import build_packet, write_packet


def _by_gene(rows):
    return {row["gene"]: row for row in rows}


def test_cross_substrate_discovery_packet_classifies_frozen_rows():
    packet = build_packet()

    assert packet["title"] == "Cross-substrate discovery packet"
    assert packet["status"] == "computationally_reproduced"
    assert packet["trust_boundary"] == "frozen_counts_over_committed_tables"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["method"]["model_in_trust_path"] == "no"
    assert packet["method"]["accepted_state_mutation"] == "none"
    assert packet["method"]["replay_command"] == "./prospect cross-substrate-discovery"
    assert packet["thresholds"] == {
        "rest_high_de": 1000,
        "rest_tolerated_de_for_t_cell_candidate": 250,
        "stim_strong_de": 100,
        "marson_low_de_for_non_immune_only": 10,
        "non_immune_major_de": 25,
        "non_immune_low_de": 25,
    }
    assert packet["counts"]["marson_genes_considered"] == 11526
    assert packet["counts"]["overlap_k562"] == 8112
    assert packet["counts"]["overlap_rpe1"] == 1337
    assert packet["counts"]["overlap_any_non_immune"] == 8112
    assert packet["class_counts"] == {
        "shared_cellular_machinery": 80,
        "t_cell_specific_activation": 409,
        "non_immune_only_effect": 333,
        "ambiguous_or_not_tested": 10704,
    }
    exemplars = _by_gene(packet["exemplar_rows"])
    assert exemplars["MED19"]["cross_substrate_class"] == "shared_cellular_machinery"
    assert exemplars["MED19"]["rest_de"] == 2012
    assert exemplars["MED19"]["k562_de"] == 3716
    assert exemplars["MED19"]["rpe1_de"] == 3090
    assert exemplars["BCL10"]["cross_substrate_class"] == "t_cell_specific_activation"
    assert exemplars["BCL10"]["stim_max_de"] == 3456
    assert exemplars["PGGT1B"]["cross_substrate_class"] == "t_cell_specific_activation"
    assert exemplars["PGGT1B"]["campaign_rank"] == 1
    assert exemplars["RAC3"]["cross_substrate_class"] == "non_immune_only_effect"
    assert exemplars["LAT"]["cross_substrate_class"] == "ambiguous_or_not_tested"
    assert packet["top_rows"][0]["gene"] == "MED19"
    assert packet["campaign_intersections"][0]["gene"] == "PGGT1B"
    assert packet["campaign_intersections"][0]["cross_substrate_class"] == "t_cell_specific_activation"
    assert "wet-lab" in packet["limitations"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_cross_substrate_discovery_packet_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "cross_substrate_discovery.json"
    out_doc = tmp_path / "CROSS_SUBSTRATE_DISCOVERY.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "computationally_reproduced"
    assert data["class_counts"]["t_cell_specific_activation"] == 409
    assert "Cross-substrate discovery packet" in doc
    assert "computationally_reproduced" in doc
    assert "No accepted state changes" in doc
    assert "./prospect cross-substrate-discovery" in doc
    assert "PGGT1B" in doc
    assert "RAC3" in doc


def test_cross_substrate_discovery_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "cross-substrate-discovery"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "cross_substrate_discovery.json" in proc.stdout


if __name__ == "__main__":
    test_cross_substrate_discovery_packet_classifies_frozen_rows()
    test_cross_substrate_discovery_packet_writes_json_and_markdown(Path("/tmp/prospect-cross-substrate-discovery-test"))
    test_cross_substrate_discovery_runs_from_prospect_cli()
    print("PASS: cross-substrate discovery")
