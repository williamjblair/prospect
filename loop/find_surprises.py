"""Mine the verified atlas for serendipity: verified findings a scientist would never
stumble on. Deterministic, from the released ground-truth table.
  - hidden_regulators: strong verified regulators that are NOT canonical T-cell genes
  - demoted_famous:    famous immune/target genes that are verified non-regulators
                       (knockdown confirmed, ~no transcriptional effect in this assay)
  - untested_famous:   famous genes the screen could NOT test (no knockdown) — kept DISTINCT.
"""
import json, os

CANON = set("""CD3D CD3E CD3G CD247 ZAP70 LCK LAT ITK PLCG1 LCP2 VAV1 FYN
PDCD1 CTLA4 LAG3 HAVCR2 TIGIT BTLA CD28 ICOS CD40LG TNFRSF9
IL2 IL2RA IL2RB IL7R IL21 IL10 IFNG TNF TGFB1 FOXP3 GATA3 TBX21 RORC BCL6
CD4 CD8A CD8B CCR7 SELL PTPRC BCL10 CARD11 MALT1 NFKB1 NFKB2 RELA REL
STAT1 STAT3 STAT5A STAT5B JAK1 JAK3 NFATC1 NFATC2 RUNX1 RUNX3 IKZF1 IKZF2
TNFAIP3 CBLB PTPN2 PTPN22 SOCS1 SOCS3 CD5 CD6 DGKA DGKZ""".split())

_HERE = os.path.dirname(os.path.abspath(__file__))
_BB = os.path.join(_HERE, "..", "examples", "data", "atlas_backbone.json")

def _max_dn(node):
    return max((c["n_downstream"] for c in node["conditions"].values()), default=0)

def mine(backbone_path=_BB):
    bb = {n["gene"]: n for n in json.load(open(backbone_path))}
    reg = [g for g, n in bb.items()
           if n["class"] in ("constitutive_regulator", "condition_specific_regulator")]

    hidden = []
    for g in sorted(reg, key=lambda g: _max_dn(bb[g]), reverse=True):
        if g in CANON:
            continue
        hidden.append({"gene": g, "class": bb[g]["class"],
                       "max_downstream": _max_dn(bb[g]), "conditions": bb[g]["conditions"]})
        if len(hidden) >= 20:
            break

    demoted, untested = [], []
    for g in sorted(CANON):
        n = bb.get(g)
        if not n:
            continue
        if n["class"] == "verified_non_regulator":
            demoted.append({"gene": g, "conditions": n["conditions"]})
        elif n["class"] == "unverifiable_no_kd":
            untested.append({"gene": g, "conditions": n["conditions"]})

    return {"hidden_regulators": hidden, "demoted_famous": demoted, "untested_famous": untested}

if __name__ == "__main__":
    s = mine()
    print("=== HIDDEN REGULATORS (top verified regulators, not canonical T-cell genes) ===")
    for h in s["hidden_regulators"][:15]:
        print(f"  {h['gene']:10s} max_downstream={h['max_downstream']:5d}  {h['class']}")
    print("\n=== FAMOUS GENES the data demotes (verified non-regulator in this assay) ===")
    for d in s["demoted_famous"]:
        conds = ", ".join(f"{k}:{v['n_de']}DE" for k, v in d["conditions"].items())
        print(f"  {d['gene']:10s} {conds}")
    print("\n=== FAMOUS GENES the screen could NOT test (no knockdown) ===")
    print("  " + ", ".join(d["gene"] for d in s["untested_famous"]))
