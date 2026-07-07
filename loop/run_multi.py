"""Multi-claim-type overlay: ask a model for richer typed claims per gene (magnitude AND
direction), check each dimension against the frozen table, and report the phantom rate
BY CLAIM TYPE. Shows where AI overstates most.

  python loop/run_multi.py --n 400 --model claude-haiku-4-5
"""
from __future__ import annotations
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loop.run import load_env, sample_genes, price_for, tag_for, ROOT

PROMPT = """You are an AI research assistant interpreting a genome-scale CRISPRi Perturb-seq
screen in stimulated CD4+ T cells. For each gene, using your biological knowledge, judge:
1. major_regulator: would knocking it down broadly reshape the transcriptome (>10 genes change)?
2. direction: IF it has an effect, does knockdown mostly UP-regulate or DOWN-regulate other genes?

Return ONLY a JSON array, one object per gene:
{"gene":"SYM","major_regulator":true/false,"direction":"up"|"down"|"none","confidence":0.0-1.0}

Genes: %s"""

def ask(client, model, genes):
    msg = client.messages.create(model=model, max_tokens=4000,
        messages=[{"role": "user", "content": PROMPT % ", ".join(genes)}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\[.*\]", text, re.S)
    return (json.loads(m.group(0)) if m else []), msg.usage.input_tokens, msg.usage.output_tokens

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--batch", type=int, default=20)
    a = ap.parse_args(argv)
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")
    import anthropic
    from engine.schema import Claim
    from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
    client = anthropic.Anthropic()
    ck = MarsonPerturbseqChecker(os.path.join(ROOT, "examples", "data", "marson_de_full.csv"))
    bb = json.load(open(os.path.join(ROOT, "examples", "data", "atlas_backbone.json")))
    picks = [g for g, _ in sample_genes(bb, a.n)]

    types = {t: {"claimed": 0, "supported": 0, "refuted": 0} for t in ("magnitude", "direction")}
    tin = tout = 0
    for i in range(0, len(picks), a.batch):
        chunk = picks[i:i + a.batch]
        try:
            js, ti, to = ask(client, a.model, chunk); tin += ti; tout += to
        except Exception as e:
            print("batch error:", str(e)[:100]); continue
        jm = {j.get("gene"): j for j in js if isinstance(j, dict)}
        for g in chunk:
            j = jm.get(g)
            if not j: continue
            if j.get("major_regulator"):
                v = ck.check(Claim(f"{g} major", g, "Stim48hr", asserts_major=True))
                types["magnitude"]["claimed"] += 1
                if v.status == "supported": types["magnitude"]["supported"] += 1
                elif v.status == "refuted": types["magnitude"]["refuted"] += 1
            d = j.get("direction")
            if d in ("up", "down"):
                s, _ = ck.check_direction(g, "Stim48hr", d)
                types["direction"]["claimed"] += 1
                if s == "supported": types["direction"]["supported"] += 1
                elif s == "refuted": types["direction"]["refuted"] += 1
        print(f"  {min(i+a.batch,len(picks))}/{len(picks)} · "
              f"mag {types['magnitude']['refuted']}/{types['magnitude']['claimed']} refuted · "
              f"dir {types['direction']['refuted']}/{types['direction']['claimed']} refuted")

    pin, pout = price_for(a.model)
    out = {"model": a.model, "cost_usd": round(tin/1e6*pin + tout/1e6*pout, 4), "by_type": {}}
    for t, d in types.items():
        chk = d["supported"] + d["refuted"]
        d["phantom_rate"] = round(d["refuted"] / chk, 3) if chk else None
        out["by_type"][t] = d
    json.dump(out, open(os.path.join(ROOT, "examples", "data", f"claim_types_{tag_for(a.model)}.json"), "w"), indent=2)
    print("\nPHANTOM RATE BY CLAIM TYPE:")
    for t, d in out["by_type"].items():
        r = f"{d['phantom_rate']:.0%}" if d["phantom_rate"] is not None else "n/a"
        print(f"  {t:10s} {d['refuted']}/{d['supported']+d['refuted']} contradicted = {r}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
