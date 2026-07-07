"""Falsification benchmark: build a pack of clean + tampered claims and prove the checker
NEVER admits a tampered claim as 'supported' (zero false admissions), while still passing
genuinely-supported claims. Deterministic, no API - the un-forgeable floor.

  python benchmark/mutation_pack.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = os.path.join(ROOT, "examples", "data", "atlas_backbone.json")
DATA = os.path.join(ROOT, "examples", "data", "marson_de_full.csv")

def max_de(node):
    return max(int(c["n_de"]) for c in node["conditions"].values())

def build_pack(n=10):
    bb = json.load(open(BB))
    # CLEAN: genuine major regulators (constitutive, KD confirmed, >10 DE) claimed major -> should pass
    clean = sorted((x for x in bb if x["class"] == "constitutive_regulator"),
                   key=max_de, reverse=True)[:n]
    # TAMPER-SEMANTIC: verified non-regulators claimed as major -> must NOT pass
    semantic = [x for x in bb if x["class"] == "verified_non_regulator"][:n]
    # TAMPER-MAGNITUDE: real but MINOR regulators (2-10 DE) claimed "major" -> must NOT pass
    def is_minor(x):
        return any(c["status"] == "regulator_minor" for c in x["conditions"].values()) \
               and not any(c["status"] == "regulator_major" for c in x["conditions"].values())
    magnitude = [x for x in bb if is_minor(x)][:n]
    pack = []
    for x in clean:
        pack.append(("clean", Claim(f"{x['gene']} is a major regulator", x["gene"], "Stim48hr", asserts_major=True)))
    for x in semantic:
        pack.append(("tamper_semantic", Claim(f"{x['gene']} is a major regulator", x["gene"], "Stim48hr", asserts_major=True)))
    for x in magnitude:
        pack.append(("tamper_magnitude", Claim(f"{x['gene']} is a major regulator", x["gene"], "Stim48hr", asserts_major=True)))
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
