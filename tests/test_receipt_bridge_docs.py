"""Receipt bridge docs must expose the external client demo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RECEIPT_BRIDGE.md"
RUN_DOC = ROOT / "docs" / "RUN_YOUR_OWN_CLAIM.md"


def test_receipt_bridge_docs_include_external_client_demo():
    text = DOC.read_text()

    assert "python examples/receipt_bridge_client.py" in text
    assert "--json" in text
    assert "accepted=false" in text
    assert "human_signature_required" in text
    assert "RUN_YOUR_OWN_CLAIM.md" in text
    assert "./prospect serve-acceptance --port 8130" in text


def test_run_your_own_claim_guide_has_web_service_and_mcp_paths():
    text = RUN_DOC.read_text()

    assert "Run your own claim through Prospect" in text
    assert "Path 1: no-setup web submit" in text
    assert "./prospect serve-acceptance --port 8130" in text
    assert "prospect.receipt.submit_artifact" in text
    assert "accepted=false" in text
    assert "human_signature_required" in text


if __name__ == "__main__":
    test_receipt_bridge_docs_include_external_client_demo()
    test_run_your_own_claim_guide_has_web_service_and_mcp_paths()
    print("PASS: receipt bridge docs")
