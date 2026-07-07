# Demo script (2 minutes)

The arc is refusal, then reveal, then number. Never open on the map. Open on a model being wrong.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

**0:00 · Refusal.** Overview tab. Read the AI claim on the demo chips: *"CRISPRi of A1BG drives
a broad activation program in stimulated CD4 T cells, a promising target."* It sounds right. The
frozen checker marks it **unsupported**: A1BG was never knocked down, so the perturbation did not
happen. The claim has no basis. One line: an AI can assert this in a second; confirming it is the
slow part almost no one does.

**0:20 · The number.** The headline card: **48% of confident AI "major regulator" claims are
contradicted** by the measured data, pooled across four frontier models on one frozen sample. Then
the tie-in: on the genes the field targets most, PD-1, TIM-3, IL-2, the overclaim rate is **64%**.
Models overstate the famous genes more than random ones.

**0:40 · Findings.** Findings tab. Finding 01: the TCR cascade, silent at rest and moving 5,000+
genes once stimulated (CD3E 4 → 5,711). The screen rebuilt a textbook pathway from knockout effects
with no priors. Finding 02: PD-1, TIM-3, CTLA-4 change almost nothing on knockdown, each a
literature-vs-data contradiction cited to the review that calls it a regulator.

**1:05 · The moat.** Finding 04, verifier transfer. The same claim, run through
`get_checker("marson")` and `get_checker("replogle")`. Essentiality genes reshape a non-immune cell
too (MED19 moves 3,716 genes in K562); the immune program stays inert (BCL10 moves 2). A second
independent dataset confirms which regulators are housekeeping and which are T-cell-specific.

**1:30 · The loop.** Back to Overview, the propose panel. Claude proposed fifteen transcription
factors. The frozen verifier admitted six and rejected nine, including FOXP3, the textbook master
regulator, because its knockdown does not broadly reshape the transcriptome here. A human signs the
accepted delta. Claude proposes; the data decides; a human signs.

**1:50 · Close.** Frontier tab, receipt bridge. This is not a trace viewer. `./prospect mcp`
lets another workbench discover the receipt contract, validate a receipt, and submit it only as a
proposal. Agent tab, PGGT1B deep dive. The packet shows 3,014 Stim8hr DE genes, 175 Rest DE genes,
1 K562 DE gene, 0 CollecTRI targets, two literature hooks, and a stimulated CD4+ assay readout.
The whole frontier re-derives from frozen data with zero drift and carries one human signature.
Generation is cheap. Accepted state is the scarce thing, and it compounds.
