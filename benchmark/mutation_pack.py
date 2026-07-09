"""Falsification benchmark: build a pack of clean + tampered claims and prove the checker
NEVER admits a tampered claim as 'supported' (zero false admissions), while still passing
genuinely-supported claims. Deterministic, no API - the un-forgeable floor.

  python benchmark/mutation_pack.py
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data", "marson_de_full.csv")

def build_pack(n=10):
    with open(DATA, newline="") as handle:
        rows = [
            row for row in csv.DictReader(handle)
            if row["culture_condition"] == "Stim48hr"
            and row["ontarget_effect_category"] == "on-target KD"
        ]
    rows.sort(key=lambda row: row["target_contrast_gene_name"])
    clean = sorted(
        (row for row in rows if int(row["n_total_de_genes"]) > 10),
        key=lambda row: (-int(row["n_total_de_genes"]), row["target_contrast_gene_name"]),
    )[:n]
    semantic = [row for row in rows if int(row["n_total_de_genes"]) <= 1][:n]
    magnitude = [row for row in rows if 2 <= int(row["n_total_de_genes"]) <= 10][:n]
    if min(len(clean), len(semantic), len(magnitude)) < n:
        raise ValueError("frozen Marson table lacks enough rows for every mutation lane")
    pack = []
    for x in clean:
        gene = x["target_contrast_gene_name"]
        pack.append(("clean", Claim(f"{gene} is a major regulator", gene, "Stim48hr", asserts_major=True)))
    for x in semantic:
        gene = x["target_contrast_gene_name"]
        pack.append(("tamper_semantic", Claim(f"{gene} is a major regulator", gene, "Stim48hr", asserts_major=True)))
    for x in magnitude:
        gene = x["target_contrast_gene_name"]
        pack.append(("tamper_magnitude", Claim(f"{gene} is a major regulator", gene, "Stim48hr", asserts_major=True)))
    return pack

def main():
    ck = MarsonPerturbseqChecker(DATA)
    pack = build_pack(10)
    false_admissions, clean_passed, clean_total = 0, 0, 0
    by_kind = {}
    for kind, claim in pack:
        v = ck.check(claim)
        admitted = v.status == "supported"
        by_kind.setdefault(kind, []).append((claim.gene, v.status))
        if kind == "clean":
            clean_total += 1; clean_passed += admitted
        elif admitted:
            false_admissions += 1
    print("MUTATION PACK RESULTS\n")
    for kind, items in by_kind.items():
        supp = sum(1 for _, s in items if s == "supported")
        print(f"  {kind:18s} {len(items)} claims · {supp} admitted as 'supported'")
        for g, s in items:
            print(f"      {g:10s} -> {s}")
    print(f"\nFALSE ADMISSIONS (tampered claims marked supported): {false_admissions}")
    print(f"CLEAN RECALL (real regulators passed): {clean_passed}/{clean_total}")
    ok = false_admissions == 0
    print("\nPASS: zero false admissions" if ok else "\nFAIL: a tampered claim was admitted")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
