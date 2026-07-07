"""Runs the Marson checker against the REAL released DE table slice.
Proves the three demo verdicts on real data:
  VAV1  -> supported   (KD confirmed, >10 DE genes)
  A1BG  -> unsupported (no on-target KD, no effect)
  BCL10 -> needs_qualification (silent at Rest, strong under stim)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

DATA = os.path.join(os.path.dirname(__file__), "..", "examples", "data", "marson_de_demo_slice.csv")

def run():
    ck = MarsonPerturbseqChecker(DATA)
    cases = [
        ("VAV1 true",  Claim("VAV1 is a major regulator of the stimulated CD4 T-cell transcriptome.",
                             gene="VAV1", condition="Stim48hr", asserts_major=True), "supported"),
        ("A1BG phantom", Claim("CRISPRi of A1BG drives a broad activation program in stimulated CD4 T cells.",
                             gene="A1BG", condition="Stim48hr", asserts_major=True), "unsupported"),
        ("BCL10 unqualified", Claim("BCL10 regulates CD4 T-cell state.",
                             gene="BCL10", condition=None, asserts_effect=True), "needs_qualification"),
        ("A1BG target hype", Claim("A1BG is a promising therapeutic target.",
                             gene="A1BG", condition="Stim48hr", strength="promising_target"), "asserted"),
    ]
    ok = True
    for name, claim, expected in cases:
        v = ck.check(claim)
        mark = "PASS" if v.status == expected else "FAIL"
        if v.status != expected: ok = False
        print(f"[{mark}] {name:18s} -> {v.status:20s} (want {expected})")
        print(f"        {v.reason}")
    print("\nALL PASS" if ok else "\nSOME FAILED")
    return ok

if __name__ == "__main__":
    sys.exit(0 if run() else 1)
