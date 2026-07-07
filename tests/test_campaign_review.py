"""Campaign review appendix tests.

The review appendix makes the proposal-only campaign leaderboard easier to
audit without moving any candidate into accepted state.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.campaign_review import build_review, write_review


def test_campaign_review_summarizes_proposal_only_campaign():
    review = build_review()

    assert review["status"] == "evidence_attached"
    assert review["trust_boundary"] == "proposal_only"
    assert review["acceptance"] is False
    assert review["campaign_id"].startswith("campaign_")
    assert review["candidate_count"] == 20
    assert review["top_gene"] == "PGGT1B"
    assert review["lane_counts"]["top wet-lab bet"] == 1
    assert review["lane_counts"]["late activation follow-up"] >= 1
    assert review["audit_questions"][0]["question"] == "Is there an on-target stimulated footprint?"
    assert "verified" not in json.dumps(review).lower()
    assert "true" not in json.dumps(review).lower()


def test_campaign_review_rows_bind_frozen_facts_and_stop_rules():
    rows = build_review()["rows"]
    pggt1b = rows[0]

    assert len(rows) == 20
    assert pggt1b["gene"] == "PGGT1B"
    assert pggt1b["stimulated_signal"] == "3014 DE at Stim8hr"
    assert pggt1b["specificity"] == "Rest 175 DE, K562 1 DE, RPE1 not measured"
    assert pggt1b["review_lane"] == "top wet-lab bet"
    assert pggt1b["decision"] == "advance_to_assay_design"
    assert any("failed on-target knockdown" in rule for rule in pggt1b["stop_rules"])
    assert all(row["status"] == "evidence_attached" for row in rows)
    assert all(row["trust_boundary"] == "proposal_only" for row in rows)


def test_campaign_review_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "agent_campaign_review.json"
    out_csv = tmp_path / "agent_campaign_review.csv"
    out_doc = tmp_path / "AGENT_CAMPAIGN_REVIEW.md"

    write_review(out_json=out_json, out_csv=out_csv, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["rows"][0]["gene"] == "PGGT1B"
    assert "Campaign review appendix" in doc
    assert "evidence_attached" in doc
    assert "proposal only" in doc
    assert "advance_to_assay_design" in out_csv.read_text()


def test_campaign_review_runs_as_cli_command():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "campaign-review"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "agent_campaign_review.json" in proc.stdout


def test_campaign_review_is_in_public_web_bundle():
    path = os.path.join(ROOT, "web", "public", "data", "frontier.json")
    data = json.loads(open(path).read())
    review = data["agent_campaign_review"]

    assert review["status"] == "evidence_attached"
    assert review["trust_boundary"] == "proposal_only"
    assert review["candidate_count"] == 20
    assert review["rows"][0]["gene"] == "PGGT1B"


if __name__ == "__main__":
    test_campaign_review_summarizes_proposal_only_campaign()
    test_campaign_review_rows_bind_frozen_facts_and_stop_rules()
    test_campaign_review_writes_json_csv_and_markdown(__import__("pathlib").Path("/tmp/prospect-campaign-review-test"))
    test_campaign_review_runs_as_cli_command()
    test_campaign_review_is_in_public_web_bundle()
    print("PASS: campaign review")
