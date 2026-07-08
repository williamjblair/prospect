"""Static contract for the cross-substrate discovery packet in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_cross_substrate_discovery_is_bundled_and_visible_in_findings_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "cross_substrate_discovery" in gen_data
    assert "CrossSubstrateDiscoveryPacket" in page
    assert "d.cross_substrate_discovery" in page
    assert "/data/cross_substrate_discovery.json" in page
    assert "Cross-substrate discovery packet" in page
    assert "T-cell-specific activation" in page
    assert "non-immune-only effects" in page


if __name__ == "__main__":
    test_cross_substrate_discovery_is_bundled_and_visible_in_findings_tab()
    print("PASS: cross-substrate discovery UI contract")
