"""Static contract for the campaign challenger ledger in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_campaign_challenger_ledger_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "campaign_challenger_ledger" in gen_data
    assert "CampaignChallengerLedgerCard" in page
    assert "d.campaign_challenger_ledger" in page
    assert "/data/campaign_challenger_ledger.json" in page
    assert "Campaign challenger ledger" in page
    assert "challenges RWDD2B" in page
    assert "adds CYB5RL" in page


if __name__ == "__main__":
    test_campaign_challenger_ledger_is_bundled_and_visible_in_agent_tab()
    print("PASS: campaign challenger ledger UI contract")
