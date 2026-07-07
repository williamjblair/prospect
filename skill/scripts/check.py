#!/usr/bin/env python3
"""Self-contained Prospect claim checker for the Marson CD4+ T-cell CRISPRi screen.
No third-party deps — reads the bundled frozen released DE slice and checks typed claims
deterministically. Frozen code + frozen table = no model in the trust path.

  python scripts/check.py claims.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SLICE = os.path.join(HERE, "..", "references", "marson_de_slice.csv")
CONDS = ["Rest", "Stim8hr", "Stim48hr"]

def load_table(path):
    by = {}
    for r in csv.DictReader(open(path)):
        by[(r["target_contrast_gene_name"], r["culture_condition"])] = r
    return by

def check(claim, by):
    gene = claim["gene"]; cond = claim.get("condition")
    strength = claim.get("strength", "quantitative")
    if strength in ("promising_target", "mechanism", "clinical"):
        return ("asserted", f"Interpretive ({strength}). This screen shows whether {gene} "
                f"reshapes the transcriptome, not whether it is a target/mechanism. Not gradeable here.")
    conds = [cond] if cond else CONDS
    rows = {c: by.get((gene, c)) for c in conds if by.get((gene, c))}
    if not rows:
        return ("unsupported", f"{gene} not found in the screen for the stated condition(s).")
    def kd(r):   return r["ontarget_effect_category"] == "on-target KD"
    def nde(r):  return int(float(r["n_total_de_genes"]))
    def major(r):return r["n_total_genes_category"] == ">10 DE genes"
    if not any(kd(r) for r in rows.values()):
        return ("unsupported", f"No on-target knockdown of {gene} in {', '.join(rows)}. "
                f"The perturbation did not work, so any regulatory claim is unsupported.")
    real = [c for c, r in rows.items() if kd(r) and nde(r) > 2]
    if claim.get("asserts_major") and not any(major(r) for r in rows.values()):
        counts = ", ".join(f"{c}={nde(rows[c])} DE genes" for c in rows)
        return ("refuted", f"{gene} is not a major regulator: no condition shows >10 DE genes ({counts}).")
    if cond is None:
        silent = [c for c in rows if c not in real]
        if real and silent:
            return ("needs_qualification", f"{gene}'s effect is condition-specific: active in {real}, "
                    f"~silent in {silent}. State the condition.")
    return ("supported", f"{gene}: on-target knockdown confirmed and a real effect in {real}. "
            + ("Major regulator (>10 DE genes)." if claim.get("asserts_major") else "Effect reproduced."))

_MARK = {"supported": "✅", "refuted": "❌", "unsupported": "❌",
         "needs_qualification": "⚠️", "asserted": "○"}

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/check.py claims.json")
    by = load_table(SLICE)
    claims = json.load(open(sys.argv[1]))
    ok = flag = 0
    print("\nProspect — claims checked against the released Marson DE table (no model in the trust path)\n")
    for c in claims:
        status, reason = check(c, by)
        print(f"{_MARK[status]}  {status.upper():20s} {c.get('text', c['gene'])}")
        print(f"    └ {reason}")
        ok += status == "supported"; flag += status in ("refuted", "unsupported")
    print(f"\n{ok}/{len(claims)} supported · {flag} should not be reported as-is")
    print('"supported" means the data reproduces the claim — never that the biology is true.\n')

if __name__ == "__main__":
    main()
