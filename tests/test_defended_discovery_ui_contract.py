"""UI data contract for the defended discovery endgame outcome."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_json_embeds_defended_discovery_endgame_packets():
    data = json.loads(FRONTIER.read_text())

    exhaustion = data["defended_discovery_endgame_exhaustion"]

    assert exhaustion["outcome"] == "honest_exhaustion"
    assert exhaustion["accepted"] is False
    assert exhaustion["candidate_count"] == 18
    assert exhaustion["cleared_count"] == 0
    assert exhaustion["common_blockers"] == [
        {
            "rung": "cell_type_specificity",
            "typed_detail": "rpe1_not_assayed",
            "affected_candidates": 18,
        }
    ]
    assert exhaustion["candidate_decisions"][0]["gene"] == "PGGT1B"
    assert exhaustion["candidate_decisions"][4]["gene"] == "CCDC22"
    assert exhaustion["candidate_decisions"][4]["decision"] == "not_cleared_full_bar"


def test_overview_contains_endgame_exhaustion_panel():
    page = PAGE.read_text()

    assert "EndgameExhaustionPanel" in page
    assert "The strongest honest result is exhaustion." in page
    assert "RPE1 not_assayed" in page
    assert "0 cleared" not in page
    assert "CCDC22DefendedPanel" not in page


if __name__ == "__main__":
    test_frontier_json_embeds_defended_discovery_endgame_packets()
    test_overview_contains_endgame_exhaustion_panel()
