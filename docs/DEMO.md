# Demo script (2 minutes)

The arc is connector, refusal, then reveal. Never open on the map. Open on reproducible association
being separated into drivers and passengers.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Recording runbook: [DEMO_RECORDING_RUNBOOK.md](DEMO_RECORDING_RUNBOOK.md)

**0:00 · Connector.** Overview tab. Start at the acceptance-layer panel. A real Claude Science export
from the Sade-Feldman melanoma ICB scRNA-seq session produces a reproducible associative signature
with AUC 0.859 and an internal review completed with 0 findings. Prospect asks the causal question
the session itself says remains open: which genes are causal drivers and which are associative
passengers when perturbed in Marson CRISPRi? The answer is typed, not laundered: 52 genes checked,
12 drivers typed `evidence_attached`, 22 `associative_only` passengers, 3 `contradicted` explicit
checkpoint-driver claims, 15 `not_assayed`, `accepted=false`, and `human_signature_required`.

**0:25 · Refusal.** Overview tab. Read the AI claim on the opening claim cards: *"CRISPRi of A1BG drives
a broad activation program in stimulated CD4 T cells, a promising target."* It sounds right. The
frozen checker marks it **unsupported**: A1BG was never knocked down, so the perturbation did not
happen. The claim has no basis. One line: an AI can assert this in a second; confirming it is the
slow part almost no one does.

**0:45 · The number.** The headline card: **48% of confident AI "major regulator" claims are
contradicted** by the measured data, pooled across four frontier models on one frozen sample. Then
the tie-in: on the genes the field targets most, PD-1, TIM-3, IL-2, the overclaim rate is **64%**.
Models overstate the famous genes more than random ones.
Point to the Judge packet card: the live root, commands, and public data are one click away.

**1:00 · Findings.** Findings tab. Start with the scannable index: five reproduced finding objects,
ordered as recover, catch, resist, transfer, recover regulons. Finding 01: the TCR cascade, silent
at rest and moving 5,000+ genes once stimulated (CD3E 4 → 5,711). Finding 02: PD-1, TIM-3, CTLA-4
change almost nothing on knockdown, each a literature-vs-data contradiction cited to the review that
calls it a regulator.

**1:20 · The moat.** Finding 04, verifier transfer, then the substrate replay packet. The same claim,
run through `get_checker("marson")` and `get_checker("replogle")`. Essentiality genes reshape a
non-immune cell too (MED19 moves 3,716 genes in K562); the immune program stays inert (BCL10 moves
2). The substrate replay packet keeps the result `computationally_reproduced` across Marson CD4+ T
cells, Replogle K562, and Replogle RPE1, with no accepted-state mutation.

**1:40 · The defended endgame.** Overview tab. Scroll to the defended-discovery endgame. The
pre-registration locked the bar before the deep dive: strong Marson driver signal, Replogle K562
and RPE1 specificity, five-plus frozen public datasets, comparator-readout checks, mechanism, hook,
three kill attempts, and a falsifiable stimulated primary CD4+ experiment. Prospect worked down all
18 locked candidates. Zero cleared. Four retained independent primary T-cell support, but all 18
hit the same hard blocker: missing RPE1 assay coverage. This is the point, the system found signal
and refused to promote it past the evidence.

**1:55 · Close.** Frontier tab, executable bridge path. This is not a trace viewer. `./prospect mcp`
lets Claude Science or another workbench discover the receipt schema, validate a receipt, submit a
gene list, and receive typed Prospect verdicts only as a proposal. Agent tab, PGGT1B deep dive. The
packet shows 3,014 Stim8hr DE genes, 175 Rest DE genes,
1 K562 DE gene, 0 CollecTRI targets, a 17.22x stimulation ratio, a 3014x transfer check, two
literature hooks, a released-matrix slice of 671 moved transcripts, missing evidence before acceptance,
and a stimulated CD4+ assay readout.
Then open `/data/defended_discovery_endgame_exhaustion.json`. The whole frontier re-derives from
frozen data with zero drift and carries one human signature. Generation is cheap. Accepted state is
the scarce thing, and it compounds.
