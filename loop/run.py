"""The AI-claim overlay loop: measure how often confident AI biology survives the data,
and what it costs. Samples genes across the reproduced atlas, asks a model (BLIND to the
ground truth) to judge each as a regulator with a one-line claim, then checks every claim
against the frozen released table. Emits per-claim verdicts + phantom rate + token cost.

  # set ANTHROPIC_API_KEY in ~/personal/prospect/.env first
  python loop/run.py --n 300 --model claude-haiku-4-5
"""
from __future__ import annotations
import argparse, json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# $ per 1M tokens (input, output) - from the claude-api skill pricing table.
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
    payload = dict(model=model, max_tokens=4000,
                   messages=[{"role": "user", "content": PROMPT % ", ".join(genes)}])
    # Fable's safety classifiers can false-positive on life-sciences prompts; opt into the
    # server-side refusal fallback to Opus so a decline is transparently re-served in-call.
    if "fable" in model:
        try:
            msg = client.beta.messages.create(
                betas=["server-side-fallback-2026-06-01"],
                fallbacks=[{"model": "claude-opus-4-8"}], **payload)
        except TypeError:
            msg = client.messages.create(**payload)   # SDK without the fallback param
    else:
        msg = client.messages.create(**payload)
    if getattr(msg, "stop_reason", "") == "refusal":
        return [], msg.usage.input_tokens, msg.usage.output_tokens   # discard a refused batch
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\[.*\]", text, re.S)
    judgments = json.loads(m.group(0)) if m else []
    return judgments, msg.usage.input_tokens, msg.usage.output_tokens

def load_corpus(path):
    """Return [(gene, class, buckets)] from a frozen benchmark_corpus.json (core + effector_focus)."""
    c = json.load(open(path))
    m = {}  # gene -> [class, set(buckets)]
    for bucket in ("core", "effector_focus"):
        for row in c.get(bucket, []):
            e = m.setdefault(row["gene"], [row["class"], set()])
            e[1].add("core" if bucket == "core" else "effector")
    return [(g, cls, sorted(bk)) for g, (cls, bk) in m.items()]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--out", default=None)
    ap.add_argument("--corpus", default=None, help="frozen benchmark_corpus.json - grade exactly these genes")
    ap.add_argument("--tag", default=None, help="output tag override (default derived from model); use to avoid clobbering a historical run")
    a = ap.parse_args(argv)
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Put it in ~/personal/prospect/.env")
    tag = a.tag or tag_for(a.model)
    prefix = "bench" if a.corpus else "claims"
    out = a.out or os.path.join(ROOT, "examples", "data", f"{prefix}_{tag}.jsonl")

    import anthropic
    from engine.schema import Claim
    from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
    client = anthropic.Anthropic()
    checker = MarsonPerturbseqChecker(os.path.join(ROOT, "examples", "data", "marson_de_full.csv"))
    backbone = json.load(open(os.path.join(ROOT, "examples", "data", "atlas_backbone.json")))

    if a.corpus:
        picks = load_corpus(a.corpus)          # [(gene, class, buckets)]
    else:
        picks = [(g, c, ["core"]) for g, c in sample_genes(backbone, a.n)]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["gene"] for l in open(out)}
    picks = [p for p in picks if p[0] not in done]

    fh = open(out, "a")
    tin = tout = 0
    ai_major = phantom = 0
    for i in range(0, len(picks), a.batch):
        chunk = picks[i:i + a.batch]
        try:
            judgments, ti, to = ask_claude(client, a.model, [g for g, _, _ in chunk])
            tin += ti; tout += to
        except Exception as e:
            print("batch error:", str(e)[:120]); continue
        jmap = {j.get("gene"): j for j in judgments if isinstance(j, dict)}
        for g, cls, buckets in chunk:
            j = jmap.get(g)
            if not j: continue
            claim = Claim(text=j.get("claim", f"{g} is a major regulator"), gene=g,
                          condition="Stim48hr", asserts_major=bool(j.get("major_regulator")))
            v = checker.check(claim)
            rec = {"gene": g, "truth_class": cls, "buckets": buckets,
                   "ai_major": bool(j.get("major_regulator")),
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
    stats = {"model": a.model, "tag": tag, "n": len(picks),
             "input_tokens": tin, "output_tokens": tout, "cost_usd": round(cost, 4),
             "ai_major_claims": ai_major, "refuted": phantom}
    json.dump(stats, open(os.path.join(ROOT, "examples", "data", f"{prefix}_stats_{tag}.json"), "w"), indent=2)
    print(f"\n{a.model}: {tin+tout:,} tokens, ${cost:.4f} · AI-major {ai_major}, refuted {phantom}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
