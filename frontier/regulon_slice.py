"""For every CollecTRI transcription factor that is a major regulator in the Marson screen, slice
its ACTUAL target set from the frozen released matrix via S3 byte-range reads (no full download):
the genes whose expression changed when that TF was knocked down, with direction = sign(log_fc).

This is the data-derived regulon. Comparing it to CollecTRI's literature regulon (regulon_recover.py)
answers: does the frontier recover known TF->target biology from perturbation alone?

  python frontier/regulon_slice.py            # writes examples/data/marson_regulons.json
"""
from __future__ import annotations
import csv, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from frontier.graph_edges import open_matrix, read_col

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
OUT = os.path.join(DATA, "marson_regulons.json")
Q_THRESH, LFC_THRESH = 0.1, 1.0

def _tf_list():
    """CollecTRI TFs that are major regulators (>10 DE) with on-target KD in Marson, and their
    strongest condition (max n_downstream)."""
    tfs = {r["tf"] for r in csv.DictReader(open(os.path.join(DATA, "collectri_human.csv")))}
    bb = {n["gene"]: n for n in json.load(open(os.path.join(DATA, "atlas_backbone.json")))}
    out = {}
    for g in tfs:
        n = bb.get(g)
        if not n:
            continue
        best, best_dn = None, -1
        for c, v in n["conditions"].items():
            if v.get("kd") == "on-target KD" and v.get("n_de", 0) > 10 and v.get("n_downstream", 0) > best_dn:
                best, best_dn = c, v["n_downstream"]
        if best:
            out[g] = best
    return out

def main():
    want = _tf_list()
    print(f"slicing {len(want)} CollecTRI TFs that are major Marson regulators...")
    h = open_matrix()
    var = h["var"]
    targets = np.array([x.decode() if isinstance(x, bytes) else str(x)
                        for x in (var["gene_name"] if "gene_name" in var else var["_index"])[:]])
    obs = h["obs"]
    src = read_col(obs, "target_contrast_gene_name")
    cond = read_col(obs, "culture_condition")
    idx = {(str(src[i]), str(cond[i])): i for i in range(len(src))}

    regulons, t0 = {}, time.time()
    for k, (tf, c) in enumerate(sorted(want.items())):
        i = idx.get((tf, c))
        if i is None:
            continue
        lfc = np.asarray(h["layers/log_fc"][i, :]).ravel()
        q = np.asarray(h["layers/adj_p_value"][i, :]).ravel()
        sig = np.where((q < Q_THRESH) & (np.abs(lfc) > LFC_THRESH) & (targets != tf))[0]
        # direction of the TARGET under TF knockdown: down = TF-activated, up = TF-repressed
        tg = {str(targets[j]): (1 if lfc[j] > 0 else -1) for j in sig}
        regulons[tf] = {"condition": c, "n_targets": len(tg), "targets": tg}
        if k % 25 == 0:
            print(f"  {k+1}/{len(want)} · {tf} ({len(tg)} targets) · {time.time()-t0:.0f}s")
    json.dump(regulons, open(OUT, "w"))
    sizes = sorted((v["n_targets"] for v in regulons.values()))
    print(f"\nwrote {OUT}: {len(regulons)} data-derived regulons · "
          f"target counts median {sizes[len(sizes)//2]}, max {sizes[-1]}")

if __name__ == "__main__":
    main()
