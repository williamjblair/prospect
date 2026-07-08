"""UI data contract for the defended discovery fixed-bar outcome."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_json_embeds_defended_discovery_endgame_packets():
    data = json.loads(FRONTIER.read_text())

    result = data["defended_discovery_endgame_result"]

    assert result["outcome"] == "defended_lead"
    assert result["accepted"] is False
    assert result["candidate_count"] == 18
    assert result["cleared_count"] == 1
    assert result["lead_candidate"]["gene"] == "PGGT1B"
    assert result["non_blocking_not_assayed"] == [
        {
            "rung": "cell_type_specificity",
            "typed_detail": "rpe1_not_assayed",
            "affected_candidates": 18,
            "basis": "RPE1 coverage is sparse in the frozen Replogle comparator, so missing RPE1 rows are not_assayed context.",
        }
    ]
    assert result["candidate_decisions"][0]["decision"] == "clears_fixed_bar_pending_human_key"
    assert result["candidate_decisions"][4]["gene"] == "CCDC22"
    assert result["candidate_decisions"][4]["decision"] == "not_selected_after_rank1_lead"


def test_overview_contains_endgame_result_panel():
    page = PAGE.read_text()

    assert "EndgameResultPanel" in page
    assert "PGGT1B clears the fixed bar as a proposal." in page
    assert "RPE1 context" in page
    assert "defended_discovery_endgame_exhaustion" not in page
    assert "CCDC22DefendedPanel" not in page


if __name__ == "__main__":
    test_frontier_json_embeds_defended_discovery_endgame_packets()
    test_overview_contains_endgame_result_panel()
