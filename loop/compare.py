"""Aggregate per-model runs into a cost-vs-phantom comparison. Reads each model's
run_stats + claims corpus, computes the honest refuted-rate (refuted / checkable, matching
score.py), and the cost. Writes examples/data/model_comparison.json for the atlas UI.

  python loop/compare.py
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
ORDER = ["haiku", "sonnet", "opus", "fable"]
LABEL = {"haiku": "Haiku 4.5", "sonnet": "Sonnet 5", "opus": "Opus 4.8", "fable": "Fable 5"}

def compare():
    rows = []
    for tag in ORDER:
        st = os.path.join(DATA, f"run_stats_{tag}.json")
        cl = os.path.join(DATA, f"claims_{tag}.jsonl")
        if not (os.path.exists(st) and os.path.exists(cl)):
            continue
        stats = json.load(open(st))
        ai = [json.loads(l) for l in open(cl) if json.loads(l)["ai_major"]]
        supported = sum(r["verdict"] == "supported" for r in ai)
        refuted = sum(r["verdict"] == "refuted" for r in ai)
        checkable = supported + refuted
        rows.append({
            "tag": tag, "label": LABEL.get(tag, tag), "model": stats["model"],
            "cost_usd": stats["cost_usd"], "tokens": stats["input_tokens"] + stats["output_tokens"],
            "ai_major": len(ai), "supported": supported, "refuted": refuted,
            "checkable": checkable,
            "refuted_rate": round(refuted / checkable, 3) if checkable else None,
        })
    json.dump(rows, open(os.path.join(DATA, "model_comparison.json"), "w"), indent=2)
    print(f"{'model':12s} {'cost':>8s} {'AI-major':>9s} {'checkable':>10s} {'refuted':>8s} {'rate':>6s}")
    for r in rows:
        rate = f"{r['refuted_rate']:.0%}" if r["refuted_rate"] is not None else "n/a"
        print(f"{r['label']:12s} {'$'+format(r['cost_usd'],'.3f'):>8s} {r['ai_major']:>9d} "
              f"{r['checkable']:>10d} {r['refuted']:>8d} {rate:>6s}")
    return rows

if __name__ == "__main__":
    compare()
