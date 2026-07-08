"""Public web data contract guardrails."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"


def test_frontier_json_uses_public_typed_class_names():
    data = json.loads(FRONTIER.read_text())
    text = json.dumps({
        "stats": data["stats"],
        "atlas": [{"cls": node["cls"]} for node in data["atlas"]],
    })

    assert "verified_non_regulator" not in text
    assert "reproduced_non_regulator" in data["stats"]["dist"]
    assert any(node["cls"] == "reproduced_non_regulator" for node in data["atlas"])


def test_frontier_json_embeds_pggt1b_evidence_capsule():
    data = json.loads(FRONTIER.read_text())
    capsule = data["pggt1b_deep_dive"]["evidence_capsule"]

    assert capsule["decision"] == "advance_to_orthogonal_assay"
    assert capsule["stimulated_to_rest_ratio"] == 17.22
    assert capsule["stimulated_to_k562_ratio"] == 3014.0
    assert capsule["evidence_ladder"][0]["status"] == "computationally_reproduced"
    assert capsule["evidence_ladder"][-1]["status"] == "evidence_attached"
    assert "proposal evidence" in capsule["missing_for_acceptance"][0]


def test_frontier_json_embeds_pggt1b_matrix_slice():
    data = json.loads(FRONTIER.read_text())
    matrix_slice = data["pggt1b_deep_dive"]["matrix_slice"]

    assert matrix_slice["condition"] == "Stim8hr"
    assert matrix_slice["status"] == "computationally_reproduced"
    assert matrix_slice["trust_boundary"] == "evidence_for_proposal"
    assert matrix_slice["n_thresholded_transcripts"] == 671
    assert matrix_slice["top_up"][0]["gene"] == "KLF2"
    assert matrix_slice["top_down"][0]["gene"] == "IL5"


def test_frontier_json_embeds_transfer_replay_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["transfer_replay_packet"]

    assert packet["status"] == "computationally_reproduced"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["counts"]["t_cell_regulators_compared"] == 377
    assert packet["rates"]["activation_specificity"]["rate"] == 0.8024
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_frontier_json_embeds_substrate_replay_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["substrate_replay_packet"]

    assert packet["status"] == "computationally_reproduced"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["counts"]["t_cell_regulators_compared"] == 377
    assert packet["substrate_classes"][0]["class"] == "shared_cellular_machinery"
    assert packet["substrate_classes"][1]["class"] == "t_cell_specific_regulation"
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_frontier_json_embeds_campaign_pressure_summary():
    data = json.loads(FRONTIER.read_text())
    summary = data["campaign_pressure_summary"]

    assert summary["status"] == "evidence_attached"
    assert summary["trust_boundary"] == "proposal_only"
    assert summary["accepted_state_mutations"] == 0
    assert summary["counts"]["claude_probe_rows"] == 8
    assert summary["counts"]["triage_rows"] == 4
    assert summary["gate_recommendations"]["gate_sufficient"] == 2
    assert "verified" not in json.dumps(summary).lower()
    assert "true" not in json.dumps(summary).lower()


if __name__ == "__main__":
    test_frontier_json_uses_public_typed_class_names()
    test_frontier_json_embeds_pggt1b_evidence_capsule()
    test_frontier_json_embeds_pggt1b_matrix_slice()
    test_frontier_json_embeds_transfer_replay_packet()
    test_frontier_json_embeds_substrate_replay_packet()
    test_frontier_json_embeds_campaign_pressure_summary()
    print("PASS: web data contract")
