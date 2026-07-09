"""Static guardrail for the Lab Console shell width."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
CSS = ROOT / "web" / "app" / "globals.css"


def test_app_main_global_width_matches_console_cap():
    page = PAGE.read_text()
    css = CSS.read_text()

    assert "prospect-console" in page
    assert "console-topbar" in page
    assert "console-nav" in page
    assert "SidebarProvider" not in page
    assert 'className="frontier-pane"' in page
    assert ".console-main" in css
    assert "max-width: 94rem;" in css
    assert "max-width: 118rem" not in css
    assert ".frontier-pane > *" in css
    assert ".frontier-pane .card-paper" in css


def test_console_nav_uses_paint_only_tab_feedback():
    css = CSS.read_text()

    assert "transition: background-color 180ms var(--ease), color 180ms var(--ease);" in css
    console_block = css.split(".console-nav-item", 1)[1].split(".console-actions", 1)[0]
    assert "transform" not in console_block
    assert "box-shadow" not in console_block


def test_app_shell_has_browser_icon_asset():
    icon = ROOT / "web" / "app" / "icon.svg"

    assert icon.exists()
    text = icon.read_text()
    assert "<svg" in text
    assert "Prospect" in text


if __name__ == "__main__":
    test_app_main_global_width_matches_console_cap()
    test_console_nav_uses_paint_only_tab_feedback()
    test_app_shell_has_browser_icon_asset()
    print("PASS: app shell width")
