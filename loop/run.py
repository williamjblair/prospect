"""The AI-claim overlay loop: measure how often confident AI biology survives the data.

Samples genes across the verified atlas, asks Claude (BLIND to the ground truth) to
judge each as a regulator with a one-line claim, then checks every claim against the
frozen released table. Emits per-claim verdicts + the phantom rate.

  # set ANTHROPIC_API_KEY in ~/personal/prospect/.env first
  python loop/run.py --n 200 --model claude-haiku-4-5-20251001
"""
from __future__ import annotations
import argparse, json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def sample_genes(backbone, n, seed=0):
    """Stratified sample so the test is balanced across real regulators, verified
    non-regulators, and untested genes (deterministic given seed)."""
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
    return json.loads(m.group(0)) if m else []

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(ROOT, "examples", "data", "claims.jsonl"))
    a = ap.parse_args(argv)
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Put it in ~/personal/prospect/.env")

    import anthropic
    from engine.schema import Claim
    from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
    client = anthropic.Anthropic()
    checker = MarsonPerturbseqChecker(os.path.join(ROOT, "examples", "data", "marson_de_full.csv"))
    backbone = json.load(open(os.path.join(ROOT, "examples", "data", "atlas_backbone.json")))
    truth = {n["gene"]: n["class"] for n in backbone}

    picks = sample_genes(backbone, a.n)
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["gene"] for l in open(a.out)}
    picks = [(g, c) for g, c in picks if g not in done]

    fh = open(a.out, "a")
    tally = {"ai_major": 0, "ai_major_phantom": 0, "graded": 0, "supported": 0, "unsupported": 0}
    for i in range(0, len(picks), a.batch):
        chunk = picks[i:i + a.batch]
        try:
            judgments = ask_claude(client, a.model, [g for g, _ in chunk])
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
                tally["ai_major"] += 1
                if v.status in ("unsupported", "refuted"):
                    tally["ai_major_phantom"] += 1
            if v.status in ("supported", "unsupported", "refuted"):
                tally["graded"] += 1
                tally["supported" if v.status == "supported" else "unsupported"] += 1
        print(f"  {min(i+a.batch,len(picks))}/{len(picks)} · "
              f"AI-major {tally['ai_major']} of which {tally['ai_major_phantom']} phantom")
    fh.close()
    rate = tally["ai_major_phantom"] / tally["ai_major"] if tally["ai_major"] else 0
    print(f"\nPHANTOM RATE: {tally['ai_major_phantom']}/{tally['ai_major']} = {rate:.0%} of confident "
          f"'major regulator' claims are not supported by the data")
    json.dump({**tally, "phantom_rate": rate},
              open(os.path.join(ROOT, "examples", "data", "phantom_summary.json"), "w"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
