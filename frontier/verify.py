"""Re-derive every node/edge/contradiction content_id from its frozen fields and confirm it
matches the stored id. This is the EXACT-lane floor: a hand-edited or fabricated frontier
object fails, because the id is a pure function of the frozen source-derived fields - an
admission that is re-derived, not self-asserted.

  python frontier/verify.py
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontier.model import Node, Edge, Contradiction, OpenQuestion, Finding

FR = os.path.dirname(os.path.abspath(__file__))
KINDS = {"nodes.jsonl": Node, "edges.jsonl": Edge,
         "contradictions.jsonl": Contradiction, "open.jsonl": OpenQuestion,
         "findings.jsonl": Finding}

def verify():
    total = drift = 0; cids = []
    for fname, cls in KINDS.items():
        path = os.path.join(FR, fname)
        if not os.path.exists(path):
            continue
        for l in open(path):
            d = json.loads(l); stored = d.pop("cid", "")
            obj = cls(**d).freeze()          # recompute from frozen fields
            total += 1; cids.append(obj.cid)
            if obj.cid != stored:
                drift += 1
                print(f"  DRIFT in {fname}: "
                      f"{d.get('gene') or d.get('source') or d.get('subject') or d.get('kind')} "
                      f"stored={stored} recomputed={obj.cid}")
    root = "root_" + hashlib.sha256("".join(sorted(cids)).encode()).hexdigest()[:16]
    print(f"\nverified {total} objects · {drift} drift")
    print(f"frontier root: {root}")
    print("EXACT-lane PASS: every object re-derives from frozen data" if drift == 0
          else "FAIL: some objects do not re-derive")
    return drift == 0, root

if __name__ == "__main__":
    ok, _ = verify()
    sys.exit(0 if ok else 1)
