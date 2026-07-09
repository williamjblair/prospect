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
    "overclaim_counter",
    "receipts",
    "receipt_bridge",
    "external_run_receipt_demo",
    "claude_science_acceptance_demo",
    "pggt1b_defended_evidence",
    "substrate_coverage_report",
]

CUT_PACKET_KEYS = [
    "agent_campaign",
    "discovery_campaign",
    "cross_validation",
    "flagship_module",
    "lab_packet",
    "disease_genetics_overlay",
    "lab_writeback_receipt",
    "defended_discovery_endgame_preregistration",
    "pggt1b_endgame_decision",
    "defended_discovery_endgame_result",
    "pggt1b_matrix_slice",
    "public_robustness_fuzz",
    "overnight_preregistration",
    "overnight_genome_wide_atlas",
    "overnight_literature_claims",
    "overnight_literature_audit",
    "overnight_defended_leaderboard",
    "exhaustive_compute_preregistration",
    "exhaustive_literature_audit",
    "exhaustive_coverage_preregistration",
    "survivor_discovery",
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


def test_public_receipt_projection_never_launders_legacy_root_attestations():
    data = json.loads(FRONTIER.read_text())
    receipts = data["receipts"]

    assert receipts
    assert all(receipt["accepted"] is False for receipt in receipts)
    assert all(receipt["legacy_attestation"] is True for receipt in receipts)
    assert all(receipt["covered_root"] for receipt in receipts)
    assert next(receipt for receipt in receipts if receipt["kind"] == "hypothesis")["status"] == "evidence_attached"
    assert next(receipt for receipt in receipts if receipt["kind"] == "regulator_vs_effector")["status"] == "computationally_reproduced"
    text = json.dumps(receipts).lower()
    for phrase in [
        "not immune biology",
        "independent cells validate",
        "data overrules the literature",
        "cell-type-specific regulator",
    ]:
        assert phrase not in text


def test_public_acceptance_service_url_is_sanitized_before_link_construction():
    source = (ROOT / "web" / "app" / "page.tsx").read_text()
    assert 'NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL || "").trim().replace(/\\/+$/, "")' in source


def test_frontier_json_embeds_pggt1b_evidence_capsule():
    data = json.loads(FRONTIER.read_text())
    capsule = data["pggt1b_deep_dive"]["evidence_capsule"]

    assert capsule["decision"] == "advance_to_orthogonal_assay"
    assert capsule["stimulated_to_rest_ratio"] == 17.22
    assert capsule["stimulated_to_k562_ratio"] == 3014.0
    assert capsule["evidence_ladder"][0]["status"] == "computationally_reproduced"
    assert capsule["evidence_ladder"][-1]["status"] == "evidence_attached"
    assert "proposal evidence" in capsule["missing_for_acceptance"][0]


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
        "passengers": 25,
        "associative_only": 25,
        "contradicted": 0,
        "not_assayed": 15,
    }
    assert demo["causal_rule"]["comparison"] == "driver_vs_passenger"
    assert not [row for row in demo["verdicts"] if row["typed_status"] == "contradicted"]
    assert {row["gene"] for row in demo["verdicts"] if row["typed_status"] == "associative_only"} >= {"HAVCR2", "LAG3", "PDCD1"}
    assert demo["commands"]["claude_science"] == "python examples/claude_science_connector_client.py --json"
    assert demo["commands"]["generic"] == "python examples/prospect_connector_client.py --case openresearch --json"
    assert ("veri" + "fied") not in json.dumps(demo).lower()


def test_frontier_json_embeds_pggt1b_defended_evidence():
    data = json.loads(FRONTIER.read_text())
    packet = data["pggt1b_defended_evidence"]

    assert packet["gene"] == "PGGT1B"
    assert packet["accepted"] is False
    assert packet["status"] == "evidence_attached"
    assert packet["orthogonal_public_dataset_count"] >= 5
    assert packet["wet_lab_protocol"]["minimum_donors"] >= 3
    assert "computation over released data" in packet["honest_ceiling"].lower()


def test_frontier_json_embeds_substrate_coverage_report():
    data = json.loads(FRONTIER.read_text())
    report = data["substrate_coverage_report"]

    assert report["accepted"] is False
    coverage = report["coverage"]["sade_feldman_signature"]
    assert coverage["before"]["not_assayed"] == 15
    assert coverage["after"]["not_assayed"] == 5
    assert "Computation over released data" in report["ceiling"]


if __name__ == "__main__":
    test_frontier_json_uses_public_typed_class_names()
    test_frontier_json_keeps_only_the_consolidated_packet_surface()
    test_public_receipt_projection_never_launders_legacy_root_attestations()
    test_public_acceptance_service_url_is_sanitized_before_link_construction()
    test_frontier_json_embeds_pggt1b_evidence_capsule()
    test_frontier_json_embeds_overclaim_counter_packet()
    test_frontier_json_embeds_external_run_receipt_demo()
    test_frontier_json_embeds_claude_science_acceptance_demo()
    test_frontier_json_embeds_pggt1b_defended_evidence()
    test_frontier_json_embeds_substrate_coverage_report()
    print("PASS: web data contract")
