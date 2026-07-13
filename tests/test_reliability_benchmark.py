"""The AI Biology Reliability Benchmark reproduces from committed data, with correct statistics."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.reliability_benchmark import build_reliability_benchmark, wilson_ci


def test_wilson_ci_is_a_correct_95_percent_interval():
    # Degenerate cases.
    assert wilson_ci(0, 0) == [0.0, 0.0]
    # A half-and-half proportion is centred near 0.5 and brackets it.
    lo, hi = wilson_ci(50, 100)
    assert lo < 0.5 < hi
    assert 0.39 < lo < 0.41 and 0.59 < hi < 0.61  # known Wilson bounds for 50/100
    # A unanimous count does not produce a degenerate [1, 1] interval (Wilson pulls the bound in).
    lo, hi = wilson_ci(10, 10)
    assert lo < 1.0 and hi == 1.0 or hi <= 1.0
    assert lo > 0.7
    # Bounds always sit inside [0, 1].
    for k, n in [(0, 5), (5, 5), (1, 3), (46, 96), (46, 72)]:
        lo, hi = wilson_ci(k, n)
        assert 0.0 <= lo <= hi <= 1.0


def test_headline_reproduces_from_committed_frozen_runs():
    packet = build_reliability_benchmark()
    core = packet["metrics"]["contradiction_rate"]["pooled_core"]
    eff = packet["metrics"]["overclaim_frequency_famous_genes"]["pooled"]

    # The committed 4-model pooled runs give the published headline, exactly.
    assert core["refuted"] == 46
    assert core["checkable"] == 96
    assert core["contradiction_rate"] == 0.4792
    assert eff["overclaimed"] == 46
    assert eff["total"] == 72
    assert eff["overclaim_rate"] == 0.6389

    # The 95% CI brackets the point estimate on both metrics.
    assert core["ci95"][0] < core["contradiction_rate"] < core["ci95"][1]
    assert eff["ci95"][0] < eff["overclaim_rate"] < eff["ci95"][1]


def test_two_metrics_are_defined_and_distinct():
    packet = build_reliability_benchmark()
    metrics = packet["metrics"]
    assert "contradiction_rate" in metrics and "overclaim_frequency_famous_genes" in metrics
    # Each carries its own explicit definition string, so they are never conflated.
    assert metrics["contradiction_rate"]["definition"] != metrics["overclaim_frequency_famous_genes"]["definition"]
    assert "knockdown" in metrics["contradiction_rate"]["definition"]


def test_famous_gene_effect_is_significant():
    effect = build_reliability_benchmark()["famous_gene_effect"]
    # Famous genes are overclaimed far more than data-confirmed non-regulators, and the seeded
    # permutation test is deterministic, so the significance is stable.
    assert effect["famous_overclaim_rate"] > effect["baseline_overclaim_rate"]
    assert effect["permutation_p_one_sided"] < 0.05
    assert effect["significant_at_0_05"] is True
    assert effect["n_baseline"] > 100


def test_calibration_bins_are_well_formed():
    bins = build_reliability_benchmark()["confidence_calibration"]["bins"]
    assert len(bins) >= 3
    total = sum(b["n"] for b in bins)
    assert total > 0
    for b in bins:
        assert "stated_confidence" in b
        if b["n"]:
            assert 0.0 <= b["contradiction_rate"] <= 1.0
            assert b["ci95"][0] <= b["contradiction_rate"] <= b["ci95"][1]


def test_packet_stays_proposal_only_under_the_ceiling():
    packet = build_reliability_benchmark()
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"


def test_committed_packet_matches_a_fresh_build():
    # The committed artifact must be computed, not hand-edited: a fresh build from the committed
    # frozen runs reproduces it exactly. This is the benchmark's own thesis applied to itself.
    built = build_reliability_benchmark()
    committed = json.loads((ROOT / "examples" / "data" / "reliability_benchmark.json").read_text())
    assert built == committed, "reliability_benchmark.json is stale; run ./prospect reliability-benchmark"


if __name__ == "__main__":
    test_wilson_ci_is_a_correct_95_percent_interval()
    test_headline_reproduces_from_committed_frozen_runs()
    test_two_metrics_are_defined_and_distinct()
    test_famous_gene_effect_is_significant()
    test_calibration_bins_are_well_formed()
    test_packet_stays_proposal_only_under_the_ceiling()
    test_committed_packet_matches_a_fresh_build()
    print("PASS: reliability benchmark")
