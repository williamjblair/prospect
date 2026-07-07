"""Mine the verified atlas for serendipity: verified findings a scientist would
never stumble on. Two flavors:
  - hidden gems: strong verified regulators that are NOT canonical T-cell genes
  - hype the data kills: famous immune/drug-target genes that are verified NON-regulators
All from the released ground-truth table; deterministic."""
import pandas as pd, json
de = pd.read_csv("examples/data/marson_de_full.csv")
bb = {n["gene"]: n for n in json.load(open("examples/data/atlas_backbone.json"))}

# canonical T-cell / immunotherapy vocabulary (famous genes a biologist expects to matter)
CANON = set("""CD3D CD3E CD3G CD247 ZAP70 LCK LAT ITK PLCG1 LCP2 VAV1 FYN
PDCD1 CTLA4 LAG3 HAVCR2 TIGIT BTLA CD28 ICOS CD40LG TNFRSF9
IL2 IL2RA IL2RB IL7R IL21 IL10 IFNG TNF TGFB1 FOXP3 GATA3 TBX21 RORC BCL6
CD4 CD8A CD8B CCR7 SELL PTPRC BCL10 CARD11 MALT1 NFKB1 NFKB2 RELA REL
STAT1 STAT3 STAT5A STAT5B JAK1 JAK3 NFATC1 NFATC2 RUNX1 RUNX3 IKZF1 IKZF2
TNFAIP3 CBLB PTPN2 PTPN22 SOCS1 SOCS3 CD5 CD6 DGKA DGKZ""".split())

def max_dn(g):
    return max((c["n_downstream"] for c in bb[g]["conditions"].values()), default=0)

# 1) HIDDEN GEMS: top verified regulators NOT in the canonical vocabulary
reg = [g for g,n in bb.items() if n["class"] in ("constitutive_regulator","condition_specific_regulator")]
gems = sorted((g for g in reg if g not in CANON and g.isalpha()==False or (g in reg and g not in CANON)),
              key=max_dn, reverse=True)
gems = [g for g in sorted(reg, key=max_dn, reverse=True) if g not in CANON][:15]
print("=== HIDDEN GEMS: top verified regulators that are NOT canonical T-cell genes ===")
for g in gems:
    print(f"  {g:10s} max_downstream={max_dn(g):5d}  class={bb[g]['class']}")

# 2) HYPE THE DATA KILLS: famous genes that are verified non-regulators (KD worked, no effect)
print("\n=== FAMOUS GENES the data demotes (verified non-regulator OR no knockdown) ===")
for g in sorted(CANON):
    if g in bb:
        cls = bb[g]["class"]
        if cls in ("verified_non_regulator","unverifiable_no_kd"):
            conds = {c: (v["status"], v["n_de"]) for c,v in bb[g]["conditions"].items()}
            print(f"  {g:10s} {cls:22s} {conds}")
