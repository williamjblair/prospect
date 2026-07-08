"""Static contract for the donor-condition replay packet in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_donor_condition_replay_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "donor_condition_replay" in gen_data
    assert "DonorConditionReplayCard" in page
    assert "d.donor_condition_replay" in page
    assert "/data/donor_condition_replay.json" in page
    assert "Donor-condition replay packet" in page
    assert "donor-supported" in page
    assert "donor-fragile" in page


if __name__ == "__main__":
    test_donor_condition_replay_is_bundled_and_visible_in_agent_tab()
    print("PASS: donor-condition replay UI contract")
