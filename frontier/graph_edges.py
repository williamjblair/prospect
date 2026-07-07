"""Slice REAL gene->gene regulatory edges from the 16.8GB released DE matrix, directly from
S3 via byte-range reads (anon; no full download). For each selected perturbation, read its
released log_fc + adj_p_value across all 10,282 genes, threshold, and emit typed edges
(source knockdown -> target changes, direction = sign(log_fc)). Frozen released data only -
never a live recompute.

  python frontier/graph_edges.py --top 60 --condition Stim48hr
"""
from __future__ import annotations
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from frontier.model import Edge

S3PATH = "genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.DE_stats.h5ad"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "frontier", "edges_raw.jsonl")

def open_matrix():
    import s3fs, h5py
    fs = s3fs.S3FileSystem(anon=True)
    f = fs.open(S3PATH, "rb", block_size=2**20)
    return h5py.File(f, "r")

def read_col(obs, name):
    import h5py
    g = obs[name]
    if isinstance(g, h5py.Group) and "categories" in g:
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
        codes = g["codes"][:]
        return np.array([cats[c] if c >= 0 else None for c in codes], dtype=object)
    return np.array([x.decode() if isinstance(x, bytes) else x for x in g[:]], dtype=object)

def build_edges(top=60, condition="Stim48hr", q_thresh=0.1, lfc_thresh=1.0,
                include=None, out=OUT, max_targets=400):
    h = open_matrix()
    var = h["var"]
    targets = np.array([x.decode() if isinstance(x, bytes) else str(x)
                        for x in (var["gene_name"] if "gene_name" in var else var["_index"])[:]])
    obs = h["obs"]
    src = read_col(obs, "target_contrast_gene_name")
    cond = read_col(obs, "culture_condition")
    ndown = np.asarray(obs["n_downstream"][:]).astype(float)

    mask = (cond == condition)
    order = np.argsort(-np.where(mask, ndown, -1))
    picks = list(order[:top])
    if include:
        for g in include:
            hits = np.where((src == g) & (cond == condition))[0]
            picks += [i for i in hits if i not in picks]

    fh = open(out, "w"); n_edges = 0; t0 = time.time()
    for k, i in enumerate(picks):
        g = str(src[i])
        lfc = np.asarray(h["layers/log_fc"][i, :]).ravel()
        q = np.asarray(h["layers/adj_p_value"][i, :]).ravel()
        sig = np.where((q < q_thresh) & (np.abs(lfc) > lfc_thresh) & (targets != g))[0]
        # cap per-source targets by strongest effect so the graph stays tractable
        if len(sig) > max_targets:
            sig = sig[np.argsort(-np.abs(lfc[sig]))[:max_targets]]
        for j in sig:
            e = Edge(source=g, target=str(targets[j]), condition=condition,
                     direction="up" if lfc[j] > 0 else "down",
                     effect_size=float(lfc[j]), q=float(q[j])).freeze()
            fh.write(json.dumps(e.__dict__) + "\n"); n_edges += 1
        if k % 10 == 0:
            print(f"  {k+1}/{len(picks)} perturbations · {n_edges} edges · {time.time()-t0:.0f}s")
    fh.close()
    print(f"\n{n_edges} edges from {len(picks)} perturbations -> {out}")
    return n_edges

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--condition", default="Stim48hr")
    ap.add_argument("--include", nargs="*", default=["VAV1", "BCL10", "TADA2B", "BCAT2"])
    a = ap.parse_args()
    build_edges(top=a.top, condition=a.condition, include=a.include)
