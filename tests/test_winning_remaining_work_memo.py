"""Winning memo must track the expanded July 13 build goal."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMO = ROOT / "docs" / "WINNING_REMAINING_WORK.md"


def test_winning_memo_names_expanded_active_goal_and_floor():
    text = MEMO.read_text()

    for phrase in [
        "Active goal",
        "July 13, 2026",
        "Submission-ready is the floor, not the finish line",
        "Preserve the floor",
        "./prospect final-check",
        "./prospect submit-smoke",
        "root_a8b0dcdd4024e12f",
    ]:
        assert phrase in text


def test_winning_memo_lists_high_ceiling_workstreams():
    text = MEMO.read_text()

    for phrase in [
        "P0, protect the existing submission floor",
        "P1, second-substrate replay surface",
        "P1, complete the Claude campaign pressure loop",
        "P1, Gladstone-ready assay operations bundle",
        "P2, submission and demo production",
        "P3, deliberate non-goals",
    ]:
        assert phrase in text


def test_winning_memo_keeps_trust_boundary_and_scope_constraints():
    text = MEMO.read_text()

    for phrase in [
        "No model in the trust path",
        "`computationally_reproduced`",
        "`evidence_attached`",
        "`contradicted`",
        "proposal-only",
        "no accepted-state mutation",
        "Do not chase a full wet-lab result",
        "Do not add clinical or therapeutic claims",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_winning_memo_names_expanded_active_goal_and_floor()
    test_winning_memo_lists_high_ceiling_workstreams()
    test_winning_memo_keeps_trust_boundary_and_scope_constraints()
    print("PASS: winning remaining work memo")
