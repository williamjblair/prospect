# Findings

Five findings, mined deterministically from the released Marson CD4+ CRISPRi Perturb-seq
DE-stats table (`examples/data/atlas_backbone.json`). Every threshold lives in
`frontier/predicates.py`, so a finding never drifts from the number that justifies it. Nothing
here is a live recompute; each claim re-derives from the frozen table, and each becomes a
content-addressed, human-signed object in the frontier.

The dataset has three culture conditions: `Rest`, `Stim8hr`, `Stim48hr`. For each perturbed
gene it reports, per condition, whether the knockdown was on-target and how many genes changed
(`n_de`).

---

## Finding 1 - the activation module, rebuilt from perturbation alone

**Claim.** The TCR-proximal signaling cascade is silent in a resting cell and becomes the
regulatory core of the transcriptome only after stimulation. The screen recovers this module
from knockout effects, with no prior pathway knowledge, and the frontier types every one of its
edges as condition-gated rather than constitutive.

**Definition** (`is_activation_module`): a gene with `Rest` DE < 10, a confirmed on-target
knockdown in a stimulated condition, and > 100 DE genes in that condition. 245 genes qualify.

**The exemplar - the TCR cascade, in textbook order:**

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

## Finding 2 - regulator vs effector

**Claim.** The T-cell genes the field targets most (immune checkpoints and effector cytokines)
produce near-zero transcriptional change when knocked down, even under stimulation. They are
outputs of the T-cell program, not its transcriptional drivers. A frontier model asked whether
PD-1 is a key regulator of CD4 T-cell state says yes; the released data says no in this assay.
This is where a broad AI driver claim and this frozen assay part ways.

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

The signed frontier preserves an early literature-vs-data `Contradiction` object for each row. The
current public interpretation is narrower. These citations establish important biological or
therapeutic roles, but do not necessarily assert the same broad transcriptome-driver claim. Prospect
therefore uses the rows to limit that specific claim in this assay. It emits `contradicted` only when
a submitter explicitly makes a comparable causal-driver claim. An associative signature containing
the same genes receives `associative_only`, not `contradicted`.

*Citation note: gene roles above are drawn from PubMed.*

---

## Finding 3 - reach is not regulation

**Current claim.** High Rest reach argues against activation specificity, but does not by itself
establish housekeeping, essentiality, or irrelevance to immune biology. This wording qualifies the
legacy signed finding without changing the accepted root.

**Why effect size needs context.** CD3E, LAT, and PLCG1 (Finding 1) each move 5,000+ genes at
Stim8hr, similar in magnitude to SAGA and Mediator perturbations. Rest reach separates a
stimulation-gated pattern from a broad cross-state pattern in this assay. It does not determine why
the broad pattern occurs.

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

The displayed machinery examples sit at Rest DE 2,012 to 4,681. The activation module (Finding 1)
sits at Rest DE 1 to 7. The frozen predicate retains the historical internal name
`essentiality_artifact`, but the public finding is only about lack of activation specificity.

**The corrective test.** Replogle K562 provides genome-wide cross-cell context. RPE1 is sparse and
noncoverage is `not_assayed`, never a failure. The independently frozen GSE278572 comparator then
tests the interpretation in primary human CD4+ Teff and Treg contexts. MED12 meets the locked
qualification rule: its high Rest reach coexists with context-dependent activation effects. The
correction remains proposal-only and `accepted=false`.

---

## Finding 4 - verifier transfer

**Current claim.** The same checker can compare perturbation reach across primary CD4+ cells and
non-immune cell contexts. Cross-cell reach is orthogonal evidence about breadth, not a housekeeping
or essentiality label.

**Method** (`frontier/transfer.py`): run one `Claim` through `get_checker("marson")` and
`get_checker("replogle")`. One verifier shape, two frozen datasets, two verdicts.

The historical high-Rest group has median 71 K562 DE genes among the compared rows; the activation
module has median 4. MED19 moves 3,716 genes in K562 and BCL10 moves 2. This difference qualifies
cell-context breadth. It does not establish that every high-Rest gene is housekeeping or that every
K562-low gene is specific to T cells. Covered RPE1 rows are additional context; missing RPE1 rows
remain `not_assayed`.

---

## Finding 5 - recovering known regulons from perturbation

**Claim.** The frontier re-derives enrichment of known transcription-factor targets from
perturbation alone, with no regulon supplied to the screen. It also surfaces sign disagreements for
review.

**Method** (`frontier/regulon_slice.py`, `regulon_recover.py`): for each CollecTRI TF that is a
major regulator here, slice its data-derived target set from the frozen matrix and compare to its
CollecTRI literature regulon. Enrichment is a hypergeometric test over the measured gene universe;
direction uses the correct sign convention (a TF that activates a target should, on knockdown, make
it go down).

Across 154 TFs, literature targets are **4.0x enriched** among the genes their knockdown moved
(Fisher combined p approximately 1e-26), and when a data edge meets a known one the sign agrees
**63%** of the time. The Th1 and Th2 master factors **TBX21 (20x) and GATA3 (8x)** are recovered.
The screen surfaces **82 sign-disagreement edges**. Those disagreements can reflect cell context,
thresholds, or reference mismatch and do not by themselves overturn the literature.

---

## How they connect

The frontier recovers known activation biology (Finding 1) and regulon enrichment (Finding 5), then
uses the same frozen rules to limit broad driver claims (Finding 2), separate Rest reach from
activation specificity (Finding 3), and compare reach across cell contexts (Finding 4). The later
GSE278572 proposal demonstrates the intended correction loop: new evidence qualifies the
interpretation without silently rewriting accepted state. The separately pre-registered
GSE171737/GSE271788 calibration adds an independent result across 79 shared primary-CD4
perturbations. Its positive Stim48hr association passes three adversarial kills, while the different
activation times keep it cross-context evidence rather than condition-level equivalence.
