"""The Skill ships a dependency-free re-implementation of the check ladder
(skill/scripts/check.py) so it can run inside Claude with no pandas. That is a second copy of
the logic - this test pins the two together: pointed at the same frozen slice, the engine checker
and the skill checker must return the SAME verdict for every claim. If they ever diverge, this
fails, so the copies cannot silently drift.

  python tests/test_skill_parity.py
"""
import csv, importlib.util, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SLICE = os.path.join(ROOT, "skill", "references", "marson_de_slice.csv")
CONDS = ["Rest", "Stim8hr", "Stim48hr", None]

from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

# load the skill's stdlib checker as a module (it is not importable as a package)
_spec = importlib.util.spec_from_file_location(
    "skill_check", os.path.join(ROOT, "skill", "scripts", "check.py"))
skill = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(skill)

def main():
    genes = sorted({r["target_contrast_gene_name"] for r in csv.DictReader(open(SLICE))})
    engine = MarsonPerturbseqChecker(SLICE)
    by = skill.load_table(SLICE)

    cases, mismatches = 0, []
    for g in genes:
        for cond in CONDS:
            for major in (True, False):
                for strength in ("quantitative", "promising_target"):
                    c = {"gene": g, "condition": cond, "asserts_major": major,
                         "strength": strength, "text": f"{g} claim"}
                    eng = engine.check(Claim(**c)).status
                    skl = skill.check(c, by)[0]
                    cases += 1
                    if eng != skl:
                        mismatches.append((g, cond, major, strength, eng, skl))

    print(f"skill/engine parity: {cases} claims checked · {len(mismatches)} mismatches")
    for m in mismatches:
        print(f"  DRIFT {m[0]} cond={m[1]} major={m[2]} {m[3]}: engine={m[4]} skill={m[5]}")
    if mismatches:
        sys.exit("FAIL: the Skill checker has drifted from the engine")
    print("PASS: the Skill checker matches the engine on every claim")

if __name__ == "__main__":
    main()
