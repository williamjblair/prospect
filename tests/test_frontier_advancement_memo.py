"""Frontier advancement memo must stay concrete, sourced, and Prospect-native."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMO = ROOT / "docs" / "FRONTIER_ADVANCEMENT_MEMO.md"


def test_frontier_advancement_memo_names_goal_sources_and_workstreams():
    text = MEMO.read_text()

    for phrase in [
        "Active goal",
        "Primary-source research",
        "donor-condition replay",
        "cross-substrate discovery",
        "disease-genetics overlay",
        "perturbation-atlas scout",
        "Primary Human CD4+ T Cell Perturb-seq",
        "Replogle et al. 2022",
        "scPerturb",
        "PerturBase",
        "Tahoe-100M",
        "Open Targets Platform",
        "GWAS Catalog",
    ]:
        assert phrase in text


def test_frontier_advancement_memo_keeps_trust_boundary_and_no_prior_branding():
    text = MEMO.read_text()

    for phrase in [
        "No model in the trust path",
        "`computationally_reproduced`",
        "`evidence_attached`",
        "`contradicted`",
        "no accepted-state mutation",
        "./prospect final-check",
        "./prospect submit-smoke",
    ]:
        assert phrase in text

    for forbidden in [
        "Vela",
        "vela",
        "Constellate",
        "constellate",
        "verified biology",
        "wet-lab truth",
        "clinical truth",
    ]:
        assert forbidden not in text


if __name__ == "__main__":
    test_frontier_advancement_memo_names_goal_sources_and_workstreams()
    test_frontier_advancement_memo_keeps_trust_boundary_and_no_prior_branding()
    print("PASS: frontier advancement memo")
