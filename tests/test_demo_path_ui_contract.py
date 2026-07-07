"""Static contract for the self-guided judge demo path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_overview_exposes_judge_demo_path_tabs():
    source = PAGE.read_text()

    assert "packet.demo_path" in source
    assert 'setTab("findings")' in source
    assert 'setTab("frontier")' in source
    assert 'setTab("agent")' in source
    assert "Demo path" in source


if __name__ == "__main__":
    test_overview_exposes_judge_demo_path_tabs()
    print("PASS: demo path UI contract")
