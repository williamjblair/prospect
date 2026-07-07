"""Compute the honest phantom-rate summary from claims.jsonl.
Separates 'refuted' (knockdown worked, AI's major-regulator claim contradicted) from
'untestable' (no knockdown, can't check) — never launders one into the other.

  python loop/score.py
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = os.path.join(ROOT, "examples", "data", "claims.jsonl")

def score(path=CLAIMS):
    out = path.replace("claims", "phantom_summary").replace(".jsonl", ".json")
    rows = [json.loads(l) for l in open(path)]
    ai = [r for r in rows if r["ai_major"]]
    supported = sum(r["verdict"] == "supported" for r in ai)
    refuted   = sum(r["verdict"] == "refuted" for r in ai)
    qual      = sum(r["verdict"] == "needs_qualification" for r in ai)
    untestable = sum(r["verdict"] == "unsupported" for r in ai)   # no knockdown
    checkable = supported + refuted + qual                        # knockdown confirmed
    rate = refuted / checkable if checkable else 0.0
    s = {"total_graded": len(rows), "ai_major_claims": len(ai),
         "supported": supported, "refuted": refuted, "needs_qualification": qual,
         "untestable_no_kd": untestable, "checkable": checkable,
         "refuted_rate": round(rate, 3)}
    json.dump(s, open(out, "w"), indent=2)
    print(json.dumps(s, indent=2))
    print(f"\nHEADLINE: of {checkable} confident AI 'major regulator' claims we could verify, "
          f"{refuted} were contradicted by the data = {rate:.0%}")
    return s

if __name__ == "__main__":
    score(sys.argv[1] if len(sys.argv) > 1 else CLAIMS)
