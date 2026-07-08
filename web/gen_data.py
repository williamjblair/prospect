"""Assemble the frontier into a single JSON the Next.js app fetches from /data/frontier.json.
Mirrors atlas/build.py's data section. Run from prospect/web/."""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from collections import Counter, defaultdict
from loop.find_surprises import mine
from engine.schema import Claim
from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
from examples.openresearch_receipt_client import preview as external_run_receipt_preview
from receipt.causal_bridge import CAUSAL_RULE, EXPLICIT_DRIVER_CLAIMS
from receipt.bridge import export_bridge
from receipt.input_normalizer import ALIASES

DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")
PUB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data")
OUT = os.path.join(PUB, "frontier.json")
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
receipts = [{"id": r["receipt_id"], "status": r["status"], "replayability": r["replayability"],
             "kind": r["kind"], "subject": r["subject"][:6], "claim": r["claim"],
             "accepted": r.get("accepted", False), "producer": r["producer"],
             "n_evidence": len(r.get("evidence", [])), "n_artifacts": len(r.get("artifacts", [])),
             "verifier": r["verifier"]["name"], "replay": r["verifier"]["replay"],
             "signer": (r.get("acceptance") or {}).get("signer")} for r in _receipts_raw]
bridge = export_bridge(BRIDGE_OUT)["manifest"]
external_run_receipt_demo = external_run_receipt_preview()

pggt1b_receipt = next(
    (r for r in _receipts_raw if r.get("kind") == "hypothesis" and "PGGT1B" in r.get("subject", [])),
    None,
)
live_claim_rail = None
if pggt1b_receipt:
    live_claim_rail = {
        "title": "Follow one claim",
        "gene": "PGGT1B",
        "claim": pggt1b_receipt["claim"],
        "status": pggt1b_receipt["status"],
        "receipt_id": pggt1b_receipt["receipt_id"],
        "receipt_kind": pggt1b_receipt["kind"],
        "reproduce_command": pggt1b_receipt["verifier"]["replay"],
        "accepted_event": (pggt1b_receipt.get("acceptance") or {}).get("delta_id", ""),
        "accepted_state": False,
        "why_not_state": "The receipt binds replayable evidence, but the biological claim remains a proposal until orthogonal wet-lab evidence and a human state-signing step.",
        "state_diff": {
            "accepted": False,
            "model_can_apply": False,
            "effect": "proposal_only_no_state_mutation",
            "target": "prospect_marson_cd4_perturbseq",
        },
        "open_obligation": "orthogonal wet-lab evidence before accepted biological state",
        "next_task": "run stimulated primary CD4+ follow-up assay",
        "stages": [
            {"stage": "Claim", "text": pggt1b_receipt["claim"]},
            {"stage": "Receipt", "text": pggt1b_receipt["receipt_id"]},
            {"stage": "State diff", "text": "proposal_only_no_state_mutation"},
            {"stage": "Replay", "text": pggt1b_receipt["verifier"]["replay"]},
            {"stage": "Obligation", "text": "orthogonal wet-lab evidence"},
            {"stage": "Next task", "text": "stimulated primary CD4+ follow-up assay"},
        ],
    }

# Kept packets surfaced in the app.
pggt1b_deep_dive = load("pggt1b_deep_dive.json")
pggt1b_matrix_slice = load("pggt1b_matrix_slice.json")
agent_campaign = load("agent_campaign.json")
discovery_campaign = load("discovery_campaign.json")
cross_validation = load("cross_validation.json")
flagship_module = load("flagship_module.json")
overclaim_counter = load("overclaim_counter.json")
lab_packet = load("lab_packet.json")
lab_writeback_receipt = load("lab_writeback_receipt.json")
finding_index = load("finding_index.json")
disease_genetics_overlay = load("disease_genetics_overlay.json")
ccdc22_defended_evidence = load("ccdc22_defended_evidence.json")
defended_candidate_decisions = load("defended_candidate_decisions.json")
claude_science_acceptance_demo = load("claude_science_acceptance_demo.json")

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
gene_id_map = {"ensembl_to_symbol": {}}
_seen_gene_ids = set()
_assay_rows = defaultdict(list)
with open(os.path.join(DATA, "marson_de_full.csv"), newline="") as f:
    for row in csv.DictReader(f):
        ensembl = row.get("target_contrast", "")
        symbol = row.get("target_contrast_gene_name", "")
        if ensembl and symbol and ensembl not in _seen_gene_ids:
            gene_id_map["ensembl_to_symbol"][ensembl.upper()] = symbol
            _seen_gene_ids.add(ensembl)
        if symbol:
            _assay_rows[symbol].append(row)
acceptance_lookup = {}
for symbol, rows_for_symbol in _assay_rows.items():
    on_target = [r for r in rows_for_symbol if r.get("ontarget_effect_category") == "on-target KD"]
    if on_target:
        best = max(on_target, key=lambda r: int(r["n_total_de_genes"]))
        acceptance_lookup[symbol] = {
            "on_target": True,
            "condition": best["culture_condition"],
            "n_total_de_genes": int(best["n_total_de_genes"]),
        }
    else:
        acceptance_lookup[symbol] = {"on_target": False, "condition": "", "n_total_de_genes": None}
acceptance_rule = {
    "causal_rule": CAUSAL_RULE,
    "aliases": ALIASES,
    "explicit_driver_claims": EXPLICIT_DRIVER_CLAIMS,
    "lookup": acceptance_lookup,
}
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
cross_domain_benchmark = None
if phantom:
    biology_rate = round(float(phantom.get("refuted_rate", 0)), 2)
    effector_rate = round(float(phantom.get("effector_overclaim_rate", 0)), 2)
    math_false = 19
    math_total = 24
    math_rate = round(math_false / math_total, 2)
    cross_domain_benchmark = {
        "title": "Two domains, one trust boundary",
        "status": "evidence_attached",
        "accepted_state_mutation": "none",
        "range": f"{round(biology_rate * 100)}-{round(math_rate * 100)}%",
        "biology": {
            "domain": "biology",
            "source_name": "Prospect Marson CD4+ T-cell overclaiming benchmark",
            "overclaim_rate": biology_rate,
            "effector_overclaim_rate": effector_rate,
            "claims_contradicted": phantom.get("refuted"),
            "claims_checked": phantom.get("checkable"),
        },
        "math": {
            "domain": "math",
            "source_name": "Adversarial falsification audit: 19 of 24 verification claims fail",
            "platform": "OpenResearch, an alphaXiv project",
            "platform_url": "https://openresearch.sh/",
            "claims_false": math_false,
            "claims_total": math_total,
            "false_claim_rate": math_rate,
            "audit_method": "exact-arithmetic re-derivation",
        },
        "boundary": "frozen_rederivation_plus_human_key",
        "claim": "AI-generated scientific claims fail at similar rates when an independent re-derivation checks them.",
        "why_it_matters": "The producer can create activity, but a separate frozen checker and human key decide whether a state transition is accepted.",
    }

data = {
    "stats": {"n_genes": len(nodes), "n_perturbations": sum(len(n["conditions"]) for n in nodes),
              "dist": dict(dist), "n_edges": len(edges)},
    "atlas": atlas, "out": out_adj, "in": in_adj,
    "gene_id_map": gene_id_map,
    "acceptance_rule": acceptance_rule,
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
    "live_claim_rail": live_claim_rail,
    "cross_domain_benchmark": cross_domain_benchmark,
    "pggt1b_deep_dive": pggt1b_deep_dive, "agent_campaign": agent_campaign,
    "discovery_campaign": discovery_campaign,
    "cross_validation": cross_validation,
    "flagship_module": flagship_module,
    "overclaim_counter": overclaim_counter,
    "lab_packet": lab_packet, "lab_writeback_receipt": lab_writeback_receipt,
    "disease_genetics_overlay": disease_genetics_overlay,
    "ccdc22_defended_evidence": ccdc22_defended_evidence,
    "defended_candidate_decisions": defended_candidate_decisions,
    "claude_science_acceptance_demo": claude_science_acceptance_demo,
    "demo": demo, "phantom": phantom, "models": models,
    "frontier": {"root": sig.get("root", ""), "signer": sig.get("signer", ""),
                 "n_nodes": len(nodes), "n_edges": len(edges),
                 "n_contra": len(contradictions), "n_open": len(openq),
                 "n_findings": len(findings)},
}
os.makedirs(PUB, exist_ok=True)
for obj, name in [(pggt1b_deep_dive, "pggt1b_deep_dive.json"), (pggt1b_matrix_slice, "pggt1b_matrix_slice.json"),
                  (agent_campaign, "agent_campaign.json"), (discovery_campaign, "discovery_campaign.json"),
                  (cross_validation, "cross_validation.json"),
                  (flagship_module, "flagship_module.json"),
                  (overclaim_counter, "overclaim_counter.json"),
                  (lab_packet, "lab_packet.json"),
                  (lab_writeback_receipt, "lab_writeback_receipt.json"),
                  (finding_index, "finding_index.json"), (disease_genetics_overlay, "disease_genetics_overlay.json"),
                  (ccdc22_defended_evidence, "ccdc22_defended_evidence.json"),
                  (defended_candidate_decisions, "defended_candidate_decisions.json"),
                  (claude_science_acceptance_demo, "claude_science_acceptance_demo.json")]:
    if obj:
        json.dump(obj, open(os.path.join(PUB, name), "w"))
json.dump(data, open(OUT, "w"))
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB), {len(atlas)} nodes, {len(edges)} edges, "
      f"{len(out_adj)} genes with out-edges, {len(data['contra'])} contradictions")
