"""UI data contract for the defended CCDC22 proposal."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_json_embeds_defended_discovery_packets():
    data = json.loads(FRONTIER.read_text())

    ccdc22 = data["ccdc22_defended_evidence"]
    ledger = data["defended_candidate_decisions"]

    assert ccdc22["gene"] == "CCDC22"
    assert ccdc22["status"] == "evidence_attached"
    assert ccdc22["accepted"] is False
    assert ccdc22["defended_discovery_status"] == "computational_bar_cleared_pending_human_key"
    assert ccdc22["orthogonal_public_dataset_count"] == 7
    assert ccdc22["frozen_external_context_count"] == 10
    assert sum(1 for row in ccdc22["support_audit"] if row["counts_for_full_bar"]) == 7
    assert ledger["campaign_state"] == "candidate_hold_pending_human_key"
    assert ledger["held_candidate"]["gene"] == "CCDC22"


def test_overview_contains_defended_ccdc22_panel():
    page = PAGE.read_text()

    assert "CCDC22DefendedPanel" in page
    assert "computational bar cleared, pending human key" in page
    assert "CCDC22 defended proposal" in page
    assert "counted support rows" in page
    assert "non-counted context" in page


if __name__ == "__main__":
    test_frontier_json_embeds_defended_discovery_packets()
    test_overview_contains_defended_ccdc22_panel()
