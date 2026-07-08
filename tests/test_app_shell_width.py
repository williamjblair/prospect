"""Static guardrail for the app shell width.

The sidebar inset plus an oversized app frame can create page-level horizontal
overflow even when individual tables are internally scrollable. Keep the
global app frame cap aligned with the shell in page.tsx.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
CSS = ROOT / "web" / "app" / "globals.css"
SIDEBAR = ROOT / "web" / "components" / "ui" / "sidebar.tsx"


def test_app_main_global_width_matches_shell_cap():
    page = PAGE.read_text()
    css = CSS.read_text()
    sidebar = SIDEBAR.read_text()

    assert 'maxWidth: "78rem"' in page
    assert 'className="frontier-pane"' in page
    assert ".app-main {\n  max-width: 78rem;" in css
    assert "max-width: 118rem" not in css
    assert ".frontier-pane > *" in css
    assert ".frontier-pane .card-paper" in css
    assert '"relative flex min-w-0 flex-1 flex-col bg-background"' in sidebar
    assert '"relative flex w-full flex-1 flex-col bg-background"' not in sidebar


if __name__ == "__main__":
    test_app_main_global_width_matches_shell_cap()
    print("PASS: app shell width")
