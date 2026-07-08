"""Wet-lab assay packet tests."""
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.lab_packet import build_lab_packet, write_lab_packet


def test_lab_packet_builds_assay_ready_rows_without_acceptance():
    packet = build_lab_packet(limit=5)
    rows = packet["candidates"]
    pg = rows[0]

    assert packet["title"] == "Wet-lab assay packet"
    assert packet["status"] == "evidence_attached"
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["acceptance"] is False
    assert len(rows) == 5
    assert [row["gene"] for row in rows] == ["PGGT1B", "RCC1L", "MCAT", "RWDD2B", "CCDC22"]
    assert packet["source"].startswith("validation-sheet ranked candidates")
    assert packet["method"]["candidate_source"] == "frontier.validation_sheet.rank_candidates"
    assert pg["gene"] == "PGGT1B"
    assert pg["status"] == "evidence_attached"
    assert pg["intervention"] == "CRISPRi knockdown"
    assert "stimulated primary CD4+ T cells" in pg["primary_readout"]
    assert "non-targeting guide" in pg["negative_controls"]
    assert "VAV1" in pg["positive_controls"]
    assert "broad non-immune effect" in pg["exclusion_criteria"]
    assert "/data/frontier.json" in pg["replay_links"]
    assert "/data/agent_campaign.json" in pg["replay_links"]
    assert "/data/campaign_challenger_ledger.json" not in pg["replay_links"]
    assert "verified" not in json.dumps(packet).lower()


def test_lab_packet_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "lab_packet.json"
    out_csv = tmp_path / "lab_packet.csv"
    out_doc = tmp_path / "LAB_PACKET.md"

    packet = write_lab_packet(out_json=out_json, out_csv=out_csv, out_doc=out_doc, limit=5)

    data = json.loads(out_json.read_text())
    csv_rows = list(csv.DictReader(out_csv.open()))
    doc = out_doc.read_text()
    assert packet["candidates"][0]["gene"] == "PGGT1B"
    assert data["candidates"][0]["gene"] == "PGGT1B"
    assert csv_rows[0]["gene"] == "PGGT1B"
    assert [row["gene"] for row in data["candidates"]] == ["PGGT1B", "RCC1L", "MCAT", "RWDD2B", "CCDC22"]
    assert "Wet-lab assay packet" in doc
    assert "evidence_attached" in doc
    assert "proposal only" in doc


def test_lab_packet_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "lab-pack"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "lab_packet.json" in proc.stdout


if __name__ == "__main__":
    test_lab_packet_builds_assay_ready_rows_without_acceptance()
    test_lab_packet_writes_json_csv_and_markdown(__import__("pathlib").Path("/tmp/prospect-lab-packet-test"))
    test_lab_packet_runs_from_prospect_cli()
    print("PASS: wet-lab assay packet")
