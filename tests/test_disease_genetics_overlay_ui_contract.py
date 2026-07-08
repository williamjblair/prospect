"""Static contract for the disease-genetics overlay packet in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_disease_genetics_overlay_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "disease_genetics_overlay" in gen_data
    assert "DiseaseGeneticsOverlayCard" in page
    assert "d.disease_genetics_overlay" in page
    assert "/data/disease_genetics_overlay.json" in page
    assert "Disease-genetics overlay packet" in page
    assert "immune or hematologic context" in page
    assert "No accepted state changes" in page


if __name__ == "__main__":
    test_disease_genetics_overlay_is_bundled_and_visible_in_agent_tab()
    print("PASS: disease-genetics overlay UI contract")
