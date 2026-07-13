"""The AI Biology Reliability Benchmark.

How often do confident LLM biology claims survive contact with frozen CRISPRi Perturb-seq ground
truth? This module adds the statistics the headline overclaim number was missing: Wilson 95%
confidence intervals on every rate, a seeded permutation test for the famous-gene overclaiming
effect, and a confidence-calibration curve (does a model's stated confidence track whether the
frozen data contradicts it?).

It is pure re-processing of the committed frozen model runs (examples/data/bench_*.jsonl). It makes
no API calls and never re-grades: the frozen checker (engine/checkers/marson_perturbseq.py) already
produced every verdict, and the model generations (claim text plus stated confidence) are frozen in
the committed records. The whole result therefore replays offline from committed data.

  python -m frontier.reliability_benchmark        # writes examples/data/reliability_benchmark.json
  ./prospect reliability-benchmark
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT = DATA / "reliability_benchmark.json"

SEED = 7
PERMUTATIONS = 10000
Z95 = 1.959963984540054  # standard normal quantile for a two-sided 95% interval

HISTORICAL_TAGS = ["haiku", "sonnet", "opus", "fable"]
CURRENT_TAG = "opus_current"
LABEL = {
    "haiku": "Haiku 4.5",
    "sonnet": "Sonnet 5",
    "opus": "Opus 4.8",
    "fable": "Fable 5",
    "opus_current": "Opus 4.8 (fresh run)",
}
CEILING = "computation over released data, not wet-lab or clinical truth"


def _rows(tag: str) -> list[dict[str, Any]]:
    path = DATA / f"bench_{tag}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _sha(tag: str) -> str | None:
    path = DATA / f"bench_{tag}.jsonl"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else None


def wilson_ci(k: int, n: int, z: float = Z95) -> list[float]:
    """95% Wilson score interval for a binomial proportion k/n. Pure arithmetic, no dependency."""
    if n <= 0:
        return [0.0, 0.0]
    phat = k / n
    denom = 1.0 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(phat * (1.0 - phat) / n + z * z / (4.0 * n * n))
    return [round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)]


def _contradiction(claims: list[dict[str, Any]]) -> dict[str, Any]:
    """Contradiction rate over confident major-regulator claims the assay could check.

    Checkable = the claim asserted major AND on-target knockdown was confirmed, so the verdict is
    either supported or refuted. Contradiction rate = refuted / checkable.
    """
    checkable = [c for c in claims if c["ai_major"] and c["verdict"] in ("supported", "refuted")]
    refuted = sum(1 for c in checkable if c["verdict"] == "refuted")
    supported = sum(1 for c in checkable if c["verdict"] == "supported")
    n = len(checkable)
    return {
        "checkable": n,
        "supported": supported,
        "refuted": refuted,
        "contradiction_rate": round(refuted / n, 4) if n else 0.0,
        "ci95": wilson_ci(refuted, n),
    }


def _core(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _contradiction([r for r in rows if "core" in r.get("buckets", [])])


def _overclaim_frequency(rows: list[dict[str, Any]], bucket: str) -> dict[str, Any]:
    """Fraction of judgments in `bucket` that confidently called the gene a major regulator."""
    graded = [r for r in rows if bucket in r.get("buckets", [])]
    claimed = sum(1 for r in graded if r["ai_major"])
    n = len(graded)
    return {
        "total": n,
        "overclaimed": claimed,
        "overclaim_rate": round(claimed / n, 4) if n else 0.0,
        "ci95": wilson_ci(claimed, n),
    }


def _major_labels(rows: list[dict[str, Any]], predicate) -> list[int]:
    return [1 if r["ai_major"] else 0 for r in rows if predicate(r)]


def _permutation_diff_p(group_a: list[int], group_b: list[int]) -> dict[str, Any]:
    """One-sided permutation test that rate(A) > rate(B) for two 0/1 label lists. Seeded, add-one."""
    na, nb = len(group_a), len(group_b)
    if na == 0 or nb == 0:
        return {"n_a": na, "n_b": nb, "difference": 0.0, "permutation_p_one_sided": 1.0}
    rate_a = sum(group_a) / na
    rate_b = sum(group_b) / nb
    observed = rate_a - rate_b
    pool = list(group_a) + list(group_b)
    rng = random.Random(SEED)
    at_least = 0
    for _ in range(PERMUTATIONS):
        rng.shuffle(pool)
        diff = sum(pool[:na]) / na - sum(pool[na:]) / nb
        if diff >= observed:
            at_least += 1
    return {
        "n_a": na,
        "n_b": nb,
        "rate_a": round(rate_a, 4),
        "rate_b": round(rate_b, 4),
        "difference": round(observed, 4),
        "permutation_p_one_sided": round((at_least + 1) / (PERMUTATIONS + 1), 6),
        "permutations": PERMUTATIONS,
        "seed": SEED,
    }


CALIBRATION_BINS = [(0.0, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 1.01)]


def _calibration(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Contradiction rate among checkable confident major claims, binned by stated confidence."""
    claims = [
        r
        for r in rows
        if r["ai_major"]
        and r["verdict"] in ("supported", "refuted")
        and isinstance(r.get("ai_confidence"), (int, float))
    ]
    table = []
    for lo, hi in CALIBRATION_BINS:
        binned = [r for r in claims if lo <= float(r["ai_confidence"]) < hi]
        refuted = sum(1 for r in binned if r["verdict"] == "refuted")
        n = len(binned)
        table.append(
            {
                "stated_confidence": f"{lo:.2f} to {min(hi, 1.0):.2f}",
                "n": n,
                "contradicted": refuted,
                "contradiction_rate": round(refuted / n, 4) if n else None,
                "ci95": wilson_ci(refuted, n) if n else None,
            }
        )
    return table


def _per_model(tags: list[str]) -> list[dict[str, Any]]:
    out = []
    for tag in tags:
        rows = _rows(tag)
        if not rows:
            continue
        core = _core(rows)
        eff = _overclaim_frequency(rows, "effector")
        out.append(
            {
                "tag": tag,
                "label": LABEL.get(tag, tag),
                "core_contradiction": core,
                "effector_overclaim": eff,
            }
        )
    return out


def _one_model_summary(tag: str) -> dict[str, Any] | None:
    rows = _rows(tag)
    if not rows:
        return None
    return {
        "tag": tag,
        "label": LABEL.get(tag, tag),
        "input_sha": _sha(tag),
        "core_contradiction": _core(rows),
        "effector_overclaim": _overclaim_frequency(rows, "effector"),
        "confidence_calibration": _calibration(rows),
    }


def build_reliability_benchmark() -> dict[str, Any]:
    historical = [t for t in HISTORICAL_TAGS if _rows(t)]
    pooled = [r for t in historical for r in _rows(t)]

    core = _core(pooled)
    effector = _overclaim_frequency(pooled, "effector")

    # The famous-gene effect: do models call famous non-major genes "major" more often than they
    # call data-confirmed non-major genes "major"? Baseline = core genes the frozen data classes as
    # non-regulators (a matched non-major control), so the comparison isolates fame, not biology.
    famous = _major_labels(pooled, lambda r: "effector" in r.get("buckets", []))
    baseline = _major_labels(
        pooled,
        lambda r: "core" in r.get("buckets", []) and r.get("truth_class") == "verified_non_regulator",
    )
    effect = _permutation_diff_p(famous, baseline)

    packet: dict[str, Any] = {
        "packet": "ai_biology_reliability_benchmark",
        "question": (
            "How often do confident LLM biology claims survive contact with frozen CRISPRi "
            "Perturb-seq ground truth, and does a model's stated confidence track whether the data "
            "contradicts it?"
        ),
        "method": {
            "ground_truth": "Marson primary human CD4+ CRISPRi Perturb-seq differential-expression table (frozen, committed)",
            "checker": "engine/checkers/marson_perturbseq.py, deterministic and model-free",
            "corpus": {
                "core_genes": 220,
                "effector_genes": 18,
                "stratification": "55 genes per truth class, plus 18 famous checkpoint/cytokine genes",
                "seed": 7,
                "source": "examples/data/benchmark_corpus.json",
            },
            "models_pooled": [LABEL[t] for t in historical],
            "interval_method": "Wilson score interval, 95 percent",
            "permutation_iterations": PERMUTATIONS,
            "seed": SEED,
            "reproducibility": "replays offline from the committed bench_*.jsonl with no API calls and no re-grading",
        },
        "metrics": {
            "contradiction_rate": {
                "definition": (
                    "Of confident major-regulator claims the frozen assay could check (on-target "
                    "knockdown confirmed), the fraction the measured data contradicts."
                ),
                "pooled_core": core,
            },
            "overclaim_frequency_famous_genes": {
                "definition": (
                    "Of judgments on the 18 famous checkpoint and cytokine genes the data shows are "
                    "not major regulators, the fraction a model confidently called a major regulator."
                ),
                "pooled": effector,
            },
        },
        "famous_gene_effect": {
            "description": (
                "Models call famous checkpoint and cytokine genes major regulators more often than "
                "genes the frozen data classes as non-regulators."
            ),
            "famous_overclaim_rate": effect.get("rate_a"),
            "baseline_overclaim_rate": effect.get("rate_b"),
            "difference": effect.get("difference"),
            "permutation_p_one_sided": effect.get("permutation_p_one_sided"),
            "significant_at_0_05": bool(effect.get("permutation_p_one_sided", 1.0) < 0.05),
            "n_famous": effect.get("n_a"),
            "n_baseline": effect.get("n_b"),
        },
        "confidence_calibration": {
            "description": (
                "Contradiction rate among confident major claims, binned by the model's own stated "
                "confidence. A well-calibrated model would show a lower contradiction rate at higher "
                "stated confidence."
            ),
            "bins": _calibration(pooled),
        },
        "per_model": _per_model(historical),
        "input_sha": {t: _sha(t) for t in historical},
        "honest_ceiling": CEILING,
        "accepted": False,
        "next": "human_signature_required",
        "reproduce_command": "./prospect reliability-benchmark",
    }

    current = _one_model_summary(CURRENT_TAG)
    if current is not None:
        packet["current_model"] = current

    return packet


def main(argv: list[str] | None = None) -> int:
    packet = build_reliability_benchmark()
    OUT.write_text(json.dumps(packet, indent=2) + "\n")

    core = packet["metrics"]["contradiction_rate"]["pooled_core"]
    eff = packet["metrics"]["overclaim_frequency_famous_genes"]["pooled"]
    effect = packet["famous_gene_effect"]
    print("AI Biology Reliability Benchmark")
    print(
        f"  contradiction rate (core): {core['refuted']}/{core['checkable']} = "
        f"{core['contradiction_rate']*100:.1f}%  95% CI [{core['ci95'][0]*100:.1f}, {core['ci95'][1]*100:.1f}]"
    )
    print(
        f"  overclaim on famous genes: {eff['overclaimed']}/{eff['total']} = "
        f"{eff['overclaim_rate']*100:.1f}%  95% CI [{eff['ci95'][0]*100:.1f}, {eff['ci95'][1]*100:.1f}]"
    )
    print(
        f"  famous-gene effect: {effect['famous_overclaim_rate']*100:.1f}% vs "
        f"{effect['baseline_overclaim_rate']*100:.1f}% baseline, permutation p = "
        f"{effect['permutation_p_one_sided']}"
    )
    print("  confidence calibration (contradiction rate by stated confidence):")
    for b in packet["confidence_calibration"]["bins"]:
        if b["n"]:
            print(
                f"    conf {b['stated_confidence']}: {b['contradicted']}/{b['n']} = "
                f"{b['contradiction_rate']*100:.1f}%"
            )
    if "current_model" in packet:
        cm = packet["current_model"]["core_contradiction"]
        print(
            f"  current model {packet['current_model']['label']}: "
            f"{cm['refuted']}/{cm['checkable']} = {cm['contradiction_rate']*100:.1f}%  "
            f"95% CI [{cm['ci95'][0]*100:.1f}, {cm['ci95'][1]*100:.1f}]"
        )
    print(f"  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
