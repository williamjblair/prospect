"""Substrate replay packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.substrate_replay import build_packet, write_packet


def test_substrate_replay_packet_summarizes_protocol_generalization():
    packet = build_packet()

    assert packet["title"] == "Substrate replay packet"
    assert packet["status"] == "computationally_reproduced"
    assert packet["trust_boundary"] == "frozen_checkers_over_frozen_tables"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["signed_frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["method"]["replay_command"] == "./prospect substrate-replay"
    assert packet["method"]["model_in_trust_path"] == "no"
    assert packet["method"]["accepted_state_mutation"] == "none"
    assert packet["datasets"] == [
        {"id": "marson2025_cd4_perturbseq", "substrate": "primary_human_cd4_t_cells"},
        {"id": "replogle2022_k562_gwps", "substrate": "k562_non_immune_cell_line"},
        {"id": "replogle2022_rpe1", "substrate": "rpe1_non_immune_cell_line"},
    ]
    assert packet["counts"]["t_cell_regulators_compared"] == 377
    assert packet["counts"]["essentiality_artifact_regulators"] == 129
    assert packet["counts"]["activation_or_effector_regulators"] == 248
    assert packet["rates"]["essentiality_replication"]["rate"] == 0.5426
    assert packet["rates"]["activation_specificity"]["rate"] == 0.8024
    assert packet["substrate_classes"][0]["class"] == "shared_cellular_machinery"
    assert packet["substrate_classes"][0]["example_genes"][0]["gene"] == "MED19"
    assert packet["substrate_classes"][1]["class"] == "t_cell_specific_regulation"
    assert packet["substrate_classes"][1]["example_genes"][0]["gene"] == "BCL10"
    assert packet["replay_rows"][0]["gene"] == "MED19"
    assert packet["replay_rows"][1]["gene"] == "BCL10"
    assert "wet-lab" in packet["limitations"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_substrate_replay_packet_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "substrate_replay_packet.json"
    out_doc = tmp_path / "SUBSTRATE_REPLAY_PACKET.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "computationally_reproduced"
    assert data["counts"]["t_cell_regulators_compared"] == 377
    assert "Substrate replay packet" in doc
    assert "computationally_reproduced" in doc
    assert "No accepted state changes" in doc
    assert "./prospect substrate-replay" in doc
    assert "primary human CD4+ T cells" in doc


def test_substrate_replay_packet_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "substrate-replay"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "substrate_replay_packet.json" in proc.stdout


if __name__ == "__main__":
    test_substrate_replay_packet_summarizes_protocol_generalization()
    test_substrate_replay_packet_writes_json_and_markdown(Path("/tmp/prospect-substrate-replay-test"))
    test_substrate_replay_packet_runs_from_prospect_cli()
    print("PASS: substrate replay packet")
