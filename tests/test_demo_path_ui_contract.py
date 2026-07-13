"""Static contract for the self-guided judge demo path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_overview_exposes_judge_demo_path_tabs():
    source = PAGE.read_text()

    for label in ['label: "Check"', 'label: "Evidence"', 'label: "Lead"', 'label: "Receipts"']:
        assert label in source
    for old_label in ['label: "Overview"', 'label: "Atlas"', 'label: "Network"', 'label: "Frontier"', 'label: "Findings"', 'label: "Agent"', 'label: "Genes"', 'label: "Graph"']:
        assert old_label not in source
    for tab in ['"findings"', '"frontier"', '"agent"', '"atlas"', '"network"']:
        assert tab in source


def test_overview_headline_numbers_are_traceable():
    source = PAGE.read_text()

    assert "Reproducible is not verified" in source
    assert "real Claude Science export" in source
    assert "p.refuted" in source
    assert "p.effector_overclaim_rate" in source
    assert "PGGT1B" in source
    # The human acceptance boundary stays traceable on the Overview even after the standalone card
    # was folded into the hero and the "How Claude is used" strip.
    assert "human_signature_required" in source
    assert "No model sits in the trust path" in source


def test_overview_keeps_the_canonical_check_surface_first():
    source = PAGE.read_text()

    overview_start = source.index("function Overview")
    workbench = source.index("<ProspectAcceptanceWorkbench", overview_start)
    evidence = source.index("real Claude Science export", overview_start)
    assert workbench < evidence


if __name__ == "__main__":
    test_overview_exposes_judge_demo_path_tabs()
    test_overview_headline_numbers_are_traceable()
    test_overview_keeps_the_canonical_check_surface_first()
    print("PASS: demo path UI contract")
