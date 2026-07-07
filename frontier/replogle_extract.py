"""Derive a small, committable per-gene transcriptional-strength table for K562 from the
Replogle et al. 2022 genome-scale Perturb-seq pseudobulk (Cell 2022, PMID 35688146). We never
recompute a DE test: Replogle already reports, per perturbation, the number of differentially
expressed genes (Mann-Whitney and Anderson-Darling counts) in obs. We just read those.

  python frontier/replogle_extract.py <h5ad> [out_csv] [de_col]
  # K562: python frontier/replogle_extract.py .../K562_gwps_normalized_bulk_01.h5ad
  # RPE1: python frontier/replogle_extract.py .../rpe1_normalized_bulk_01.h5ad examples/data/replogle_rpe1_de.csv rpe1_de

Writes  gene, <de_col>, is_control. This is a frozen second/third dataset the transfer verifier
reads. The big h5ad is never committed.
"""
import csv, os, sys
import h5py

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "examples", "data", "replogle_k562_de.csv")

def _gene(transcript):
    # "10023_ZC3H18_P1P2_ENSG00000158545" -> "ZC3H18"
    p = transcript.split("_")
    return p[1] if len(p) > 1 else transcript

def main(h5_path, out=DEFAULT_OUT, de_col="k562_de"):
    f = h5py.File(h5_path, "r")
    gt = [x.decode() if isinstance(x, bytes) else str(x) for x in f["obs/gene_transcript"][:]]
    mw = f["obs/mann_whitney_counts"][:]
    cc = f["obs/core_control"][:]
    best = {}
    for i, t in enumerate(gt):
        g = _gene(t)
        row = {"gene": g, de_col: int(mw[i]), "is_control": bool(cc[i])}
        if g not in best or row[de_col] > best[g][de_col]:
            best[g] = row
    rows = sorted(best.values(), key=lambda r: -r[de_col])
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["gene", de_col, "is_control"])
        w.writeheader(); w.writerows(rows)
    ctrl = sum(1 for r in rows if r["is_control"])
    print(f"wrote {out}: {len(rows)} genes ({ctrl} controls) · "
          f"{de_col} range {rows[-1][de_col]}–{rows[0][de_col]}")
    print("  strongest:", ", ".join(f"{r['gene']}({r[de_col]})" for r in rows[:8]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: replogle_extract.py <h5ad> [out_csv] [de_col]")
    main(*sys.argv[1:])
