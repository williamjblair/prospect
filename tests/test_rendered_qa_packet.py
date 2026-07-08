"""Rendered QA packet contract for the final judge path."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.rendered_qa import build_packet, write_packet


def test_rendered_qa_packet_names_browser_path_without_overclaiming():
    packet = build_packet()

    assert packet["title"] == "Prospect rendered QA packet"
    assert packet["status"] == "evidence_attached"
    assert packet["production_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["local_url"] == "http://localhost:8124"
    assert packet["avoid_port"] == 3000
    assert packet["trust_boundary"]["model_in_trust_path"] == "no"
    assert packet["trust_boundary"]["accepted_state_mutations"] == 0
    assert packet["automation_claim"] == "manual_browser_checklist"
    assert packet["public_artifact"] == "/data/rendered_qa_packet.json"
    assert len(packet["viewports"]) == 2
    assert packet["viewports"][0]["name"] == "desktop"
    assert packet["viewports"][1]["name"] == "mobile"

    tabs = {item["tab"]: item for item in packet["tabs"]}
    assert tabs["Overview"]["must_show"] == ["Opening claim checks", "48%", "Judge packet"]
    assert tabs["Findings"]["must_show"] == ["Scannable findings index", "Substrate replay packet", "MED19"]
    assert tabs["Frontier"]["must_show"] == ["Executable bridge path", "accepted=false", "human_signature_required"]
    assert tabs["Agent"]["must_show"] == ["Campaign pressure summary", "Gladstone assay operations bundle", "PGGT1B"]
    assert "./prospect submit-smoke" in packet["evidence_commands"]
    assert "./prospect final-check" in packet["evidence_commands"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_rendered_qa_packet_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "rendered_qa_packet.json"
    out_doc = tmp_path / "RENDERED_QA_PACKET.md"

    data = write_packet(out_json=out_json, out_doc=out_doc)

    doc = out_doc.read_text()
    assert data["public_artifact"] == "/data/rendered_qa_packet.json"
    assert "Prospect rendered QA packet" in doc
    assert "Manual browser checklist" in doc
    assert "http://localhost:8124" in doc
    assert "Avoid local port: `3000`" in doc
    assert "Campaign pressure summary" in doc
    assert "./prospect submit-smoke" in doc


def test_rendered_qa_packet_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "rendered-qa"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "rendered_qa_packet.json" in proc.stdout


if __name__ == "__main__":
    test_rendered_qa_packet_names_browser_path_without_overclaiming()
    test_rendered_qa_packet_writes_json_and_markdown(Path("/tmp/prospect-rendered-qa-test"))
    test_rendered_qa_packet_runs_from_prospect_cli()
    print("PASS: rendered QA packet")
