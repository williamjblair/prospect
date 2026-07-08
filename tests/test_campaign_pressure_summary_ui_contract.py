"""Static contract for the campaign pressure summary in the web app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
GEN_DATA = ROOT / "web" / "gen_data.py"


def test_campaign_pressure_summary_is_bundled_and_visible_in_agent_tab():
    page = PAGE.read_text()
    gen_data = GEN_DATA.read_text()

    assert "campaign_pressure_summary" in gen_data
    assert "CampaignPressureSummary" in page
    assert "d.campaign_pressure_summary" in page
    assert "/data/campaign_pressure_summary.json" in page
    assert "Campaign pressure summary" in page
    assert "Claude pressure became review work" in page


if __name__ == "__main__":
    test_campaign_pressure_summary_is_bundled_and_visible_in_agent_tab()
    print("PASS: campaign pressure summary UI contract")
