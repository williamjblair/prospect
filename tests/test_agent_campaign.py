"""Agent campaign leaderboard tests.

The campaign expands the single signed agent hypothesis into a ranked set of
proposal-only hypotheses to test, using frozen Prospect lookups only.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.agent_campaign import build_campaign, write_campaign


def test_campaign_ranks_many_proposal_only_candidates():
    campaign = build_campaign(limit=20)
    rows = campaign["candidates"]
    by_gene = {r["gene"]: r for r in rows}

    assert campaign["status"] == "evidence_attached"
    assert campaign["acceptance"] is False
    assert campaign["trust_boundary"] == "proposal_only"
    assert len(rows) == 20
    assert rows[0]["gene"] == "PGGT1B"
    assert by_gene["PGGT1B"]["stim_max_de"] == 3014
    assert by_gene["PGGT1B"]["rank"] == 1
    assert by_gene["PGGT1B"]["status"] == "evidence_attached"
    assert "hypothesis to test" in by_gene["PGGT1B"]["rationale"]
    assert "verified" not in json.dumps(campaign).lower()
    assert "true" not in json.dumps(campaign).lower()
    assert by_gene["PGGT1B"]["priority_lane"] == "top wet-lab bet"
    assert by_gene["PGGT1B"]["primary_readout"] == "Stim8hr transcriptional program"
    assert "largest stimulated footprint" in by_gene["PGGT1B"]["why_interesting"]
    assert "proposal-only" in by_gene["PGGT1B"]["main_risk"]


def test_campaign_keeps_filters_and_evidence_atoms():
    rows = build_campaign(limit=20)["candidates"]
    genes = {r["gene"] for r in rows}

    assert "PDCD1" not in genes
    assert "CTLA4" not in genes
    assert "MED19" not in genes
    assert all(r["strongest_kd"] == "on-target KD" for r in rows)
    assert all(r["cross_cell_type"] == "cell-type-specific" for r in rows)
    assert all(r["known_regulon_targets"] == 0 for r in rows[:10])
    assert all(len(r["evidence"]) >= 4 for r in rows)
    assert {r["priority_lane"] for r in rows[:12]} >= {
        "top wet-lab bet",
        "late activation follow-up",
        "clean specificity",
    }
    assert all(r["review_summary"] for r in rows)
    assert all(r["what_would_weaken"] for r in rows)


def test_campaign_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "agent_campaign.json"
    out_csv = tmp_path / "agent_campaign.csv"
    out_doc = tmp_path / "AGENT_CAMPAIGN.md"

    write_campaign(out_json=out_json, out_csv=out_csv, out_doc=out_doc, limit=20)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["candidates"][0]["gene"] == "PGGT1B"
    assert "Agent campaign leaderboard" in doc
    assert "evidence_attached" in doc
    assert "proposal only" in doc
    assert "Review lane" in doc
    assert "What would weaken it" in doc
    assert "PGGT1B" in out_csv.read_text()


def test_agent_campaign_runs_as_a_script():
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "frontier", "agent_campaign.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "agent_campaign.json" in proc.stdout


if __name__ == "__main__":
    test_campaign_ranks_many_proposal_only_candidates()
    test_campaign_keeps_filters_and_evidence_atoms()
    test_campaign_writes_json_csv_and_markdown(__import__("pathlib").Path("/tmp/prospect-agent-campaign-test"))
    test_agent_campaign_runs_as_a_script()
    print("PASS: agent campaign")
