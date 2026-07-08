"""Static contract for the live judge quickstart affordance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_overview_surfaces_judge_quickstart_from_live_app():
    source = PAGE.read_text()

    for phrase in [
        "Judge quickstart",
        "Five-minute path",
        "A1BG refusal",
        "PGGT1B packet",
        "docs/JUDGE_QUICKSTART.md",
        "github.com/williamjblair/prospect/blob/master/docs/JUDGE_QUICKSTART.md",
        "Judge packet JSON",
    ]:
        assert phrase in source


if __name__ == "__main__":
    test_overview_surfaces_judge_quickstart_from_live_app()
    print("PASS: judge quickstart UI contract")
