"""Campaign disagreement triage tests.

The triage layer turns Claude-vs-deterministic disagreement into lab-facing
gates without letting the model advance accepted state.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.campaign_triage import build_triage, write_triage


def test_campaign_triage_turns_more_aggressive_probe_rows_into_assay_gates():
    triage = build_triage()
    rows = triage["rows"]
    by_gene = {row["gene"]: row for row in rows}

    assert triage["title"] == "Campaign disagreement triage"
    assert triage["status"] == "evidence_attached"
    assert triage["trust_boundary"] == "proposal_only"
    assert triage["acceptance"] is False
    assert triage["source_probe_id"].startswith("campaign_probe_")
    assert triage["summary"]["more_aggressive"] == 3
    assert [row["gene"] for row in rows] == ["RCC1L", "RWDD2B", "CCDC22"]
    assert by_gene["RCC1L"]["deterministic_decision"] == "hold_as_ranked_backup"
    assert by_gene["RCC1L"]["agent_recommendation"] == "advance_to_assay_design"
    assert by_gene["RCC1L"]["triage_decision"] == "secondary_assay_queue"
    assert "orthogonal knockdown" in by_gene["RCC1L"]["assay_gate"]
    assert "model disagreement" in by_gene["RWDD2B"]["reason_to_hold"].lower()
    assert all(row["status"] == "evidence_attached" for row in rows)
    assert all(row["trust_boundary"] == "proposal_only" for row in rows)
    assert "verified" not in json.dumps(triage).lower()
    assert "true" not in json.dumps(triage).lower()


def test_campaign_triage_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_triage.json"
    out_csv = tmp_path / "campaign_triage.csv"
    out_doc = tmp_path / "CAMPAIGN_TRIAGE.md"

    triage = write_triage(out_json=out_json, out_csv=out_csv, out_doc=out_doc)

    doc = out_doc.read_text()
    assert triage["rows"][0]["gene"] == "RCC1L"
    assert "Campaign disagreement triage" in doc
    assert "proposal only" in doc
    assert "RCC1L" in out_csv.read_text()
    assert json.loads(out_json.read_text())["summary"]["more_aggressive"] == 3


def test_campaign_triage_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "campaign-triage"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "campaign_triage.json" in proc.stdout


def test_campaign_triage_is_in_public_web_bundle():
    data = json.loads((ROOT / "web" / "public" / "data" / "frontier.json").read_text())
    triage = data["campaign_triage"]

    assert triage["status"] == "evidence_attached"
    assert triage["trust_boundary"] == "proposal_only"
    assert triage["acceptance"] is False
    assert triage["rows"][0]["gene"] == "RCC1L"


def test_campaign_triage_is_visible_in_agent_tab():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    gen_data = (ROOT / "web" / "gen_data.py").read_text()

    assert "campaign_triage" in gen_data
    assert "CampaignDisagreementTriage" in page
    assert "Campaign disagreement triage" in page
    assert "/data/campaign_triage.json" in page
    assert "d.campaign_triage" in page


if __name__ == "__main__":
    test_campaign_triage_turns_more_aggressive_probe_rows_into_assay_gates()
    test_campaign_triage_writes_json_csv_and_markdown(Path("/tmp/prospect-campaign-triage-test"))
    test_campaign_triage_runs_from_prospect_cli()
    test_campaign_triage_is_in_public_web_bundle()
    test_campaign_triage_is_visible_in_agent_tab()
    print("PASS: campaign disagreement triage")
