"""Judge packet tests."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cli.submit_pack import PUBLIC_ARTIFACTS
from frontier.judge_packet import build_packet, write_packet


def test_judge_packet_summarizes_live_replay_surface():
    packet = build_packet()

    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["trust_boundary"]["model_moves_accepted_state"] is False
    assert packet["trust_boundary"]["receipt_submission"] == "proposal_only"
    assert "./prospect verify" in packet["gate_commands"]
    assert "./prospect final-check" in packet["gate_commands"]
    assert "./prospect submit-smoke" in packet["gate_commands"]
    assert "./prospect submit-pack" in packet["gate_commands"]
    assert "./prospect demo-pack" in packet["gate_commands"]
    assert "./prospect release-manifest" in packet["gate_commands"]
    assert "python benchmark/mutation_pack.py" in packet["gate_commands"]
    assert "python tests/test_skill_parity.py" in packet["gate_commands"]
    assert packet["receipt_bridge_demo"]["command"] == "python examples/receipt_bridge_client.py"
    assert packet["receipt_bridge_demo"]["accepted"] is False
    assert packet["receipt_bridge_demo"]["next"] == "human_signature_required"
    assert packet["artifact_counts"]["findings"] == 5
    assert packet["artifact_counts"]["receipts"] == 6
    assert packet["artifact_counts"]["agent_campaign_candidates"] == 20
    assert packet["artifact_counts"]["campaign_review_rows"] == 20
    assert packet["artifact_counts"]["campaign_probe_rows"] == 20
    assert packet["artifact_counts"]["campaign_triage_rows"] == 11
    assert packet["artifact_counts"]["campaign_gate_probe_rows"] == 11
    assert packet["artifact_counts"]["campaign_pressure_rows"] == 20
    assert packet["artifact_counts"]["campaign_challenger_rows"] == 20
    assert packet["artifact_counts"]["campaign_challenger_primary_challenges"] == 1
    assert packet["artifact_counts"]["campaign_challenger_replacements"] == 1
    assert packet["artifact_counts"]["campaign_probe_audit_issues"] == 0
    assert packet["artifact_counts"]["validation_candidates"] == 5
    assert packet["artifact_counts"]["lab_packet_candidates"] == 5
    assert packet["artifact_counts"]["assay_operations_candidates"] == 5
    assert packet["artifact_counts"]["pilot_design_candidates"] == 5
    assert packet["artifact_counts"]["pilot_design_culture_arms"] == 90
    assert packet["artifact_counts"]["final_submission_public_artifacts"] == len(PUBLIC_ARTIFACTS)
    assert packet["artifact_counts"]["transfer_replay_rows"] == 377
    assert packet["artifact_counts"]["substrate_replay_rows"] == 377
    assert packet["artifact_counts"]["cross_substrate_discovery_rows"] == 11526
    assert packet["artifact_counts"]["cross_substrate_campaign_rows"] == 20
    assert packet["artifact_counts"]["donor_condition_replay_rows"] == 20
    assert packet["artifact_counts"]["donor_supported_campaign_rows"] == 13
    assert packet["artifact_counts"]["disease_genetics_overlay_rows"] == 20
    assert packet["artifact_counts"]["disease_genetics_context_rows"] == 10
    assert packet["artifact_counts"]["disease_genetics_genetic_context_rows"] == 4
    assert packet["artifact_counts"]["pggt1b_evidence_ladder_steps"] == 5
    assert packet["artifact_counts"]["pggt1b_matrix_slice_transcripts"] == 671
    assert packet["science_packet"]["campaign_probe"]["coverage"]["returned_decisions"] == 20
    assert packet["science_packet"]["campaign_probe"]["coverage"]["coverage_status"] == "complete"
    assert packet["science_packet"]["campaign_gate_probe"]["coverage"]["returned_decisions"] == 11
    assert packet["science_packet"]["campaign_gate_probe"]["coverage"]["requested_limit"] == 11
    assert packet["science_packet"]["campaign_gate_probe"]["coverage"]["coverage_status"] == "complete"
    assert packet["science_packet"]["campaign_pressure_summary"]["gate_probe_coverage"]["coverage_status"] == "complete"
    assert packet["science_packet"]["campaign_challenger_ledger"]["status"] == "evidence_attached"
    assert packet["science_packet"]["campaign_challenger_ledger"]["primary_panel_challenges"] == 1
    assert packet["science_packet"]["campaign_challenger_ledger"]["panel_delta"]["remove"] == ["RWDD2B"]
    assert packet["science_packet"]["campaign_challenger_ledger"]["panel_delta"]["add"] == ["CYB5RL"]
    assert packet["science_packet"]["campaign_probe_audit"]["passed"] == "yes"
    assert packet["science_packet"]["campaign_probe_audit"]["issue_count"] == 0
    assert packet["science_packet"]["pilot_design"]["status"] == "evidence_attached"
    assert packet["science_packet"]["pilot_design"]["culture_arms"] == 90
    assert packet["science_packet"]["cross_substrate_discovery"]["status"] == "computationally_reproduced"
    assert packet["science_packet"]["cross_substrate_discovery"]["class_counts"]["t_cell_specific_activation"] == 409
    assert packet["science_packet"]["cross_substrate_discovery"]["top_campaign_gene"] == "PGGT1B"
    assert packet["science_packet"]["donor_condition_replay"]["status"] == "computationally_reproduced"
    assert packet["science_packet"]["donor_condition_replay"]["donor_supported"] == 13
    assert packet["science_packet"]["donor_condition_replay"]["top_gene"] == "PGGT1B"
    assert packet["science_packet"]["disease_genetics_overlay"]["status"] == "evidence_attached"
    assert packet["science_packet"]["disease_genetics_overlay"]["local_perturbation_status"] == "computationally_reproduced"
    assert packet["science_packet"]["disease_genetics_overlay"]["context_rows"] == 10
    assert packet["science_packet"]["disease_genetics_overlay"]["genetic_context_rows"] == 4
    assert packet["science_packet"]["disease_genetics_overlay"]["top_gene"] == "PGGT1B"
    assert packet["typed_statuses"] == ["computationally_reproduced", "evidence_attached", "contradicted"]
    assert packet["public_data"] == PUBLIC_ARTIFACTS
    assert "true" not in json.dumps(packet).lower()
    assert "verified biology" not in json.dumps(packet).lower()


def test_judge_packet_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "judge_packet.json"
    out_doc = tmp_path / "JUDGE_PACKET.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["artifact_counts"]["findings"] == 5
    assert data["artifact_counts"]["campaign_review_rows"] == 20
    assert data["artifact_counts"]["campaign_probe_rows"] == 20
    assert data["artifact_counts"]["campaign_triage_rows"] == 11
    assert data["artifact_counts"]["campaign_gate_probe_rows"] == 11
    assert data["artifact_counts"]["campaign_pressure_rows"] == 20
    assert data["artifact_counts"]["campaign_challenger_rows"] == 20
    assert data["artifact_counts"]["campaign_challenger_primary_challenges"] == 1
    assert data["artifact_counts"]["campaign_challenger_replacements"] == 1
    assert data["artifact_counts"]["campaign_probe_audit_issues"] == 0
    assert data["artifact_counts"]["transfer_replay_rows"] == 377
    assert data["artifact_counts"]["substrate_replay_rows"] == 377
    assert data["artifact_counts"]["cross_substrate_discovery_rows"] == 11526
    assert data["artifact_counts"]["cross_substrate_campaign_rows"] == 20
    assert data["artifact_counts"]["donor_condition_replay_rows"] == 20
    assert data["artifact_counts"]["donor_supported_campaign_rows"] == 13
    assert data["artifact_counts"]["disease_genetics_overlay_rows"] == 20
    assert data["artifact_counts"]["disease_genetics_context_rows"] == 10
    assert data["artifact_counts"]["disease_genetics_genetic_context_rows"] == 4
    assert data["artifact_counts"]["assay_operations_candidates"] == 5
    assert data["artifact_counts"]["pilot_design_candidates"] == 5
    assert data["artifact_counts"]["pilot_design_culture_arms"] == 90
    assert data["artifact_counts"]["final_submission_public_artifacts"] == len(PUBLIC_ARTIFACTS)
    assert data["artifact_counts"]["pggt1b_matrix_slice_transcripts"] == 671
    assert data["science_packet"]["campaign_probe"]["coverage"]["returned_decisions"] == 20
    assert data["science_packet"]["campaign_probe"]["coverage"]["coverage_status"] == "complete"
    assert data["science_packet"]["campaign_gate_probe"]["coverage"]["coverage_status"] == "complete"
    assert data["science_packet"]["campaign_challenger_ledger"]["panel_delta"]["remove"] == ["RWDD2B"]
    assert data["science_packet"]["campaign_challenger_ledger"]["panel_delta"]["add"] == ["CYB5RL"]
    assert data["science_packet"]["campaign_probe_audit"]["passed"] == "yes"
    assert data["science_packet"]["campaign_probe_audit"]["issue_count"] == 0
    assert data["science_packet"]["pilot_design"]["candidate_count"] == 5
    assert data["science_packet"]["pilot_design"]["culture_arms"] == 90
    assert data["science_packet"]["cross_substrate_discovery"]["top_campaign_gene"] == "PGGT1B"
    assert data["science_packet"]["donor_condition_replay"]["top_gene"] == "PGGT1B"
    assert data["science_packet"]["disease_genetics_overlay"]["top_gene"] == "PGGT1B"
    assert data["science_packet"]["pggt1b_deep_dive"]["evidence_capsule"]["decision"] == "advance_to_orthogonal_assay"
    assert data["science_packet"]["pggt1b"]["matrix_slice_transcripts"] == 671
    assert "Judge packet" in doc
    assert "No model in the trust path" in doc
    assert "PGGT1B evidence capsule" in doc
    assert "Campaign gate probe" in doc
    assert "Campaign pressure summary" in doc
    assert "Campaign challenger ledger" in doc
    assert "Campaign probe audit issues" in doc
    assert "Transfer replay packet" in doc
    assert "Substrate replay packet" in doc
    assert "Cross-substrate discovery packet" in doc
    assert "Donor-condition replay packet" in doc
    assert "Disease-genetics overlay" in doc
    assert "Gladstone assay operations bundle" in doc
    assert "Gladstone pilot design" in doc
    assert "Final submission audit" in doc
    assert "`/data/judge_packet.json`" in doc
    assert "`/data/release_manifest.json`" in doc
    assert "matrix-slice transcripts" in doc
    assert "./prospect verify" in doc
    assert "./prospect submit-smoke" in doc
    assert "./prospect submit-pack" in doc
    assert "./prospect demo-pack" in doc
    assert "./prospect release-manifest" in doc
    assert "python examples/receipt_bridge_client.py" in doc
    assert "proposal only" in doc


def test_judge_packet_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "judge-pack"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "judge_packet.json" in proc.stdout


if __name__ == "__main__":
    test_judge_packet_summarizes_live_replay_surface()
    test_judge_packet_writes_json_and_markdown(__import__("pathlib").Path("/tmp/prospect-judge-packet-test"))
    test_judge_packet_runs_from_prospect_cli()
    print("PASS: judge packet")
