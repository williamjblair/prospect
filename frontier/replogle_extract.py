"""Derive a small, committable per-gene transcriptional-strength table for K562 from the
Replogle et al. 2022 genome-scale Perturb-seq pseudobulk (Cell 2022, PMID 35688146). We never
recompute a DE test: Replogle already reports, per perturbation, the number of differentially
expressed genes (Mann-Whitney and Anderson-Darling counts) in obs. We just read those.

  python frontier/replogle_extract.py <path-to>/K562_gwps_normalized_bulk_01.h5ad

Writes examples/data/replogle_k562_de.csv:  gene, k562_de, k562_ad, is_control
This is the frozen second dataset the transfer verifier reads. The big h5ad is never committed.
"""
import csv, os, sys
import h5py

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "examples", "data", "replogle_k562_de.csv")

def _gene(transcript):
    # "10023_ZC3H18_P1P2_ENSG00000158545" -> "ZC3H18"
    p = transcript.split("_")
    return p[1] if len(p) > 1 else transcript

def main(h5_path):
    f = h5py.File(h5_path, "r")
    gt = [x.decode() if isinstance(x, bytes) else str(x) for x in f["obs/gene_transcript"][:]]
    mw = f["obs/mann_whitney_counts"][:]
    ad = f["obs/anderson_darling_counts"][:]
    cc = f["obs/core_control"][:]
    # one row per gene; if a gene has multiple guides/transcripts, keep the strongest signal
    best = {}
    for i, t in enumerate(gt):
        g = _gene(t)
        row = {"gene": g, "k562_de": int(mw[i]), "k562_ad": int(ad[i]), "is_control": bool(cc[i])}
        if g not in best or row["k562_de"] > best[g]["k562_de"]:
            best[g] = row
    rows = sorted(best.values(), key=lambda r: -r["k562_de"])
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["gene", "k562_de", "k562_ad", "is_control"])
        w.writeheader(); w.writerows(rows)
    ctrl = sum(1 for r in rows if r["is_control"])
    print(f"wrote {OUT}: {len(rows)} genes ({ctrl} controls) · "
          f"K562 DE range {rows[-1]['k562_de']}–{rows[0]['k562_de']}")
    print("  strongest:", ", ".join(f"{r['gene']}({r['k562_de']})" for r in rows[:8]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: replogle_extract.py <h5ad>"))
