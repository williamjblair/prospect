"""Assemble the verified regulatory frontier: typed nodes (from the classified backbone),
real gene->gene edges (sliced from the released matrix by graph_edges.py), contradictions
(from the AI-claim overlay — first-class), and open questions (untestable genes). Everything
content-addressed and re-derivable from frozen data.

  python frontier/graph_edges.py --top 60   # (once) slice edges from S3
  python frontier/build.py                   # assemble the frontier
"""
from __future__ import annotations
import glob, json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontier.model import Node, Edge, Contradiction, OpenQuestion, dump
from frontier.findings import build_findings, literature_contradictions
from frontier.transfer import build_transfer, REPLOGLE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")

STATUS = {"constitutive_regulator": "established", "condition_specific_regulator": "established",
          "verified_non_regulator": "established", "unverifiable_no_kd": "open", "off_target": "open"}

def load_edges():
    p = os.path.join(FR, "edges_raw.jsonl")
    if not os.path.exists(p):
        print("  (no edges_raw.jsonl yet — run frontier/graph_edges.py first)"); return []
    return [json.loads(l) for l in open(p)]

def load_contradictions():
    """Every AI 'major regulator' claim the data refuted/couldn't-support -> a Contradiction."""
    out = []
    for path in glob.glob(os.path.join(DATA, "claims_*.jsonl")):
        model = os.path.basename(path).replace("claims_", "").replace(".jsonl", "")
        for l in open(path):
            r = json.loads(l)
            if r.get("ai_major") and r["verdict"] in ("refuted", "unsupported"):
                out.append(Contradiction(subject=r["gene"], claimant=f"claude-{model}",
                    claim=r.get("ai_claim") or f"{r['gene']} is a major regulator",
                    data_verdict=r["verdict"], reason=r["reason"]).freeze())
    return out

def build():
    bb = json.load(open(os.path.join(DATA, "atlas_backbone.json")))
    bb_by_gene = {n["gene"]: n for n in bb}
    edges = load_edges()
    # contradictions: AI-overlay claims (first-class) + literature-vs-data (finding #2)
    contradictions = load_contradictions() + literature_contradictions(bb_by_gene)
    findings = build_findings(bb_by_gene)
    if os.path.exists(REPLOGLE):                 # cross-cell-type transfer (Replogle K562)
        findings.append(build_transfer())
    reg_path = os.path.join(FR, "regulon.jsonl")  # regulon recovery (computed offline, needs S3)
    if os.path.exists(reg_path):
        from frontier.model import Finding
        findings += [Finding(**json.loads(l)) for l in open(reg_path)]
    contested = {c.subject for c in contradictions}

    # degrees from the real edges
    out_deg, in_deg = Counter(), Counter()
    for e in edges:
        out_deg[e["source"]] += 1; in_deg[e["target"]] += 1

    nodes = []
    for n in bb:
        g = n["gene"]
        status = "contradicted" if g in contested else STATUS.get(n["class"], "open")
        nodes.append(Node(gene=g, type=n["class"], status=status,
                          conditions=n["conditions"], out_degree=out_deg.get(g, 0),
                          in_degree=in_deg.get(g, 0)).freeze())
    open_qs = [OpenQuestion(gene=n["gene"], reason="no_knockdown").freeze()
               for n in bb if n["class"] == "unverifiable_no_kd"]

    dump(nodes, os.path.join(FR, "nodes.jsonl"))
    dump([Edge(**{k: e[k] for k in ("source","target","condition","direction","effect_size","q","kind","dataset")}).freeze()
          for e in edges], os.path.join(FR, "edges.jsonl")) if edges else None
    dump(contradictions, os.path.join(FR, "contradictions.jsonl"))
    dump(open_qs, os.path.join(FR, "open.jsonl"))
    dump(findings, os.path.join(FR, "findings.jsonl"))

    print(f"FRONTIER: {len(nodes)} nodes · {len(edges)} edges · "
          f"{len(contradictions)} contradictions · {len(open_qs)} open questions · "
          f"{len(findings)} findings")
    for f in findings:
        print(f"  finding · {f.kind:24s} {len(f.genes):4d} genes · {f.status}")
    if edges:
        hubs = out_deg.most_common(5)
        print("  top regulatory hubs (out-degree):", ", ".join(f"{g}({d})" for g, d in hubs))
        for demo in ("VAV1", "BCL10", "TADA2B", "BCAT2"):
            if out_deg.get(demo):
                print(f"  {demo}: regulates {out_deg[demo]} genes (out) · regulated by {in_deg.get(demo,0)} (in)")
    return nodes, edges, contradictions, open_qs, findings

if __name__ == "__main__":
    build()
