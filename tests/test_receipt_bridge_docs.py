"""Receipt bridge docs must expose the external client demo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RECEIPT_BRIDGE.md"


def test_receipt_bridge_docs_include_external_client_demo():
    text = DOC.read_text()

    assert "python examples/receipt_bridge_client.py" in text
    assert "--json" in text
    assert "accepted=false" in text
    assert "human_signature_required" in text


if __name__ == "__main__":
    test_receipt_bridge_docs_include_external_client_demo()
    print("PASS: receipt bridge docs")
