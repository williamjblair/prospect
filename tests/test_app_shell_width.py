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


def test_sidebar_menu_button_uses_paint_only_tab_feedback():
    css = CSS.read_text()
    sidebar = SIDEBAR.read_text()
    menu_button = sidebar.split("function SidebarMenuButton", 1)[1].split("function SidebarMenuAction", 1)[0]

    assert "transition: background-color 180ms var(--ease), color 180ms var(--ease);" in css
    assert "width 300ms cubic-bezier" not in menu_button
    assert "height 300ms cubic-bezier" not in menu_button
    assert "padding 300ms cubic-bezier" not in menu_button


def test_app_shell_has_browser_icon_asset():
    icon = ROOT / "web" / "app" / "icon.svg"

    assert icon.exists()
    text = icon.read_text()
    assert "<svg" in text
    assert "Prospect" in text


if __name__ == "__main__":
    test_app_main_global_width_matches_shell_cap()
    test_sidebar_menu_button_uses_paint_only_tab_feedback()
    test_app_shell_has_browser_icon_asset()
    print("PASS: app shell width")
