"""Cross-domain overclaiming benchmark contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "web" / "public" / "data" / "frontier.json"
PAGE = ROOT / "web" / "app" / "page.tsx"


def test_frontier_json_embeds_cross_domain_benchmark_context():
    data = json.loads(FRONTIER.read_text())
    cross = data["cross_domain_benchmark"]

    assert cross["title"] == "Two domains, one trust boundary"
    assert cross["status"] == "evidence_attached"
    assert cross["accepted_state_mutation"] == "none"
    assert cross["range"] == "48-79%"
    assert cross["biology"]["domain"] == "biology"
    assert cross["biology"]["overclaim_rate"] == 0.48
    assert cross["biology"]["effector_overclaim_rate"] == 0.64
    assert cross["math"]["domain"] == "math"
    assert cross["math"]["claims_false"] == 19
    assert cross["math"]["claims_total"] == 24
    assert cross["math"]["false_claim_rate"] == 0.79
    assert cross["math"]["source_name"] == "Adversarial falsification audit: 19 of 24 verification claims fail"
    assert cross["math"]["platform_url"] == "https://openresearch.sh/"
    assert cross["boundary"] == "frozen_rederivation_plus_human_key"


def test_overview_surfaces_cross_domain_benchmark_context():
    source = PAGE.read_text()

    assert "CrossDomainBenchmark" in source
    assert "Two domains, one trust boundary" in source
    assert "48-79%" in source
    assert "Adversarial falsification audit: 19 of 24 verification claims fail" in source
    assert "frozen re-derivation plus a human key" in source


if __name__ == "__main__":
    test_frontier_json_embeds_cross_domain_benchmark_context()
    test_overview_surfaces_cross_domain_benchmark_context()
    print("PASS: cross-domain benchmark")
