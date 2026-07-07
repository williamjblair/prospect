"""Deterministic checker for claims about the Replogle et al. 2022 genome-scale Perturb-seq
screen in K562 (a chronic myeloid leukemia line — NOT an immune cell). Cell 2022, PMID 35688146.

Same interface as the Marson checker (`__init__(data_path)` + `check(Claim) -> Verdict`), the
same five Verdict statuses, reading a frozen released table — this is the point of the transfer:
one verifier shape, a second independent dataset. Ground truth = Replogle's own per-perturbation
differentially-expressed-gene count (Mann-Whitney), never a recomputed DE test.

K562 has a single cell state (no Rest/Stim conditions), so the ladder is shorter: a "major
regulator" claim is supported if the knockdown moved > MAJOR_DE genes, refuted if it moved fewer,
unsupported if the gene was not in the screen (can't test here).
"""
from __future__ import annotations
import csv
from ..schema import Claim, Verdict

# K562 DE-gene count above which a knockdown is a "major" regulator here. The genome-wide K562
# median is 2 DE genes and p75 is 18, so >25 is an order of magnitude above the noise floor.
MAJOR_DE = 25

class ReploglePerturbseqChecker:
    dataset_id = "replogle2022_k562_gwps"

    def __init__(self, de_table_path: str, major_de: int = MAJOR_DE):
        self.major_de = major_de
        self._by = {}
        with open(de_table_path) as fh:
            for r in csv.DictReader(fh):
                if r.get("is_control", "").lower() == "true":
                    continue
                self._by[r["gene"]] = int(r["k562_de"])

    def de(self, gene: str):
        return self._by.get(gene)

    def check(self, claim: Claim) -> Verdict:
        if claim.strength in ("promising_target", "mechanism", "clinical"):
            return Verdict(claim, "asserted",
                           f"Interpretive claim ('{claim.strength}'). K562 Perturb-seq can show whether "
                           f"{claim.gene} reshapes the K562 transcriptome, not whether it is a target.")
        de = self.de(claim.gene)
        if de is None:
            return Verdict(claim, "unsupported",
                           f"{claim.gene} was not perturbed in the K562 genome-scale screen — "
                           f"can't test here (often because it isn't expressed in K562).",
                           mismatch_class="no_knockdown")
        ev = {"k562_de_genes": de, "major_threshold": self.major_de}
        if claim.asserts_major and de <= self.major_de:
            return Verdict(claim, "refuted",
                           f"{claim.gene} is not a major regulator in K562: knockdown moved {de} genes "
                           f"(≤{self.major_de}).", evidence=ev, mismatch_class="magnitude")
        if de <= 2:
            return Verdict(claim, "refuted",
                           f"{claim.gene} knockdown moved {de} genes in K562 — no transcriptional effect.",
                           evidence=ev, mismatch_class="magnitude")
        return Verdict(claim, "supported",
                       f"{claim.gene}: knockdown moved {de} genes in K562" +
                       (" — a major regulator here." if de > self.major_de else " — a real effect."),
                       evidence=ev)
