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
    "discovery_campaign",
    "cross_validation",
    "flagship_module",
    "overclaim_counter",
    "lab_packet",
    "disease_genetics_overlay",
    "receipts",
    "receipt_bridge",
    "external_run_receipt_demo",
    "live_claim_rail",
    "cross_domain_benchmark",
    "lab_writeback_receipt",
    "claude_science_acceptance_demo",
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
    assert ("veri" + "fied") not in json.dumps(packet).lower()


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


def test_frontier_json_embeds_discovery_campaign_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["discovery_campaign"]

    assert packet["phase"] == "phase_1_novelty_at_scale"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["filter_counts"]["frontier_genes"] == 11526
    assert packet["filter_counts"]["cell_type_specific_replogle"] == 18
    assert packet["candidates"][0]["gene"] == "PGGT1B"
    assert packet["candidates"][0]["standard_t_cell_annotation"] is False
    assert ("veri" + "fied") not in json.dumps(packet).lower()


def test_frontier_json_embeds_cross_validation_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["cross_validation"]

    assert packet["phase"] == "phase_2_independent_cross_validation"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["counts"]["candidates_with_external_screen_hit"] == 4
    assert packet["counts"]["candidates_with_schmidt_non_hit"] == 18
    assert packet["counts"]["candidates_with_schmidt_orthogonal_phenotype"] == 18
    assert packet["counts"]["candidates_with_comparable_external_contradiction"] == 0
    assert packet["candidates"][0]["gene"] == "PGGT1B"
    assert packet["candidates"][0]["external_screen_summary"]["supporting_hits"] == ["shifrut_2018_1107"]
    assert packet["candidates"][0]["external_screen_summary"]["orthogonal_phenotypes"] == ["schmidt_2022_2427"]
    assert ("veri" + "fied") not in json.dumps(packet).lower()


def test_frontier_json_embeds_flagship_hypothesis_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["flagship_module"]
    hypothesis = packet["flagship_hypothesis"]

    assert packet["phase"] == "phase_3_single_gene_hypothesis"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert hypothesis["gene"] == "PGGT1B"
    assert hypothesis["rank"] == 1
    assert hypothesis["schmidt_status"] == "orthogonal_phenotype"
    assert hypothesis["refutation_experiment"]["perturbations"] == ["PGGT1B"]
    assert hypothesis["refutation_experiment"]["system"] == "stimulated primary human CD4+ T cells"
    assert {row["gene"] for row in packet["supported_alternatives"]} == {"CCDC22", "LETM2", "TNNC1"}
    assert ("veri" + "fied") not in json.dumps(packet).lower()


def test_frontier_json_embeds_overclaim_counter_packet():
    data = json.loads(FRONTIER.read_text())
    packet = data["overclaim_counter"]

    assert packet["phase"] == "phase_4_overclaim_counter"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["counts"]["model_contradicted_claims"] == 46
    assert packet["counts"]["phase1_refused_total"] == 11508
    assert packet["counts"]["phase2_without_external_screen_hit"] == 14
    assert packet["counts"]["phase2_schmidt_orthogonal_phenotypes"] == 18
    assert packet["flagship_boundary"]["gene"] == "PGGT1B"
    assert packet["flagship_boundary"]["claim_kind"] == "single_gene_hypothesis"
    assert ("veri" + "fied") not in json.dumps(packet).lower()


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


def test_frontier_json_embeds_claude_science_acceptance_demo():
    data = json.loads(FRONTIER.read_text())
    demo = data["claude_science_acceptance_demo"]

    assert demo["producer"] == "claude_science"
    assert demo["real_export"] is True
    assert demo["prospect"]["accepted"] is False
    assert demo["prospect"]["next"] == "human_signature_required"
    assert demo["prospect"]["typed_status_counts"] == {
        "genes": 52,
        "drivers": 12,
        "evidence_attached": 12,
        "passengers": 22,
        "associative_only": 22,
        "contradicted": 3,
        "not_assayed": 15,
    }
    assert demo["causal_rule"]["comparison"] == "driver_vs_passenger"
    assert {row["gene"] for row in demo["verdicts"] if row["typed_status"] == "contradicted"} == {"HAVCR2", "LAG3", "PDCD1"}
    assert demo["commands"]["claude_science"] == "python examples/claude_science_connector_client.py --json"
    assert demo["commands"]["generic"] == "python examples/prospect_connector_client.py --case openresearch --json"
    assert ("veri" + "fied") not in json.dumps(demo).lower()


def test_frontier_json_embeds_live_claim_rail():
    data = json.loads(FRONTIER.read_text())
    rail = data["live_claim_rail"]

    assert rail["gene"] == "PGGT1B"
    assert rail["status"] == "evidence_attached"
    assert rail["accepted_state"] is False
    assert rail["state_diff"]["model_can_apply"] is False
    assert rail["reproduce_command"] == "./prospect agent"


if __name__ == "__main__":
    test_frontier_json_uses_public_typed_class_names()
    test_frontier_json_keeps_only_the_consolidated_packet_surface()
    test_frontier_json_embeds_pggt1b_evidence_capsule()
    test_frontier_json_embeds_pggt1b_matrix_slice()
    test_frontier_json_embeds_disease_genetics_overlay_packet()
    test_frontier_json_embeds_agent_campaign_and_lab_packet()
    test_frontier_json_embeds_discovery_campaign_packet()
    test_frontier_json_embeds_cross_validation_packet()
    test_frontier_json_embeds_flagship_hypothesis_packet()
    test_frontier_json_embeds_overclaim_counter_packet()
    test_frontier_json_embeds_external_run_receipt_demo()
    test_frontier_json_embeds_live_claim_rail()
    print("PASS: web data contract")
