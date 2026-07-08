from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_web_exposes_paste_and_share_acceptance_surface():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    gen_data = (ROOT / "web" / "gen_data.py").read_text()

    assert "Run your own claim through Prospect" in page
    assert "prospect-state" in page
    assert "human_signature_required" in page
    assert "associative_only" in page
    assert "not_assayed" in page
    assert "PD-1" in page
    assert "gene_id_map" in page
    assert "gene_id_map" in gen_data
    assert "ensembl_to_symbol" in gen_data
