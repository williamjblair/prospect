"""Static contract for the lab packet in the web artifact and Agent tab."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_lab_packet_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "lab_packet" in gen_data
    assert "LAB_PACKET_OUT" in gen_data
    assert "type LabPacket" in page
    assert "LabPacketCard" in page
    assert "/data/lab_packet.json" in page
    assert "d.lab_packet" in page


if __name__ == "__main__":
    test_lab_packet_is_bundled_and_visible_in_agent_tab()
    print("PASS: lab packet UI contract")
