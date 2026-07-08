"""Transfer replay packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.transfer_replay import build_packet, write_packet


def test_transfer_replay_packet_summarizes_three_frozen_tables():
    packet = build_packet()

    assert packet["title"] == "Transfer replay packet"
    assert packet["status"] == "computationally_reproduced"
    assert packet["trust_boundary"] == "frozen_checkers_over_frozen_tables"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["signed_frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["source_finding_kind"] == "cross_cell_type_transfer"
    assert packet["source_finding_cid"].startswith("cid_")
    assert packet["datasets"] == [
        "marson2025_cd4_perturbseq",
        "replogle2022_k562_gwps",
        "replogle2022_rpe1",
    ]
    assert packet["method"]["claim_shape"] == "major_regulator"
    assert packet["method"]["model_in_trust_path"] == "no"
    assert packet["method"]["replay_command"] == "./prospect transfer-replay"
    assert packet["counts"]["t_cell_regulators_compared"] == 377
    assert packet["counts"]["essentiality_genes"] == 129
    assert packet["counts"]["activation_or_effector_genes"] == 248
    assert packet["rates"]["essentiality_replication"]["rate"] == 0.5426
    assert packet["rates"]["activation_specificity"]["rate"] == 0.8024
    assert "MED19" in packet["exemplars"]["housekeeping"]
    assert "BCL10" in packet["exemplars"]["immune_specific"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_transfer_replay_packet_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "transfer_replay_packet.json"
    out_doc = tmp_path / "TRANSFER_REPLAY_PACKET.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "computationally_reproduced"
    assert data["counts"]["t_cell_regulators_compared"] == 377
    assert "Transfer replay packet" in doc
    assert "computationally_reproduced" in doc
    assert "No accepted state changes" in doc
    assert "./prospect transfer-replay" in doc


def test_transfer_replay_packet_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "transfer-replay"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "transfer_replay_packet.json" in proc.stdout


if __name__ == "__main__":
    test_transfer_replay_packet_summarizes_three_frozen_tables()
    test_transfer_replay_packet_writes_json_and_markdown(Path("/tmp/prospect-transfer-replay-test"))
    test_transfer_replay_packet_runs_from_prospect_cli()
    print("PASS: transfer replay packet")
