"""Static contract for the Gladstone assay operations bundle in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_assay_operations_bundle_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "assay_operations_bundle" in gen_data
    assert "AssayOperationsBundle" in page
    assert "AssayOperationsBundleCard" in page
    assert "d.assay_operations_bundle" in page
    assert "/data/assay_operations_bundle.json" in page
    assert "Gladstone assay operations bundle" in page
    assert "expected positive result" in page


if __name__ == "__main__":
    test_assay_operations_bundle_is_bundled_and_visible_in_agent_tab()
    print("PASS: assay operations bundle UI contract")
