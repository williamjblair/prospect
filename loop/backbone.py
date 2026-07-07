"""Atlas backbone: classify every (gene, condition) in the released Marson DE table
into verified regulatory state — deterministically, no model. This is the ground-truth
layer of the frontier the AI-claim loop then overlays on."""
import pandas as pd, json, sys, os

def node_status(r):
    if r.ontarget_effect_category == "putative off-target": return "off_target"
    if r.ontarget_effect_category == "no on-target KD":      return "no_knockdown"      # perturbation failed
    # knockdown worked -> the gene's real effect is observable:
    cat = r.n_total_genes_category
    if cat == ">10 DE genes":   return "regulator_major"
    if cat == "2-10 DE genes":  return "regulator_minor"
    if cat == "1 DE gene":      return "regulator_weak"
    return "no_effect"                                                                  # verified NON-regulator

def build(de_path, out_path):
    df = pd.read_csv(de_path)
    genes = {}
    for r in df.itertuples(index=False):
        g = r.target_contrast_gene_name
        genes.setdefault(g, {"gene": g, "conditions": {}})
        genes[g]["conditions"][r.culture_condition] = {
            "status": node_status(r), "n_de": int(r.n_total_de_genes),
            "n_downstream": int(r.n_downstream), "effect_size": float(r.ontarget_effect_size),
            "kd": r.ontarget_effect_category}
    # per-gene aggregate: constitutive vs condition-specific vs non-regulator vs unverifiable
    REG = {"regulator_major","regulator_minor","regulator_weak"}
    for g, node in genes.items():
        active = [c for c,v in node["conditions"].items() if v["status"] in REG and v["n_de"]>2]
        kd_any = any(v["status"] not in ("no_knockdown","off_target") for v in node["conditions"].values())
        if not kd_any:                      node["class"]="unverifiable_no_kd"
        elif not active:                    node["class"]="verified_non_regulator"
        elif len(active)==len(node["conditions"]): node["class"]="constitutive_regulator"
        else:                               node["class"]="condition_specific_regulator"
        node["active_conditions"]=active
    json.dump(list(genes.values()), open(out_path,"w"))
    from collections import Counter
    dist = Counter(n["class"] for n in genes.values())
    print(f"atlas backbone: {len(genes)} genes, {len(df)} perturbation-condition nodes")
    for k,v in dist.most_common(): print(f"  {k:30s} {v}")
    # a few real regulators for sanity
    reg = sorted((n for n in genes.values() if n["class"]=="condition_specific_regulator"),
                 key=lambda n: -max(c["n_downstream"] for c in n["conditions"].values()))[:5]
    print("  e.g. condition-specific:", [n["gene"] for n in reg])
    return genes

if __name__=="__main__":
    build("examples/data/marson_de_full.csv", "examples/data/atlas_backbone.json")
