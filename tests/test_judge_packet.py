"""Judge packet tests."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.judge_packet import build_packet, write_packet


def test_judge_packet_summarizes_live_replay_surface():
    packet = build_packet()

    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["trust_boundary"]["model_moves_accepted_state"] is False
    assert packet["trust_boundary"]["receipt_submission"] == "proposal_only"
    assert "./prospect verify" in packet["gate_commands"]
    assert "python benchmark/mutation_pack.py" in packet["gate_commands"]
    assert "python tests/test_skill_parity.py" in packet["gate_commands"]
    assert packet["artifact_counts"]["findings"] == 5
    assert packet["artifact_counts"]["receipts"] == 6
    assert packet["artifact_counts"]["agent_campaign_candidates"] == 20
    assert packet["artifact_counts"]["campaign_review_rows"] == 20
    assert packet["artifact_counts"]["validation_candidates"] == 5
    assert packet["artifact_counts"]["lab_packet_candidates"] == 5
    assert packet["typed_statuses"] == ["computationally_reproduced", "evidence_attached", "contradicted"]
    assert "/data/frontier.json" in packet["public_data"]
    assert "/data/lab_packet.json" in packet["public_data"]
    assert "/data/agent_campaign_review.json" in packet["public_data"]
    assert "/data/receipt_bridge/receipt_contract.json" in packet["public_data"]
    assert "/data/receipt_bridge/receipt_manifest.json" in packet["public_data"]
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
    assert "Judge packet" in doc
    assert "No model in the trust path" in doc
    assert "./prospect verify" in doc
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
