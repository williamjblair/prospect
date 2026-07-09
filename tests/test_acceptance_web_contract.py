from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_web_exposes_paste_and_share_acceptance_surface():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    gen_data = (ROOT / "web" / "gen_data.py").read_text()

    assert "Run your own claim through Prospect" in page
    assert "NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL" in page
    assert "fetch(`${service}/submit`" in page
    assert "human_signature_required" in page
    assert "associative_only" in page
    assert "not_assayed" in page
    assert "PD-1" in page
    assert "claim_mode" in page
    assert "proposal_url" in page
    assert "prospect-state" not in page
    assert "stableHash" not in page
    assert "buildAcceptanceResult" not in page
    assert "gene_id_map" not in gen_data
    assert "acceptance_lookup" not in gen_data
    assert 'fetch("/data/check.json")' in page
    assert 'fetch("/data/frontier.json")' in page
    assert '"atlas": []' in gen_data
