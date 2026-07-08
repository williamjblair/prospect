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


if __name__ == "__main__":
    test_frontier_json_uses_public_typed_class_names()
    test_frontier_json_embeds_pggt1b_evidence_capsule()
    test_frontier_json_embeds_pggt1b_matrix_slice()
    print("PASS: web data contract")
