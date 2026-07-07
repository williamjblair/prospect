"""Deterministic checker for claims about the Marson genome-scale CRISPRi
Perturb-seq screen in primary human CD4+ T cells (Zhu, Dann, ... Marson 2025).

Ground truth = the released per-perturbation DE_stats table (frozen artifact).
We never re-run a DE test; we look up the released numbers and compare. This is
bit-for-bit deterministic and puts no model in the trust path.

Table columns used:
  target_contrast_gene_name, culture_condition (Rest/Stim8hr/Stim48hr),
  n_total_de_genes, n_total_genes_category (no effect | 1 DE gene | 2-10 DE genes | >10 DE genes),
  ontarget_effect_category (no on-target KD | on-target KD | putative off-target),
  ontarget_effect_size, ontarget_significant, n_downstream
"""
from __future__ import annotations
import pandas as pd
from ..schema import Claim, Verdict

CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]

class MarsonPerturbseqChecker:
    dataset_id = "marson2025_cd4_perturbseq"

    def __init__(self, de_table_path: str):
        df = pd.read_csv(de_table_path)
        self.df = df
        self._by = {(r.target_contrast_gene_name, r.culture_condition): r
                    for r in df.itertuples(index=False)}

    def _row(self, gene: str, condition: str):
        return self._by.get((gene, condition))

    def check(self, claim: Claim) -> Verdict:
        # Interpretive claims are never graded from this data.
        if claim.strength in ("promising_target", "mechanism", "clinical"):
            return Verdict(claim, "asserted",
                           f"Interpretive claim ('{claim.strength}'). This dataset can show "
                           f"whether {claim.gene} changes the transcriptome, not whether it is a "
                           f"therapeutic target. Not gradeable here; requires external evidence.")

        # Which conditions to consider.
        conds = [claim.condition] if claim.condition else CONDITIONS
        rows = {c: self._row(claim.gene, c) for c in conds if self._row(claim.gene, c) is not None}
        if not rows:
            return Verdict(claim, "unsupported",
                           f"{claim.gene} not found in the screen for the stated condition(s).",
                           mismatch_class="fabricated")

        def ev(r):
            return {"condition": r.culture_condition,
                    "ontarget_effect_category": r.ontarget_effect_category,
                    "n_total_de_genes": int(r.n_total_de_genes),
                    "n_total_genes_category": r.n_total_genes_category,
                    "ontarget_effect_size": float(r.ontarget_effect_size),
                    "n_downstream": int(r.n_downstream)}

        # 1) Did the perturbation actually knock the target down?
        kd_ok = {c: (r.ontarget_effect_category == "on-target KD") for c, r in rows.items()}
        # 2) Did it produce an effect (any DE genes)?
        has_effect = {c: (r.n_total_genes_category != "no effect") for c, r in rows.items()}
        # 3) Is it a "major" regulator (>10 DE genes)?
        is_major = {c: (r.n_total_genes_category == ">10 DE genes") for c, r in rows.items()}

        # No knockdown anywhere the claim covers -> the perturbation didn't work; claim has no basis.
        if not any(kd_ok.values()):
            worst = list(rows.values())[0]
            return Verdict(claim, "unsupported",
                           f"No on-target knockdown of {claim.gene} in {', '.join(rows)}. "
                           f"The perturbation did not work, so any claim of a regulatory effect is unsupported.",
                           evidence={c: ev(r) for c, r in rows.items()},
                           mismatch_class="no_knockdown")

        # Knockdown worked somewhere. Where does a SUBSTANTIVE effect actually hold?
        def real_effect(c):
            return kd_ok[c] and int(rows[c].n_total_de_genes) > 2
        active = [c for c in rows if real_effect(c)]

        # "major regulator" asserted but nowhere >10 DE genes -> refuted.
        if claim.asserts_major and not any(is_major.values()):
            counts = ", ".join(f"{c}={int(rows[c].n_total_de_genes)} DE genes" for c in rows)
            return Verdict(claim, "refuted",
                           f"{claim.gene} is not a major regulator: no condition shows >10 DE genes ({counts}).",
                           evidence={c: ev(r) for c, r in rows.items()},
                           mismatch_class="magnitude")

        # Unqualified claim (no condition) that only holds under stimulation -> needs qualification.
        if claim.condition is None:
            silent = [c for c in rows if not real_effect(c)]
            if active and silent:
                return Verdict(claim, "needs_qualification",
                               f"{claim.gene}'s effect is condition-specific: active in {active}, "
                               f"~silent in {silent}. State the condition.",
                               evidence={c: ev(r) for c, r in rows.items()},
                               mismatch_class="condition")

        # Otherwise supported: knockdown confirmed and a real (major, if claimed) effect.
        return Verdict(claim, "supported",
                       f"{claim.gene}: on-target knockdown confirmed and a real transcriptional "
                       f"effect in {active}. " +
                       ("Major regulator (>10 DE genes)." if claim.asserts_major else "Effect reproduced."),
                       evidence={c: ev(r) for c, r in rows.items()})
