"""Static contract for the self-guided judge demo path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_overview_exposes_judge_demo_path_tabs():
    source = PAGE.read_text()

    assert "DEMO_PATH" in source
    assert "Demo path" in source
    # The guided strip navigates to the three deep tabs.
    assert "setTab(step.tab" in source
    for tab in ['"findings"', '"frontier"', '"agent"']:
        assert tab in source


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
    test_overview_renders_visible_claim_check_strip()
    print("PASS: demo path UI contract")
