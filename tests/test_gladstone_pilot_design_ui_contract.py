"""Static contract for the Gladstone pilot design in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_gladstone_pilot_design_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "gladstone_pilot_design" in gen_data
    assert "GLADSTONE_PILOT_OUT" in gen_data
    assert "type GladstonePilotDesign" in page
    assert "GladstonePilotDesignCard" in page
    assert "d.gladstone_pilot_design" in page
    assert "/data/gladstone_pilot_design.json" in page
    assert "Gladstone pilot design" in page
    assert "90 culture arms" in page


if __name__ == "__main__":
    test_gladstone_pilot_design_is_bundled_and_visible_in_agent_tab()
    print("PASS: Gladstone pilot design UI contract")
