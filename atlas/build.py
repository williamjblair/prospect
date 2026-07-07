"""Build the Prospect atlas: a self-contained static site over the verified
regulatory atlas + the mined surprises. No server, no API — opens offline.

  python atlas/build.py            # -> atlas/index.html
"""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import Counter
from loop.find_surprises import mine
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BB = os.path.join(ROOT, "examples", "data", "atlas_backbone.json")
DEMO_CLAIMS = os.path.join(ROOT, "examples", "claims_demo.json")
DEMO_DATA = os.path.join(ROOT, "examples", "data", "marson_de_demo_slice.csv")

def compact(node):
    C = {}
    for cond, v in node["conditions"].items():
        C[cond] = {"s": v["status"], "de": v["n_de"], "dn": v["n_downstream"],
                   "es": round(v["effect_size"], 2)}
    return {"g": node["gene"], "cls": node["class"], "ac": node.get("active_conditions", []), "C": C}

def build():
    bb = json.load(open(BB))
    atlas = [compact(n) for n in bb]
    dist = Counter(n["class"] for n in bb)
    n_pert = sum(len(n["conditions"]) for n in bb)
    stats = {"n_genes": len(bb), "n_perturbations": n_pert, "dist": dict(dist)}
    surprises = mine(BB)
    # run the checker on the demo claims for the "refusal" strip
    ck = MarsonPerturbseqChecker(DEMO_DATA)
    demo = []
    for c in json.load(open(DEMO_CLAIMS)):
        v = ck.check(Claim(**c))
        demo.append({"text": v.claim.text, "gene": v.claim.gene, "status": v.status, "reason": v.reason})

    tpl = open(os.path.join(HERE, "template.html")).read()
    out = (tpl.replace("__ATLAS__", json.dumps(atlas))
              .replace("__STATS__", json.dumps(stats))
              .replace("__SURPRISES__", json.dumps(surprises))
              .replace("__DEMO__", json.dumps(demo)))
    path = os.path.join(HERE, "index.html")
    open(path, "w").write(out)
    kb = os.path.getsize(path) // 1024
    print(f"built {path} ({kb} KB) — {stats['n_genes']} genes, "
          f"{len(surprises['hidden_regulators'])} hidden regulators, "
          f"{len(surprises['demoted_famous'])} demoted famous genes")
    return path

if __name__ == "__main__":
    build()
