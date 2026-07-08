"""Public web data contract guardrails."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"

KEPT_PACKET_KEYS = [
    "finding_index",
    "pggt1b_deep_dive",
    "agent_campaign",
    "lab_packet",
    "disease_genetics_overlay",
    "receipts",
    "receipt_bridge",
    "external_run_receipt_demo",
]

CUT_PACKET_KEYS = [
    "judge_packet",
    "agent_campaign_review",
    "campaign_agent_probe",
    "campaign_triage",
    "campaign_gate_probe",
    "campaign_pressure_summary",
    "campaign_challenger_ledger",
    "campaign_probe_audit",
    "assay_operations_bundle",
    "gladstone_pilot_design",
    "substrate_replay_packet",
    "cross_substrate_discovery",
    "donor_condition_replay",
    "transfer_replay_packet",
    "final_submission_audit",
    "release_manifest",
    "rendered_qa_packet",
    "validation",
]


def test_frontier_json_uses_public_typed_class_names():
    data = json.loads(FRONTIER.read_text())
    text = json.dumps({
        "stats": data["stats"],
        "atlas": [{"cls": node["cls"]} for node in data["atlas"]],
    })

    assert "verified_non_regulator" not in text
    assert "reproduced_non_regulator" in data["stats"]["dist"]
    assert any(node["cls"] == "reproduced_non_regulator" for node in data["atlas"])


def test_frontier_json_keeps_only_the_consolidated_packet_surface():
    data = json.loads(FRONTIER.read_text())
    for key in KEPT_PACKET_KEYS:
        assert key in data, f"missing kept packet key: {key}"
    for key in CUT_PACKET_KEYS:
        assert key not in data, f"cut packet key still embedded: {key}"


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


def test_frontier_json_embeds_disease_genetics_overlay_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["disease_genetics_overlay"]

    assert packet["status"] == "evidence_attached"
    assert packet["local_perturbation_status"] == "computationally_reproduced"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["counts"]["campaign_rows"] == 20
    assert packet["counts"]["immune_or_hematologic_context"] == 10
    assert packet["counts"]["immune_or_hematologic_genetic_context"] == 4
    assert packet["rows"][0]["gene"] == "PGGT1B"
    assert packet["rows"][0]["overlay_class"] == "immune_or_hematologic_non_genetic_context"
    assert "verified" not in json.dumps(packet).lower()


def test_frontier_json_embeds_agent_campaign_and_lab_packet():
    data = json.loads(FRONTIER.read_text())
    campaign = data["agent_campaign"]
    lab = data["lab_packet"]

    assert campaign["trust_boundary"] == "proposal_only"
    assert campaign["acceptance"] is False
    assert len(campaign["candidates"]) == 20
    assert lab["status"] == "evidence_attached"
    assert lab["acceptance"] is False
    assert len(lab["candidates"]) == 5


def test_frontier_json_embeds_external_run_receipt_demo():
    data = json.loads(FRONTIER.read_text())
    demo = data["external_run_receipt_demo"]

    assert demo["producer"] == "external_auto_research"
    assert demo["domain"] == "biology"
    assert demo["typed_status"] == "computationally_reproduced"
    assert demo["accepted"] is False
    assert demo["next"] == "human_signature_required"
    assert demo["engine_verdict"] == "supported"
    assert demo["command"] == "python examples/openresearch_receipt_client.py --json"
    assert demo["human_acceptance_requires"] == [
        "frozen_replay_passes",
        "reviewer_accepts_state_delta",
        "human_ed25519_signature",
    ]


if __name__ == "__main__":
    test_frontier_json_uses_public_typed_class_names()
    test_frontier_json_keeps_only_the_consolidated_packet_surface()
    test_frontier_json_embeds_pggt1b_evidence_capsule()
    test_frontier_json_embeds_pggt1b_matrix_slice()
    test_frontier_json_embeds_disease_genetics_overlay_packet()
    test_frontier_json_embeds_agent_campaign_and_lab_packet()
    test_frontier_json_embeds_external_run_receipt_demo()
    print("PASS: web data contract")
