"""Unify the overclaiming benchmark. Reads the frozen-corpus runs (bench_{tag}.jsonl +
bench_stats_{tag}.json) and writes BOTH the headline stat and the per-model table from the
SAME data, fixing the old decoupling where the headline came from an untagged corpus while the
table came from separate runs.

Two numbers, kept honest and separate:
  headline (core)  — pooled over the stratified `core` bucket across all models: of the confident
                     "major regulator" claims the screen could verify, how many the data contradicts.
  effector (focus) — over the 18 finding-#2 effector genes: how often a model calls a checkpoint/
                     cytokine a major regulator when the data shows near-zero change. Reported
                     separately, never folded into the headline (that would enrich the sample).

  python loop/bench_summary.py   # writes phantom_summary.json + model_comparison.json
"""
import glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
ORDER = ["haiku", "sonnet", "opus", "fable"]
LABEL = {"haiku": "Haiku 4.5", "sonnet": "Sonnet 5", "opus": "Opus 4.8", "fable": "Fable 5"}

def _rows(tag):
    p = os.path.join(DATA, f"bench_{tag}.jsonl")
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

def _stats(tag):
    p = os.path.join(DATA, f"bench_stats_{tag}.json")
    return json.load(open(p)) if os.path.exists(p) else {}

def _score(rows, bucket):
    """Over the confident major-regulator claims in `bucket`: supported / refuted / etc."""
    claims = [r for r in rows if r["ai_major"] and bucket in r.get("buckets", [])]
    sup = sum(1 for r in claims if r["verdict"] == "supported")
    ref = sum(1 for r in claims if r["verdict"] == "refuted")
    uns = sum(1 for r in claims if r["verdict"] == "unsupported")
    qual = sum(1 for r in claims if r["verdict"] == "needs_qualification")
    checkable = sup + ref
    return {"ai_major": len(claims), "supported": sup, "refuted": ref, "unsupported": uns,
            "needs_qualification": qual, "checkable": checkable,
            "refuted_rate": round(ref / checkable, 4) if checkable else 0.0}

def main():
    tags = [t for t in ORDER if _rows(t)]
    models, pooled = [], {"supported": 0, "refuted": 0, "ai_major": 0}
    eff_pooled = {"claimed_major": 0, "total": 0}
    for t in tags:
        rows = _rows(t); st = _stats(t)
        core = _score(rows, "core")
        eff_rows = [r for r in rows if "effector" in r.get("buckets", [])]
        eff_major = sum(1 for r in eff_rows if r["ai_major"])
        models.append({"tag": t, "label": LABEL.get(t, t), "model": st.get("model", t),
                       "cost_usd": st.get("cost_usd", 0), "tokens": st.get("input_tokens", 0) + st.get("output_tokens", 0),
                       "ai_major": core["ai_major"], "supported": core["supported"], "refuted": core["refuted"],
                       "checkable": core["checkable"], "refuted_rate": core["refuted_rate"],
                       "effector_overclaimed": eff_major, "effector_total": len(eff_rows)})
        pooled["supported"] += core["supported"]; pooled["refuted"] += core["refuted"]
        pooled["ai_major"] += core["ai_major"]
        eff_pooled["claimed_major"] += eff_major; eff_pooled["total"] += len(eff_rows)

    checkable = pooled["supported"] + pooled["refuted"]
    headline = {"models": len(tags), "n_core_genes": 220,
                "supported": pooled["supported"], "refuted": pooled["refuted"],
                "checkable": checkable,
                "refuted_rate": round(pooled["refuted"] / checkable, 4) if checkable else 0.0,
                "effector_overclaimed": eff_pooled["claimed_major"], "effector_total": eff_pooled["total"],
                "effector_overclaim_rate": round(eff_pooled["claimed_major"] / eff_pooled["total"], 4) if eff_pooled["total"] else 0.0}

    # phantom_summary.json keeps the shape the web headline already reads
    json.dump({"total_graded": sum(len(_rows(t)) for t in tags), "ai_major_claims": pooled["ai_major"],
               "supported": pooled["supported"], "refuted": pooled["refuted"],
               "checkable": checkable, "refuted_rate": headline["refuted_rate"],
               "models": len(tags), "effector_overclaimed": eff_pooled["claimed_major"],
               "effector_total": eff_pooled["total"],
               "effector_overclaim_rate": headline["effector_overclaim_rate"]},
              open(os.path.join(DATA, "phantom_summary.json"), "w"), indent=2)
    json.dump(models, open(os.path.join(DATA, "model_comparison.json"), "w"), indent=2)

    print(f"HEADLINE (core, pooled over {len(tags)} models): {pooled['refuted']}/{checkable} "
          f"verifiable major-regulator claims contradicted = {headline['refuted_rate']*100:.1f}%")
    print(f"EFFECTOR overclaim: {eff_pooled['claimed_major']}/{eff_pooled['total']} "
          f"checkpoint/cytokine claims called major = {headline['effector_overclaim_rate']*100:.1f}%")
    for m in models:
        print(f"  {m['label']:10s} core {m['refuted']}/{m['checkable']} = {m['refuted_rate']*100:4.1f}% "
              f"· effectors {m['effector_overclaimed']}/{m['effector_total']} · ${m['cost_usd']}")
    return headline

if __name__ == "__main__":
    main()
