"""The AI-claim overlay loop: measure how often confident AI biology survives the data,
and what it costs. Samples genes across the verified atlas, asks a model (BLIND to the
ground truth) to judge each as a regulator with a one-line claim, then checks every claim
against the frozen released table. Emits per-claim verdicts + phantom rate + token cost.

  # set ANTHROPIC_API_KEY in ~/personal/prospect/.env first
  python loop/run.py --n 300 --model claude-haiku-4-5
"""
from __future__ import annotations
import argparse, json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# $ per 1M tokens (input, output) — from the claude-api skill pricing table.
PRICING = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-opus-4-8":  (5.00, 25.00),
    "claude-sonnet-5":  (2.00, 10.00),   # intro pricing through 2026-08-31
    "claude-fable-5":   (10.00, 50.00),
}
def price_for(model):
    for k, v in PRICING.items():
        if model.startswith(k):
            return v
    return (0.0, 0.0)
def tag_for(model):
    for k in ("haiku", "opus", "sonnet", "fable"):
        if k in model:
            return k
    return "model"

def load_env():
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def sample_genes(backbone, n, seed=0):
    rng = random.Random(seed)
    buckets = {}
    for node in backbone:
        buckets.setdefault(node["class"], []).append(node["gene"])
    picks, per = [], max(1, n // max(1, len(buckets)))
    for cls, genes in buckets.items():
        rng.shuffle(genes)
        picks += [(g, cls) for g in genes[:per]]
    rng.shuffle(picks)
    return picks[:n]

PROMPT = """You are an AI research assistant helping a T-cell immunologist interpret a CRISPR screen.
For each gene below, using your biological knowledge, judge whether knocking it down would make it a
MAJOR regulator of the CD4+ T-cell transcriptome under stimulation (i.e. perturbing it substantially
reshapes gene expression). Answer for every gene.

Return ONLY a JSON array, one object per gene:
{"gene": "SYMBOL", "major_regulator": true/false, "confidence": 0.0-1.0, "claim": "one sentence"}

Genes: %s"""

def ask_claude(client, model, genes):
    import re
    msg = client.messages.create(
        model=model, max_tokens=4000,
        messages=[{"role": "user", "content": PROMPT % ", ".join(genes)}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\[.*\]", text, re.S)
    judgments = json.loads(m.group(0)) if m else []
    return judgments, msg.usage.input_tokens, msg.usage.output_tokens

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Put it in ~/personal/prospect/.env")
    tag = tag_for(a.model)
    out = a.out or os.path.join(ROOT, "examples", "data", f"claims_{tag}.jsonl")

    import anthropic
    from engine.schema import Claim
    from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
    client = anthropic.Anthropic()
    checker = MarsonPerturbseqChecker(os.path.join(ROOT, "examples", "data", "marson_de_full.csv"))
    backbone = json.load(open(os.path.join(ROOT, "examples", "data", "atlas_backbone.json")))

    picks = sample_genes(backbone, a.n)
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["gene"] for l in open(out)}
    picks = [(g, c) for g, c in picks if g not in done]

    fh = open(out, "a")
    tin = tout = 0
    ai_major = phantom = 0
    for i in range(0, len(picks), a.batch):
        chunk = picks[i:i + a.batch]
        try:
            judgments, ti, to = ask_claude(client, a.model, [g for g, _ in chunk])
            tin += ti; tout += to
        except Exception as e:
            print("batch error:", str(e)[:120]); continue
        jmap = {j.get("gene"): j for j in judgments if isinstance(j, dict)}
        for g, cls in chunk:
            j = jmap.get(g)
            if not j: continue
            claim = Claim(text=j.get("claim", f"{g} is a major regulator"), gene=g,
                          condition="Stim48hr", asserts_major=bool(j.get("major_regulator")))
            v = checker.check(claim)
            rec = {"gene": g, "truth_class": cls, "ai_major": bool(j.get("major_regulator")),
                   "ai_confidence": j.get("confidence"), "ai_claim": j.get("claim"),
                   "verdict": v.status, "reason": v.reason}
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            if rec["ai_major"]:
                ai_major += 1
                if v.status == "refuted": phantom += 1
        print(f"  {min(i+a.batch,len(picks))}/{len(picks)} · AI-major {ai_major} · refuted {phantom}")
    fh.close()

    pin, pout = price_for(a.model)
    cost = tin/1e6*pin + tout/1e6*pout
    stats = {"model": a.model, "tag": tag, "n": a.n,
             "input_tokens": tin, "output_tokens": tout, "cost_usd": round(cost, 4),
             "ai_major_claims": ai_major, "refuted": phantom}
    json.dump(stats, open(os.path.join(ROOT, "examples", "data", f"run_stats_{tag}.json"), "w"), indent=2)
    print(f"\n{a.model}: {tin+tout:,} tokens, ${cost:.4f} · AI-major {ai_major}, refuted {phantom}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
