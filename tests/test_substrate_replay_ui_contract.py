"""Static contract for the substrate replay packet in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_substrate_replay_is_bundled_and_visible_in_findings_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "substrate_replay_packet" in gen_data
    assert "SubstrateReplayPacket" in page
    assert "d.substrate_replay_packet" in page
    assert "/data/substrate_replay_packet.json" in page
    assert "Substrate replay packet" in page
    assert "one checker contract, three frozen substrates" in page


if __name__ == "__main__":
    test_substrate_replay_is_bundled_and_visible_in_findings_tab()
    print("PASS: substrate replay UI contract")
