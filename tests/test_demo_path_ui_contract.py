"""Static contract for the self-guided judge demo path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_overview_exposes_judge_demo_path_tabs():
    source = PAGE.read_text()

    assert "DEMO_PATH" in source
    assert "Guided judge tour" in source
    assert "Five moves, no setup." in source
    for label in ['label: "Check"', 'label: "Genes"', 'label: "Graph"', 'label: "Receipts"', 'label: "Evidence"', 'label: "Lead"']:
        assert label in source
    for old_label in ['label: "Overview"', 'label: "Atlas"', 'label: "Network"', 'label: "Frontier"', 'label: "Findings"', 'label: "Agent"']:
        assert old_label not in source
    # The guided strip navigates to the three deep tabs.
    assert "setTab(step.tab" in source
    for tab in ['"findings"', '"frontier"', '"agent"']:
        assert tab in source


def test_overview_headline_numbers_are_traceable():
    source = PAGE.read_text()

    assert "TraceableHeadlineRail" in source
    assert "Four claims, four artifacts, no packet pile." in source
    assert "data-trace-number" in source
    for artifact in [
        "/data/overclaim_counter.json",
        "/data/claude_science_acceptance_demo.json",
        "/data/pggt1b_defended_evidence.json",
        "/data/frontier.json",
    ]:
        assert artifact in source
    for command in [
        "./prospect overclaim-counter",
        "python examples/claude_science_connector_client.py --json",
        "./prospect pggt1b-defended-evidence",
        "./prospect verify",
    ]:
        assert command in source


def test_overview_renders_visible_claim_check_strip():
    source = PAGE.read_text()

    assert "Opening claim checks" in source
    assert "const demoClaims" in source
    assert "demoClaims.slice(0, 3).map" in source
    assert "key={`${x.gene}-${x.status}`}" in source
    assert "{x.text}" in source
    assert "{x.reason}" in source


if __name__ == "__main__":
    test_overview_exposes_judge_demo_path_tabs()
    test_overview_headline_numbers_are_traceable()
    test_overview_renders_visible_claim_check_strip()
    print("PASS: demo path UI contract")
