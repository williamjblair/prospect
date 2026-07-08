"""Static contract for the executable receipt bridge in Frontier."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_surfaces_executable_receipt_bridge_path():
    source = PAGE.read_text()

    assert "protocol_path" in source
    assert "Executable bridge path" in source
    assert "/data/receipt_bridge/receipt_manifest.json" in source
    assert "proposal only" in source
    assert "prospect.receipt.submit" in source
    assert "receipt_bridge_demo" in source
    assert "receipt_bridge_client.py" in source
    assert "Try the boundary" in source
    assert "json_command" in source
    assert "accepted=false" in source
    assert "human_signature_required" in source


if __name__ == "__main__":
    test_frontier_surfaces_executable_receipt_bridge_path()
    print("PASS: receipt bridge UI contract")
