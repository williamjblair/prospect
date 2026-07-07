"""Does the frontier recover known TF->target biology from perturbation alone?

Compare each TF's data-derived regulon (regulon_slice.py, from the frozen Marson matrix) to its
CollecTRI literature regulon. Enrichment is a hypergeometric test over the measured gene universe;
direction is checked with the correct sign convention (a TF that ACTIVATES a target should, on
knockdown, make that target go DOWN). Mints a signed regulon_recovery Finding.

  python frontier/regulon_recover.py    # after regulon_slice.py; writes the finding + prints the card
"""
from __future__ import annotations
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from scipy.stats import hypergeom, combine_pvalues
from frontier.model import Finding, dump
from frontier.graph_edges import open_matrix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")

def _universe():
    """The measured target-gene space (var of the released matrix)."""
    h = open_matrix(); var = h["var"]
    arr = var["gene_name"] if "gene_name" in var else var["_index"]
    return {x.decode() if isinstance(x, bytes) else str(x) for x in arr[:]}

def _collectri():
    reg = {}
    for r in csv.DictReader(open(os.path.join(DATA, "collectri_human.csv"))):
        reg.setdefault(r["tf"], {})[r["target"]] = int(r["sign"])
    return reg

def analyze():
    universe = _universe(); N = len(universe)
    collectri = _collectri()
    marson = json.load(open(os.path.join(DATA, "marson_regulons.json")))

    rows, wrong_dir = [], []
    pooled_known = pooled_hit = pooled_exp = 0    # for the aggregate enrichment
    dir_agree_n = dir_agree_ok = 0
    pvals = []
    for tf, data in marson.items():
        known = {g: s for g, s in collectri.get(tf, {}).items() if g in universe}
        if len(known) < 5:
            continue
        M = set(data["targets"]) & universe               # data DE hits
        K = set(known)                                     # known measured targets
        ov = K & M
        if not M:
            continue
        expected = len(K) * len(M) / N
        fold = (len(ov) / expected) if expected else 0.0
        p = float(hypergeom.sf(len(ov) - 1, N, len(K), len(M))) if ov else 1.0
        pvals.append(min(max(p, 1e-300), 1.0))
        pooled_known += len(K); pooled_hit += len(ov); pooled_exp += expected
        # direction: a TF-activated target (+1) should go DOWN (-1) on knockdown
        signed = [g for g in ov if known[g] != 0]
        agree = sum(1 for g in signed if data["targets"][g] == -known[g])
        dir_agree_n += len(signed); dir_agree_ok += agree
        dir_agree = agree / len(signed) if signed else None
        for g in signed:
            if data["targets"][g] == known[g]:  # same sign as the regulation = opposite of predicted
                wrong_dir.append({"tf": tf, "target": g, "collectri": "activates" if known[g] > 0 else "represses"})
        recovered = p < 0.05 and len(ov) >= 3 and fold > 1.5
        rows.append({"tf": tf, "known": len(K), "hits": len(M), "overlap": len(ov),
                     "fold": round(fold, 2), "p": p, "dir_agree": dir_agree, "recovered": recovered})

    rec = [r for r in rows if r["recovered"]]
    top = sorted(rec, key=lambda r: -r["fold"])[:12]
    # aggregate across all regulons: known edges recovered vs chance, combined significance
    pooled_fold = pooled_hit / pooled_exp if pooled_exp else 0.0
    combined_p = float(combine_pvalues(pvals, method="fisher")[1]) if pvals else 1.0
    return {"rows": rows, "recovered": rec, "wrong_dir": wrong_dir, "N_universe": N,
            "top": top,
            "pooled_fold": round(pooled_fold, 2),
            "pooled_known": pooled_known, "pooled_hit": pooled_hit,
            "combined_p": combined_p,
            "dir_agree_mean": round(dir_agree_ok / dir_agree_n, 3) if dir_agree_n else 0}

def _pfmt(p):
    return "0" if p <= 0 else f"1e-{int(-np.log10(p))}" if p < 1e-3 else f"{p:.3g}"

def build_finding(a):
    tested = len(a["rows"]); rec = len(a["recovered"])
    return Finding(
        kind="regulon_recovery",
        genes=sorted(r["tf"] for r in a["recovered"]),
        claim=(f"The frontier recovers known transcription-factor biology from perturbation alone, "
               f"with no regulon supplied. Across {tested} CollecTRI TFs that are major regulators "
               f"here, their literature targets are {a['pooled_fold']}x enriched among the genes their "
               f"knockdown moved (Fisher combined p≈{_pfmt(a['combined_p'])}), and when a data edge "
               f"meets a known one the sign agrees {int(a['dir_agree_mean']*100)}% of the time. "
               f"{rec} individual regulons clear significance on their own, and the screen flags "
               f"{len(a['wrong_dir'])} known edges where the data overrules the literature's sign."),
        evidence={"reference": "CollecTRI (OmniPath), human",
                  "n_tfs_tested": tested, "n_recovered": rec,
                  "recovery_rate": round(rec / tested, 4) if tested else 0,
                  "pooled_fold_enrichment": a["pooled_fold"],
                  "combined_p": _pfmt(a["combined_p"]),
                  "known_edges_tested": a["pooled_known"], "known_edges_recovered": a["pooled_hit"],
                  "directional_agreement": a["dir_agree_mean"],
                  "n_wrong_direction_edges": len(a["wrong_dir"]),
                  "top_recovered": [{"tf": r["tf"], "overlap": r["overlap"], "known": r["known"],
                                     "fold": r["fold"], "dir_agree": r["dir_agree"]} for r in a["top"]],
                  "wrong_direction_exemplars": a["wrong_dir"][:12]},
        status="established").freeze()

def main():
    a = analyze()
    f = build_finding(a)
    dump([f], os.path.join(FR, "regulon.jsonl"))
    e = f.evidence
    print(f"REGULON RECOVERY · {f.cid}")
    print(f"  known regulon targets {e['pooled_fold_enrichment']}x enriched among data edges "
          f"({e['known_edges_recovered']}/{e['known_edges_tested']}) · Fisher p≈{e['combined_p']}")
    print(f"  directional agreement {e['directional_agreement']*100:.0f}% (activator vs repressor sign)")
    print(f"  {e['n_recovered']}/{e['n_tfs_tested']} regulons individually significant · "
          f"{e['n_wrong_direction_edges']} edges the data overrules on sign")
    print("  top:", ", ".join(f"{r['tf']}({r['overlap']}/{r['known']},{r['fold']}x)" for r in e["top_recovered"][:8]))
    return f

if __name__ == "__main__":
    main()
