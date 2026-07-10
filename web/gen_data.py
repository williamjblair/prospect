"""Assemble the frontier into a single JSON the Next.js app fetches from /data/frontier.json.
Mirrors atlas/build.py's data section. Run from prospect/web/."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from collections import Counter, defaultdict
from loop.find_surprises import mine
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
from examples.openresearch_receipt_client import preview as external_run_receipt_preview
from receipt.bridge import export_bridge

DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")
PUB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data")
OUT = os.path.join(PUB, "frontier.json")
CHECK_OUT = os.path.join(PUB, "check.json")
BRIDGE_OUT = os.path.join(PUB, "receipt_bridge")

def jl(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def load(name):
    p = os.path.join(DATA, name)
    return json.load(open(p)) if os.path.exists(p) else None

PUBLIC_CLASS = {"verified_non_regulator": "reproduced_non_regulator"}
def public_class(value): return PUBLIC_CLASS.get(value, value)

nodes = jl(os.path.join(FR, "nodes.jsonl"))
edges = jl(os.path.join(FR, "edges.jsonl"))
contradictions = jl(os.path.join(FR, "contradictions.jsonl"))
openq = jl(os.path.join(FR, "open.jsonl"))
findings = jl(os.path.join(FR, "findings.jsonl"))
_receipts_raw = jl(os.path.join(ROOT, "receipts", "receipts.jsonl"))
if any(r.get("accepted") is not False for r in _receipts_raw):
    raise ValueError("Receipt v1 projection refused an accepted receipt; acceptance requires a separate event")

PUBLIC_RECEIPT_CLAIMS = {
    "regulator_vs_effector": (
        "Eighteen field-targeted genes have effective knockdown but near-zero stimulated transcriptome "
        "reach in this assay. The result limits a broad causal-driver claim for this readout."
    ),
    "essentiality_artifact": (
        "High Rest reach argues against activation specificity, but does not by itself establish "
        "housekeeping or essentiality. GSE278572 qualifies MED12."
    ),
    "cross_cell_type_transfer": (
        "K562 and covered RPE1 rows provide orthogonal evidence about cross-cell reach. Breadth is not "
        "an essentiality label, and noncoverage is not refutation."
    ),
    "regulon_recovery": (
        "Known CollecTRI targets are enriched among moved genes. Sign disagreements remain "
        "context-sensitive review candidates."
    ),
    "hypothesis": (
        "PGGT1B is a proposal-only stimulated CD4+ activation-transcriptome hypothesis. Comparable "
        "independent replication and donor or batch specificity remain open."
    ),
}
PUBLIC_RECEIPT_STATUS = {"regulator_vs_effector": "computationally_reproduced"}

receipts = []
for r in _receipts_raw:
    attestation = r.get("acceptance") or {}
    receipts.append({
        "id": r["receipt_id"],
        "status": PUBLIC_RECEIPT_STATUS.get(r["kind"], r["status"]),
        "replayability": r["replayability"],
        "kind": r["kind"],
        "subject": r["subject"][:6],
        "claim": PUBLIC_RECEIPT_CLAIMS.get(r["kind"], r["claim"]),
        "accepted": False,
        "producer": r["producer"],
        "n_evidence": len(r.get("evidence", [])),
        "n_artifacts": len(r.get("artifacts", [])),
        "verifier": r["verifier"]["name"],
        "replay": r["verifier"]["replay"],
        "legacy_attestation": attestation.get("attestation_type") == "legacy_frontier_root_signature",
        "covered_root": attestation.get("covered_root", ""),
        "attestor": attestation.get("signer", ""),
        "interpretation_qualified": r["kind"] in PUBLIC_RECEIPT_CLAIMS,
    })
bridge = export_bridge(BRIDGE_OUT)["manifest"]
external_run_receipt_demo = external_run_receipt_preview()

# Kept packets surfaced in the app.
pggt1b_deep_dive = load("pggt1b_deep_dive.json")
overclaim_counter = load("overclaim_counter.json")
finding_index = load("finding_index.json")
pggt1b_defended_evidence = load("pggt1b_defended_evidence.json")
claude_science_acceptance_demo = load("claude_science_acceptance_demo.json")
substrate_coverage_report = load("substrate_coverage_report.json")
gse278572_comparator = load("gse278572_comparator.json")
gse271788_calibration = load("gse271788_calibration.json")

citations = load("literature_citations.json")
citations = citations["citations"] if citations else {}
proposal = load("proposal_run.json")
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
    return {"g": n["gene"], "cls": public_class(n["type"]), "st": n["status"], "od": n.get("out_degree", 0),
            "id": n.get("in_degree", 0), "C": C}

atlas = [compact(n) for n in nodes]
dist = Counter(public_class(n["type"]) for n in nodes)
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
phantom = load("phantom_summary.json") or {}
models = load("model_comparison.json") or []
data = {
    "stats": {"n_genes": len(nodes), "n_perturbations": sum(len(n["conditions"]) for n in nodes),
              "dist": dict(dist), "n_edges": len(edges)},
    "atlas": atlas, "out": out_adj, "in": in_adj,
    "contra": [{"gene": c["subject"], "claimant": c["claimant"], "claim": c["claim"],
                "verdict": c["data_verdict"], "reason": c["reason"]} for c in contradictions],
    "open": [o["gene"] for o in openq[:80]],
    "surprises": mine(os.path.join(DATA, "atlas_backbone.json")),
    "finding_index": finding_index,
    "findings": [{"kind": f["kind"], "claim": f["claim"], "status": f["status"],
                  "n_genes": len(f["genes"]), "genes": f["genes"], "evidence": f["evidence"],
                  "cid": f["cid"]} for f in findings],
    "citations": citations,
    "proposal": ({"model": proposal["model"], "proposed": proposal["proposed"],
                  "admitted": proposal["admitted"], "rejected": proposal["rejected"],
                  "cost_usd": proposal.get("cost_usd", 0), "delta_id": proposal.get("delta_id", ""),
                  "items": [{"gene": p["gene"], "verdict": p["verdict"], "rationale": p["rationale"]}
                            for p in proposal["proposals"]]} if proposal else None),
    "agent": agent, "receipts": receipts, "receipt_bridge": bridge,
    "external_run_receipt_demo": external_run_receipt_demo,
    "pggt1b_deep_dive": pggt1b_deep_dive,
    "overclaim_counter": overclaim_counter,
    "pggt1b_defended_evidence": pggt1b_defended_evidence,
    "claude_science_acceptance_demo": claude_science_acceptance_demo,
    "substrate_coverage_report": substrate_coverage_report,
    "gse278572_comparator": gse278572_comparator,
    "gse271788_calibration": gse271788_calibration,
    "demo": demo, "phantom": phantom, "models": models,
    "frontier": {"root": sig.get("root", ""), "signer": sig.get("signer", ""),
                 "n_nodes": len(nodes), "n_edges": len(edges),
                 "n_contra": len(contradictions), "n_open": len(openq),
                 "n_findings": len(findings)},
}
os.makedirs(PUB, exist_ok=True)
for obj, name in [(pggt1b_deep_dive, "pggt1b_deep_dive.json"),
                  (overclaim_counter, "overclaim_counter.json"),
                  (finding_index, "finding_index.json"),
                  (pggt1b_defended_evidence, "pggt1b_defended_evidence.json"),
                  (claude_science_acceptance_demo, "claude_science_acceptance_demo.json"),
                  (substrate_coverage_report, "substrate_coverage_report.json"),
                  (gse278572_comparator, "gse278572_comparator.json"),
                  (gse271788_calibration, "gse271788_calibration.json")]:
    if obj:
        json.dump(obj, open(os.path.join(PUB, name), "w"))
json.dump(data, open(OUT, "w"))
check_data = {**data, "atlas": [], "out": {}, "in": {}}
json.dump(check_data, open(CHECK_OUT, "w"))
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB), {len(atlas)} nodes, {len(edges)} edges, "
      f"{len(out_adj)} genes with out-edges, {len(data['contra'])} contradictions")
print(f"wrote {CHECK_OUT} ({os.path.getsize(CHECK_OUT)//1024} KB), graph deferred until explorer opens")
