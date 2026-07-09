"""Overview live-object rail contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_json_embeds_live_claim_rail():
    data = json.loads(FRONTIER.read_text())
    rail = data["live_claim_rail"]

    assert rail["title"] == "Follow one claim"
    assert rail["gene"] == "PGGT1B"
    assert rail["status"] == "evidence_attached"
    assert rail["receipt_id"].startswith("rcpt_")
    assert rail["accepted_state"] is False
    assert rail["state_diff"]["model_can_apply"] is False
    assert rail["state_diff"]["effect"] == "proposal_only_no_state_mutation"
    assert rail["reproduce_command"] == "./prospect agent"
    assert rail["open_obligation"] == "orthogonal wet-lab evidence before accepted biological state"
    assert rail["next_task"] == "run stimulated primary CD4+ follow-up assay"


def test_overview_surfaces_live_claim_rail():
    source = PAGE.read_text()

    assert "LiveClaimRail" in source
    assert "Follow one claim" in source
    assert "review result" in source
    assert "missing evidence" in source
    assert "next_task" in source
    assert "reviewable, but not accepted biology" in source


if __name__ == "__main__":
    test_frontier_json_embeds_live_claim_rail()
    test_overview_surfaces_live_claim_rail()
    print("PASS: live claim rail")
