"""Build the Prospect frontier UI: a self-contained static site over the reproduced regulatory
frontier - typed nodes, real gene->gene edges (regulatory neighborhoods), first-class
contradictions, and the open frontier. No server, no API; opens offline.

  python frontier/graph_edges.py --top 200   # slice edges from S3 (once)
  python frontier/build.py                    # assemble the frontier
  python atlas/build.py                       # -> atlas/index.html
"""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import Counter, defaultdict
from loop.find_surprises import mine
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")
DEMO_CLAIMS = os.path.join(ROOT, "examples", "claims_demo.json")
DEMO_DATA = os.path.join(DATA, "marson_de_demo_slice.csv")

def jl(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []

def compact_node(n):
    C = {}
    for cond, v in n["conditions"].items():
        C[cond] = {"s": v["status"], "de": v["n_de"], "dn": v["n_downstream"],
                   "es": round(v["effect_size"], 2)}
    return {"g": n["gene"], "cls": n["type"], "st": n["status"],
            "od": n.get("out_degree", 0), "id": n.get("in_degree", 0), "C": C}

def build():
    nodes = jl(os.path.join(FR, "nodes.jsonl")) or _from_backbone()
    edges = jl(os.path.join(FR, "edges.jsonl"))
    contradictions = jl(os.path.join(FR, "contradictions.jsonl"))
    openq = jl(os.path.join(FR, "open.jsonl"))
    sig = json.load(open(os.path.join(FR, "frontier.sig.json"))) if os.path.exists(os.path.join(FR, "frontier.sig.json")) else {}

    atlas = [compact_node(n) for n in nodes]
    dist = Counter(n["type"] for n in nodes)
    n_pert = sum(len(n["conditions"]) for n in nodes)
    stats = {"n_genes": len(nodes), "n_perturbations": n_pert, "dist": dict(dist),
             "n_edges": len(edges)}

    # regulatory neighborhoods: top targets/sources per gene by |effect|
    OUT, IN = defaultdict(list), defaultdict(list)
    for e in edges:
        OUT[e["source"]].append({"t": e["target"], "d": e["direction"], "e": round(e["effect_size"], 1)})
        IN[e["target"]].append({"s": e["source"], "d": e["direction"], "e": round(e["effect_size"], 1)})
    def top(lst, k=24):
        return sorted(lst, key=lambda x: -abs(x["e"]))[:k]
    out_adj = {g: top(v) for g, v in OUT.items() if v}
    in_adj = {g: top(v) for g, v in IN.items() if v}

    contra = [{"gene": c["subject"], "claimant": c["claimant"], "claim": c["claim"],
               "verdict": c["data_verdict"], "reason": c["reason"]} for c in contradictions]
    open_sample = [o["gene"] for o in openq[:60]]
    frontier = {"root": sig.get("root", ""), "signer": sig.get("signer", ""),
                "n_nodes": len(nodes), "n_edges": len(edges),
                "n_contra": len(contradictions), "n_open": len(openq)}

    surprises = mine(os.path.join(DATA, "atlas_backbone.json"))
    ck = MarsonPerturbseqChecker(DEMO_DATA)
    demo = [{"text": v.claim.text, "gene": v.claim.gene, "status": v.status, "reason": v.reason}
            for v in (ck.check(Claim(**c)) for c in json.load(open(DEMO_CLAIMS)))]
    phantom = json.load(open(os.path.join(DATA, "phantom_summary.json"))) if os.path.exists(os.path.join(DATA, "phantom_summary.json")) else {}
    models = json.load(open(os.path.join(DATA, "model_comparison.json"))) if os.path.exists(os.path.join(DATA, "model_comparison.json")) else []

    tpl = open(os.path.join(HERE, "template.html")).read()
    for k, v in {"ATLAS": atlas, "STATS": stats, "SURPRISES": surprises, "DEMO": demo,
                 "PHANTOM": phantom, "MODELS": models, "OUT": out_adj, "IN": in_adj,
                 "CONTRA": contra, "OPEN": open_sample, "FRONTIER": frontier}.items():
        tpl = tpl.replace(f"__{k}__", json.dumps(v))
    path = os.path.join(HERE, "index.html")
    open(path, "w").write(tpl)
    print(f"built {path} ({os.path.getsize(path)//1024} KB) - {len(nodes)} nodes, "
          f"{len(edges)} edges, {len(contra)} contradictions, {len(openq)} open")
    return path

def _from_backbone():
    bb = json.load(open(os.path.join(DATA, "atlas_backbone.json")))
    return [{"gene": n["gene"], "type": n["class"], "status": "established",
             "conditions": n["conditions"], "out_degree": 0, "in_degree": 0} for n in bb]

if __name__ == "__main__":
    build()
