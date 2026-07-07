# Findings

Three findings, mined deterministically from the released Marson CD4+ CRISPRi Perturb-seq
DE-stats table (`examples/data/atlas_backbone.json`). Every threshold lives in
`frontier/predicates.py`, so a finding never drifts from the number that justifies it. Nothing
here is a live recompute; each claim re-derives from the frozen table, and each becomes a
content-addressed, human-signed object in the frontier.

The dataset has three culture conditions: `Rest`, `Stim8hr`, `Stim48hr`. For each perturbed
gene it reports, per condition, whether the knockdown was on-target and how many genes changed
(`n_de`).

---

## Finding 1 — the activation module, rebuilt from perturbation alone

**Claim.** The TCR-proximal signaling cascade is silent in a resting cell and becomes the
regulatory core of the transcriptome only after stimulation. The screen recovers this module
from knockout effects, with no prior pathway knowledge, and the frontier types every one of its
edges as condition-gated rather than constitutive.

**Definition** (`is_activation_module`): a gene with `Rest` DE < 10, a confirmed on-target
knockdown in a stimulated condition, and > 100 DE genes in that condition. 245 genes qualify.

**The exemplar — the TCR cascade, in textbook order:**

| gene | Rest DE | Stim (max) DE |
|------|--------:|--------------:|
| CD3E | 4 | 5,711 |
| LAT | 4 | 5,536 |
| PLCG1 | 3 | 5,033 |
| LCP2 | 2 | 4,982 |
| CD3D | 7 | 4,984 |
| CD3G | 5 | 4,966 |
| CD247 | 5 | 4,330 |
| BCL10 | 1 | 3,456 |
| ITK | 2 | 3,393 |
| CD28 | 5 | 1,798 |
| MALT1 | 3 | 1,640 |
| ORAI1 | 3 | 1,250 |

Knock any of these down in a resting cell and almost nothing moves. Knock the same gene down
after TCR engagement and thousands of genes shift. That is exactly what a signaling component
should do, and the screen reconstructs it without being told the pathway. This is the
validation finding: it earns trust for the two that follow.

---

## Finding 2 — regulator vs effector

**Claim.** The T-cell genes the field targets most (immune checkpoints and effector cytokines)
produce near-zero transcriptional change when knocked down, even under stimulation. They are
outputs of the T-cell program, not its transcriptional drivers. A frontier model asked whether
PD-1 is a key regulator of CD4 T-cell state says yes; the released data says no in this assay.
This is where AI overclaiming and the ground truth part ways.

**Definition** (`regulator_vs_effector`): a canonical immune gene (in the curated `CANON` set)
with a confirmed on-target knockdown in a stimulated condition, fewer than 3 DE genes there, and
never a major regulator in any condition (max DE < 50, which excludes the Finding-1 genes that
go quiet at Rest but drive thousands once stimulated). 18 genes qualify.

**The headline set** (each cited to the literature that calls it a central regulator/target;
source: PubMed):

| gene | role in the literature | max DE under stimulation | citation |
|------|------------------------|-------------------------:|----------|
| PDCD1 (PD-1) | primary inhibitory checkpoint | 2 | Pardoll, Nat Rev Cancer 2012 · [10.1038/nrc3239](https://doi.org/10.1038/nrc3239) |
| CTLA4 | negative regulator of activation | 3 | Alegre et al., Nat Rev Immunol 2001 · [10.1038/35105024](https://doi.org/10.1038/35105024) |
| HAVCR2 (TIM-3) | co-inhibitory checkpoint | 1 | Anderson et al., Immunity 2016 · [10.1016/j.immuni.2016.05.001](https://doi.org/10.1016/j.immuni.2016.05.001) |
| LAG3 | co-inhibitory checkpoint | 3 | Anderson et al., Immunity 2016 · [10.1016/j.immuni.2016.05.001](https://doi.org/10.1016/j.immuni.2016.05.001) |
| IL2 | cytokine directing effector/memory fate | 2 | Kalia & Sarkar, Front Immunol 2018 · [10.3389/fimmu.2018.02987](https://doi.org/10.3389/fimmu.2018.02987) |
| IFNG | defining Th1 effector cytokine | 1 | Zhu & Zhu, Int J Mol Sci 2020 · [10.3390/ijms21218011](https://doi.org/10.3390/ijms21218011) |

Each becomes a literature-vs-data `Contradiction` in the frontier, with the PMID as the
claimant on one side and the released DE count on the other. The frontier does not adjudicate;
it holds both and marks the gene contested. The point is not that the literature is wrong (PD-1
is a real drug target) but that "important therapeutic target" and "transcriptional regulator of
CD4 state in this assay" are different claims, and a model that conflates them overclaims.

*Citation note: gene roles above are drawn from PubMed.*

---

## Finding 3 — reach is not regulation

**Claim.** Rank genes by raw transcriptional reach and the top of the list is the cell's general
machinery, not its immune biology. Effect size alone cannot tell a T-cell regulator from an
essential housekeeping gene. The frontier's discriminator is reach at Rest.

**Why effect size fails.** CD3E, LAT, and PLCG1 (Finding 1) each move 5,000+ genes at Stim8hr,
the same magnitude as the SAGA and Mediator machinery. Magnitude does not separate them. Reach
at Rest does: a gene that reorganizes the transcriptome in an unstimulated cell is doing
housekeeping; one that only fires after TCR engagement is activation-specific. On the released
table the two classes sit on opposite sides of a wide empty gap.

**Definition** (`is_essentiality_artifact`): `Rest` DE > 1,000. 139 genes qualify.

| machinery gene | Rest DE | complex |
|----------------|--------:|---------|
| TADA2B | 4,681 | SAGA |
| SENP5 | 3,329 | SUMO protease |
| TAF6L | 3,368 | SAGA |
| SGF29 | 3,447 | SAGA |
| SUPT7L | 2,929 | SAGA |
| SUPT20H | 3,072 | SAGA |
| TADA1 | 2,944 | SAGA |
| MED12 | 2,843 | Mediator |
| MED19 | 2,012 | Mediator |

Machinery genes sit at Rest DE 2,012–4,681. The activation module (Finding 1) sits at Rest DE
1–7. Nothing lands in between. The frontier labels the high-Rest-reach genes
`essentiality_artifact` and keeps them out of the "hidden regulator" surface, so a naive
effect-size leaderboard cannot pass them off as immune findings.

**The cross-dataset test.** This definition is a hypothesis with a prediction: the high-Rest
genes are housekeeping, so they should move the transcriptome in a non-immune cell too, while
the activation module should not. Phase 3 (verifier transfer) tests it directly against the
Replogle genome-scale Perturb-seq in K562, an unrelated cell type. A regulator that fires in
both cells is housekeeping; one that fires only in stimulated CD4 T cells is immune-specific.
The second dataset turns this finding from a caveat into an independently validated result.

---

## How the three connect

The frontier recovers known activation biology (Finding 1), which earns the trust to catch the
field's most-hyped genes being mislabeled as regulators (Finding 2), while resisting the
essentiality artifact that a naive model surfaces instead (Finding 3). Recover, catch, resist:
a trust layer for machine-generated biology, grounded in real CD4 T-cell data and re-derivable
by anyone from the released table.
