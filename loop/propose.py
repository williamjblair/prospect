"""The loop, closed: Claude PROPOSES candidate regulators, the frozen verifier DECIDES, a human
SIGNS the accepted set. No model is in the trust path - Claude's proposals are untrusted until the
frozen released table admits them and a human key accepts them.

  # propose + verify (writes examples/data/proposal_run.json, prints the card)
  python loop/propose.py --n 15 --model claude-opus-4-8

  # then a human accepts the frozen-verified delta (Ed25519, one confirm)
  python loop/propose.py --sign

This is the "Built with Claude" capstone: generation is cheap and Claude is genuinely useful at
proposing, but the admission decision is a deterministic re-derivation plus a human signature.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loop.run import load_env, price_for   # reuse env-loading + pricing

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
RUN = os.path.join(DATA, "proposal_run.json")
SIG = os.path.join(DATA, "proposal_run.sig.json")
KEY = os.path.join(ROOT, "frontier", ".prospect_signing_key")

PROMPT = """You are proposing new biology for a CD4+ T-cell CRISPRi Perturb-seq atlas.
Propose %d genes you believe are MAJOR regulators of the CD4+ T-cell transcriptome under
stimulation - genes whose knockdown substantially reshapes gene expression. Favor genes a
biologist would find interesting, not only textbook TCR components.

Return ONLY a JSON array, one object per gene:
{"gene": "SYMBOL", "rationale": "one sentence why you propose it as a major regulator"}"""

def propose(n, model):
    import re, anthropic
    from engine.schema import Claim
    from engine.registry import get_checker
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set (put it in ~/personal/prospect/.env)")
    client = anthropic.Anthropic()
    checker = get_checker("marson", os.path.join(DATA, "marson_de_full.csv"))

    msg = client.messages.create(model=model, max_tokens=8000,
                                 thinking={"type": "adaptive"},
                                 messages=[{"role": "user", "content": PROMPT % n}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    proposals = json.loads(re.search(r"\[.*\]", text, re.S).group(0))

    results = []
    for p in proposals:
        g = p.get("gene", "").strip()
        if not g:
            continue
        claim = Claim(text=p.get("rationale", f"{g} is a major regulator"), gene=g,
                      condition=None, asserts_major=True)
        v = checker.check(claim)
        results.append({"gene": g, "rationale": p.get("rationale", ""),
                        "verdict": v.status, "reason": v.reason,
                        "admitted": v.status == "supported"})
    pin, pout = price_for(model)
    cost = msg.usage.input_tokens / 1e6 * pin + msg.usage.output_tokens / 1e6 * pout
    admitted = [r for r in results if r["admitted"]]
    run = {"model": model, "proposed": len(results), "admitted": len(admitted),
           "rejected": len(results) - len(admitted), "cost_usd": round(cost, 4),
           "proposals": results,
           "delta_id": "delta_" + hashlib.sha256(
               json.dumps(sorted(r["gene"] for r in admitted)).encode()).hexdigest()[:16]}
    json.dump(run, open(RUN, "w"), indent=2)
    return run

def card(run):
    mark = {"supported": "ADMIT ", "refuted": "REJECT", "unsupported": "REJECT",
            "needs_qualification": "QUALIFY", "asserted": "-     "}
    print(f"\nClaude ({run['model']}) proposed {run['proposed']} regulators; the frozen verifier decided.\n")
    for r in run["proposals"]:
        print(f"  {mark.get(r['verdict'], r['verdict']):8s} {r['gene']:10s} {r['rationale'][:66]}")
    print(f"\n  {run['admitted']} admitted · {run['rejected']} rejected by the data · ${run['cost_usd']}")
    print(f"  pending delta {run['delta_id']} - awaiting a human signature (nothing auto-accepts).\n")

def sign():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    if not os.path.exists(RUN):
        sys.exit("no proposal_run.json - run `python loop/propose.py` first")
    run = json.load(open(RUN))
    admitted = [r["gene"] for r in run["proposals"] if r["admitted"]]
    print(f"\nAccept {len(admitted)} frozen-verified proposals into pending state?")
    print(f"  delta {run['delta_id']}: {', '.join(admitted)}")
    if input("  type 'sign' to accept as this human's decision: ").strip() != "sign":
        sys.exit("not signed.")
    key = serialization.load_pem_private_key(open(KEY, "rb").read(), password=None) \
        if os.path.exists(KEY) else Ed25519PrivateKey.generate()
    if not os.path.exists(KEY):
        open(os.open(KEY, os.O_WRONLY | os.O_CREAT, 0o600), "wb").write(
            key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                              serialization.NoEncryption()))
    sig = key.sign(run["delta_id"].encode()).hex()
    pub = key.public_key().public_bytes(serialization.Encoding.Raw,
                                        serialization.PublicFormat.Raw).hex()
    json.dump({"delta_id": run["delta_id"], "admitted": admitted, "signature": sig,
               "pubkey": pub, "signer": os.environ.get("USER", "human")},
              open(SIG, "w"), indent=2)
    print(f"  signed: {run['delta_id']} accepted by {os.environ.get('USER','human')} "
          f"- Claude proposed, the data decided, a human signed.\n")

def main(argv=None):
    ap = argparse.ArgumentParser(prog="prospect propose")
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--sign", action="store_true", help="human-accept the last verified delta")
    a = ap.parse_args(argv)
    if a.sign:
        return sign()
    card(propose(a.n, a.model))

if __name__ == "__main__":
    main()
