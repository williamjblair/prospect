"""Assemble the frontier into a single JSON the Next.js app fetches from /data/frontier.json.
Mirrors atlas/build.py's data section. Run from prospect/web/."""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from collections import Counter, defaultdict
from loop.find_surprises import mine
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
from receipt.bridge import export_bridge

DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data", "frontier.json")
BRIDGE_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data", "receipt_bridge")

def jl(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

nodes = jl(os.path.join(FR, "nodes.jsonl"))
edges = jl(os.path.join(FR, "edges.jsonl"))
contradictions = jl(os.path.join(FR, "contradictions.jsonl"))
openq = jl(os.path.join(FR, "open.jsonl"))
findings = jl(os.path.join(FR, "findings.jsonl"))
_receipts_raw = jl(os.path.join(ROOT, "receipts", "receipts.jsonl"))
receipts = [{"id": r["receipt_id"], "status": r["status"], "replayability": r["replayability"],
             "kind": r["kind"], "subject": r["subject"][:6], "claim": r["claim"],
             "accepted": r.get("accepted", False), "producer": r["producer"],
             "n_evidence": len(r.get("evidence", [])), "n_artifacts": len(r.get("artifacts", [])),
             "verifier": r["verifier"]["name"], "replay": r["verifier"]["replay"],
             "signer": (r.get("acceptance") or {}).get("signer")} for r in _receipts_raw]
bridge_bundle = export_bridge(BRIDGE_OUT)
bridge = bridge_bundle["manifest"]
_vc = os.path.join(DATA, "validation_candidates.csv")
validation = [r for r in csv.DictReader(open(_vc))] if os.path.exists(_vc) else []
citations = json.load(open(os.path.join(DATA, "literature_citations.json")))["citations"] \
    if os.path.exists(os.path.join(DATA, "literature_citations.json")) else {}
_pp = os.path.join(DATA, "proposal_run.json")
proposal = json.load(open(_pp)) if os.path.exists(_pp) else None
_ap = os.path.join(DATA, "agent_run.json")
_asig = os.path.join(DATA, "agent_run.sig.json")
agent = None
if os.path.exists(_ap):
    _a = json.load(open(_ap))
    _s = json.load(open(_asig)) if os.path.exists(_asig) else {}
    agent = {"model": _a["model"], "goal": _a["goal"], "rounds": _a["rounds"],
             "tool_calls": _a["tool_calls"], "cost_usd": _a.get("cost_usd", 0),
             "hypothesis": _a.get("hypothesis"), "delta_id": _a.get("delta_id", ""),
             "signer": _s.get("signer"),
             "transcript": [{"round": t["round"], "tool": t["tool"], "input": t["input"],
                             "result": t.get("result", {})} for t in _a.get("transcript", [])]}
sig = json.load(open(os.path.join(FR, "frontier.sig.json"))) if os.path.exists(os.path.join(FR, "frontier.sig.json")) else {}

def compact(n):
    C = {c: {"s": v["status"], "de": v["n_de"], "dn": v["n_downstream"], "es": round(v["effect_size"], 2)}
         for c, v in n["conditions"].items()}
    return {"g": n["gene"], "cls": n["type"], "st": n["status"], "od": n.get("out_degree", 0),
            "id": n.get("in_degree", 0), "C": C}

atlas = [compact(n) for n in nodes]
dist = Counter(n["type"] for n in nodes)
OUTa, INa = defaultdict(list), defaultdict(list)
for e in edges:
    OUTa[e["source"]].append({"t": e["target"], "d": e["direction"], "e": round(e["effect_size"], 1)})
    INa[e["target"]].append({"s": e["source"], "d": e["direction"], "e": round(e["effect_size"], 1)})
top = lambda v, k=30: sorted(v, key=lambda x: -abs(x["e"]))[:k]
out_adj = {g: top(v) for g, v in OUTa.items() if v}
in_adj = {g: top(v) for g, v in INa.items() if v}

ck = MarsonPerturbseqChecker(os.path.join(DATA, "marson_de_demo_slice.csv"))
demo = [{"text": v.claim.text, "gene": v.claim.gene, "status": v.status, "reason": v.reason}
        for v in (ck.check(Claim(**c)) for c in json.load(open(os.path.join(ROOT, "examples", "claims_demo.json"))))]
phantom = json.load(open(os.path.join(DATA, "phantom_summary.json"))) if os.path.exists(os.path.join(DATA, "phantom_summary.json")) else {}
models = json.load(open(os.path.join(DATA, "model_comparison.json"))) if os.path.exists(os.path.join(DATA, "model_comparison.json")) else []

data = {
    "stats": {"n_genes": len(nodes), "n_perturbations": sum(len(n["conditions"]) for n in nodes),
              "dist": dict(dist), "n_edges": len(edges)},
    "atlas": atlas, "out": out_adj, "in": in_adj,
    "contra": [{"gene": c["subject"], "claimant": c["claimant"], "claim": c["claim"],
                "verdict": c["data_verdict"], "reason": c["reason"]} for c in contradictions],
    "open": [o["gene"] for o in openq[:80]],
    "surprises": mine(os.path.join(DATA, "atlas_backbone.json")),
    "findings": [{"kind": f["kind"], "claim": f["claim"], "status": f["status"],
                  "n_genes": len(f["genes"]), "genes": f["genes"], "evidence": f["evidence"],
                  "cid": f["cid"]} for f in findings],
    "citations": citations,
    "proposal": ({"model": proposal["model"], "proposed": proposal["proposed"],
                  "admitted": proposal["admitted"], "rejected": proposal["rejected"],
                  "cost_usd": proposal.get("cost_usd", 0), "delta_id": proposal.get("delta_id", ""),
                  "items": [{"gene": p["gene"], "verdict": p["verdict"], "rationale": p["rationale"]}
                            for p in proposal["proposals"]]} if proposal else None),
    "agent": agent, "receipts": receipts, "receipt_bridge": bridge, "validation": validation,
    "demo": demo, "phantom": phantom, "models": models,
    "frontier": {"root": sig.get("root", ""), "signer": sig.get("signer", ""),
                 "n_nodes": len(nodes), "n_edges": len(edges),
                 "n_contra": len(contradictions), "n_open": len(openq),
                 "n_findings": len(findings)},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"))
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB), {len(atlas)} nodes, {len(edges)} edges, "
      f"{len(out_adj)} genes with out-edges, {len(data['contra'])} contradictions")
