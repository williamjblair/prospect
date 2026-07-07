"""An autonomous Claude research agent on the verified frontier.

Claude pursues a research goal by CALLING frozen-data tools (search, check, cross-cell-type,
known-regulon) in a real tool-use loop. Every fact it reasons over is a deterministic lookup
against a released table, so the agent cannot hallucinate its evidence. It converges on a novel
hypothesis, which a human then signs. No model is in the trust path: the tools are frozen and the
acceptance is a key.

  python loop/agent.py            # runs the loop, writes examples/data/agent_run.json
  python loop/agent.py --sign     # human-accept the agent's verified hypothesis
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loop.run import load_env, price_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
RUN = os.path.join(DATA, "agent_run.json")
SIG = os.path.join(DATA, "agent_run.sig.json")
KEY = os.path.join(ROOT, "frontier", ".prospect_signing_key")
MODEL = "claude-opus-4-8"
MAX_ROUNDS = 10

# --- frozen-data tools (deterministic lookups; the agent's only source of fact) ---------------
from frontier import predicates as P
_BB = {n["gene"]: n for n in json.load(open(os.path.join(DATA, "atlas_backbone.json")))}
_K562 = {r["gene"]: int(r["k562_de"]) for r in csv.DictReader(open(os.path.join(DATA, "replogle_k562_de.csv")))} \
    if os.path.exists(os.path.join(DATA, "replogle_k562_de.csv")) else {}
_RPE1 = {r["gene"]: int(r["rpe1_de"]) for r in csv.DictReader(open(os.path.join(DATA, "replogle_rpe1_de.csv")))} \
    if os.path.exists(os.path.join(DATA, "replogle_rpe1_de.csv")) else {}
_COLLECTRI = {}
if os.path.exists(os.path.join(DATA, "collectri_human.csv")):
    for r in csv.DictReader(open(os.path.join(DATA, "collectri_human.csv"))):
        _COLLECTRI.setdefault(r["tf"], 0)
        _COLLECTRI[r["tf"]] += 1

def _stim_max(n): return P._stim_max(n)

def t_search_regulators(exclude_canonical=True, exclude_housekeeping=True, min_stim_de=200, limit=25):
    """Candidate major regulators of the stimulated CD4 program, filterable."""
    out = []
    for g, n in _BB.items():
        if _stim_max(n) < min_stim_de:
            continue
        if not P.is_activation_module(n) and n["class"] not in ("constitutive_regulator", "condition_specific_regulator"):
            continue
        if exclude_canonical and g in P.CANON:
            continue
        if exclude_housekeeping and P.is_essentiality_artifact(n):
            continue
        out.append({"gene": g, "stim_max_de": _stim_max(n), "class": n["class"],
                    "is_known_TF": g in _COLLECTRI})
    out.sort(key=lambda x: -x["stim_max_de"])
    return {"candidates": out[:limit], "note": "sorted by strongest stimulated effect"}

def t_check_regulator(gene):
    n = _BB.get(gene)
    if not n:
        return {"gene": gene, "in_screen": False}
    conds = {c: {"n_de": v["n_de"], "kd": v.get("kd"), "rest_de": None} for c, v in n["conditions"].items()}
    return {"gene": gene, "in_screen": True, "class": n["class"],
            "rest_de": P._de(n, "Rest"), "stim_max_de": _stim_max(n),
            "is_canonical_Tcell_gene": gene in P.CANON,
            "is_activation_module": P.is_activation_module(n),
            "is_essentiality_artifact": P.is_essentiality_artifact(n),
            "conditions": conds}

def t_cross_cell_type(gene):
    k = _K562.get(gene); r = _RPE1.get(gene)
    def cls(v): return None if v is None else ("major" if v > 25 else "inert")
    return {"gene": gene, "k562_de": k, "k562": cls(k), "rpe1_de": r, "rpe1": cls(r),
            "verdict": ("housekeeping" if (k and k > 25) or (r and r > 25)
                        else "cell-type-specific" if (k is not None or r is not None) else "not_tested")}

def t_known_regulon(gene):
    known = _COLLECTRI.get(gene)
    return {"gene": gene, "is_known_TF_in_CollecTRI": known is not None,
            "n_known_targets": known or 0,
            "note": "absent = no annotated regulon; a novel regulatory role would be more surprising"}

TOOLS = [
    {"name": "search_regulators", "description": "Find candidate major regulators of the stimulated CD4+ T-cell program from the frozen atlas. Filter out canonical T-cell genes and housekeeping/essentiality genes to surface under-appreciated candidates.",
     "input_schema": {"type": "object", "properties": {
         "exclude_canonical": {"type": "boolean"}, "exclude_housekeeping": {"type": "boolean"},
         "min_stim_de": {"type": "integer"}, "limit": {"type": "integer"}}}},
    {"name": "check_regulator", "description": "Frozen verifier: a gene's per-condition DE profile, knockdown status, class, and whether it is a canonical T-cell gene / activation-module / essentiality-artifact.",
     "input_schema": {"type": "object", "properties": {"gene": {"type": "string"}}, "required": ["gene"]}},
    {"name": "cross_cell_type", "description": "Does the gene's knockdown reshape non-immune cells (Replogle K562, RPE1)? 'housekeeping' if it fires there too, 'cell-type-specific' if it stays inert.",
     "input_schema": {"type": "object", "properties": {"gene": {"type": "string"}}, "required": ["gene"]}},
    {"name": "known_regulon", "description": "Is the gene an annotated transcription factor in CollecTRI, and how large is its known regulon? Absence means a novel regulatory role.",
     "input_schema": {"type": "object", "properties": {"gene": {"type": "string"}}, "required": ["gene"]}},
]
DISPATCH = {"search_regulators": t_search_regulators, "check_regulator": t_check_regulator,
            "cross_cell_type": t_cross_cell_type, "known_regulon": t_known_regulon}

GOAL = """You are a research agent working on a VERIFIED frontier of CD4+ T-cell regulation, built
from the Marson genome-scale CRISPRi Perturb-seq screen. Every tool you call returns a deterministic
lookup against frozen released data. You may ONLY assert biology you have confirmed with a tool.

Goal: identify the single most compelling UNDER-APPRECIATED regulator of the CD4+ T-cell activation
program. The ideal candidate is: a strong regulator of the stimulated transcriptome; NOT a canonical
T-cell gene; cell-type-specific rather than housekeeping (inert in non-immune cells); and, ideally,
without a well-annotated regulon (so its role is genuinely novel).

Investigate with the tools: search for candidates, then vet each with check_regulator,
cross_cell_type, and known_regulon. Compare a few. When you are confident, stop calling tools and
give your final answer as a JSON object on its own line:
{"gene": "...", "hypothesis": "one or two sentences", "evidence": ["verified fact", ...], "why_novel": "..."}
Your hypothesis will be gated by the frozen verifier and signed by a human; do not overclaim."""

def run():
    import anthropic
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set (put it in ~/personal/prospect/.env)")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": GOAL}]
    transcript, tin, tout = [], 0, 0
    final_text = ""
    for rnd in range(MAX_ROUNDS):
        msg = client.messages.create(model=MODEL, max_tokens=8000, thinking={"type": "adaptive"},
                                     tools=TOOLS, messages=messages)
        tin += msg.usage.input_tokens; tout += msg.usage.output_tokens
        messages.append({"role": "assistant", "content": msg.content})
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        tool_uses = [b for b in msg.content if getattr(b, "type", "") == "tool_use"]
        for b in tool_uses:
            transcript.append({"round": rnd + 1, "reasoning": text, "tool": b.name, "input": dict(b.input)})
        if not tool_uses:
            final_text = text
            break
        results = []
        for b in tool_uses:
            out = DISPATCH[b.name](**b.input)
            transcript[-len(tool_uses) + tool_uses.index(b)]["result"] = out
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)[:4000]})
        messages.append({"role": "user", "content": results})
    # parse the final JSON hypothesis if present
    hyp = None
    for line in reversed(final_text.splitlines()):
        line = line.strip()
        if line.startswith("{") and '"gene"' in line:
            try: hyp = json.loads(line); break
            except Exception: pass
    pin, pout = price_for(MODEL)
    cost = tin / 1e6 * pin + tout / 1e6 * pout
    run = {"model": MODEL, "goal": "under-appreciated regulator of the CD4+ activation program",
           "rounds": max(t["round"] for t in transcript) if transcript else 0,
           "tool_calls": len(transcript), "cost_usd": round(cost, 4),
           "transcript": transcript, "final_text": final_text, "hypothesis": hyp,
           "delta_id": "hyp_" + hashlib.sha256((hyp["gene"] if hyp else final_text).encode()).hexdigest()[:16]}
    json.dump(run, open(RUN, "w"), indent=2)
    return run

def card(run):
    print(f"\nAgent ({run['model']}) · goal: {run['goal']}")
    print(f"  {run['tool_calls']} verified tool calls over {run['rounds']} rounds · ${run['cost_usd']}\n")
    for t in run["transcript"]:
        arg = ", ".join(f"{k}={v}" for k, v in t["input"].items())
        print(f"  round {t['round']}: {t['tool']}({arg})")
    h = run["hypothesis"]
    if h:
        print(f"\n  HYPOTHESIS · {h['gene']}: {h['hypothesis']}")
        for e in h.get("evidence", []):
            print(f"    - {e}")
        print(f"  why novel: {h.get('why_novel','')}")
    print(f"\n  pending {run['delta_id']} — awaiting a human signature.\n")

def sign():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    run = json.load(open(RUN)); h = run.get("hypothesis") or {}
    print(f"\nAccept the agent's verified hypothesis on {h.get('gene','?')}?")
    print(f"  {h.get('hypothesis','')}")
    if input("  type 'sign' to accept as this human's decision: ").strip() != "sign":
        sys.exit("not signed.")
    key = serialization.load_pem_private_key(open(KEY, "rb").read(), password=None)
    sig = key.sign(run["delta_id"].encode()).hex()
    pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    json.dump({"delta_id": run["delta_id"], "gene": h.get("gene"), "signature": sig, "pubkey": pub,
               "signer": os.environ.get("USER", "human")}, open(SIG, "w"), indent=2)
    print(f"  signed: {run['delta_id']} ({h.get('gene')}) accepted by {os.environ.get('USER','human')}\n")

def main(argv=None):
    ap = argparse.ArgumentParser(prog="prospect agent")
    ap.add_argument("--sign", action="store_true")
    a = ap.parse_args(argv)
    if a.sign:
        return sign()
    card(run())

if __name__ == "__main__":
    main()
