"""Freeze ONE benchmark corpus so every model grades the exact same genes and the headline
number and the per-model table describe the same data.

Two buckets, kept separate for honesty:
  core           - a stratified random sample across the four node classes (fixed seed).
                   The unbiased headline contradiction rate is computed over THIS bucket only.
  effector_focus - the finding-#2 effector genes (PD-1, TIM-3, CTLA4, LAG3, IL2, IFNG, ...).
                   A deliberately-chosen subset; its overclaim rate is reported separately and
                   labeled as such, never folded into the headline (that would enrich the sample).

  python loop/make_corpus.py            # writes examples/data/benchmark_corpus.json
"""
from __future__ import annotations
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontier import predicates as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
PER_CLASS = 55     # stratified core: 55 genes x 4 classes = 220
SEED = 7

def main():
    bb = json.load(open(os.path.join(DATA, "atlas_backbone.json")))
    by_gene = {n["gene"]: n for n in bb}
    rng = random.Random(SEED)

    buckets = {}
    for n in bb:
        buckets.setdefault(n["class"], []).append(n["gene"])
    core = []
    for cls, genes in sorted(buckets.items()):
        genes = sorted(genes); rng.shuffle(genes)
        core += [{"gene": g, "class": cls} for g in genes[:PER_CLASS]]
    rng.shuffle(core)

    effector_genes = sorted(g for g, n in by_gene.items() if P.is_regulator_vs_effector(n))
    effector_focus = [{"gene": g, "class": by_gene[g]["class"]} for g in effector_genes]

    core_genes = {c["gene"] for c in core}
    corpus = {"seed": SEED, "per_class": PER_CLASS,
              "core": core,
              "effector_focus": effector_focus,
              "_note": "headline rate = core only; effector_focus reported separately (finding #2)."}
    json.dump(corpus, open(os.path.join(DATA, "benchmark_corpus.json"), "w"), indent=2)
    overlap = len(core_genes & set(effector_genes))
    print(f"corpus: {len(core)} core (stratified, seed={SEED}) + {len(effector_focus)} effector_focus "
          f"({overlap} overlap) -> {len(core_genes | set(effector_genes))} unique genes")
    from collections import Counter
    print("  core class balance:", dict(Counter(c["class"] for c in core)))
    print("  effector_focus:", ", ".join(effector_genes))

if __name__ == "__main__":
    main()
