"""Discovery campaign UI contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_discovery_surface_is_first_class_in_agent_tab():
    text = PAGE.read_text()

    assert "DiscoveryCampaignSurface" in text
    assert "Flagship discovery campaign" in text
    assert "prenylation_small_gtpase_trafficking" in text
    assert "/data/discovery_campaign.json" in text
    assert "/data/cross_validation.json" in text
    assert "/data/flagship_module.json" in text
    assert "/data/overclaim_counter.json" in text
    assert "./prospect discovery-campaign" in text
    assert "./prospect cross-validation" in text
    assert "./prospect flagship-module" in text
    assert "./prospect overclaim-counter" in text


def test_discovery_surface_copy_uses_typed_status_language():
    text = PAGE.read_text()
    surface = text[text.find("function DiscoveryCampaignSurface"):]

    assert "evidence_attached" in surface
    assert "computationally_reproduced" in surface
    assert ("veri" + "fied") not in surface.lower()
    assert "\u2014" not in surface


if __name__ == "__main__":
    test_discovery_surface_is_first_class_in_agent_tab()
    test_discovery_surface_copy_uses_typed_status_language()
    print("PASS: discovery surface UI contract")
