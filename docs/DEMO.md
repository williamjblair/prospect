# Demo script (2 minutes)

The arc is refusal, then reveal, then number. Never open on the map. Open on a model being wrong.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Recording runbook: [DEMO_RECORDING_RUNBOOK.md](DEMO_RECORDING_RUNBOOK.md)

**0:00 · Refusal.** Overview tab. Read the AI claim on the opening claim cards: *"CRISPRi of A1BG drives
a broad activation program in stimulated CD4 T cells, a promising target."* It sounds right. The
frozen checker marks it **unsupported**: A1BG was never knocked down, so the perturbation did not
happen. The claim has no basis. One line: an AI can assert this in a second; confirming it is the
slow part almost no one does.

**0:20 · The number.** The headline card: **48% of confident AI "major regulator" claims are
contradicted** by the measured data, pooled across four frontier models on one frozen sample. Then
the tie-in: on the genes the field targets most, PD-1, TIM-3, IL-2, the overclaim rate is **64%**.
Models overstate the famous genes more than random ones.
Point to the Judge packet card: the live root, commands, and public data are one click away.

**0:40 · Findings.** Findings tab. Start with the scannable index: five reproduced finding objects,
ordered as recover, catch, resist, transfer, recover regulons. Finding 01: the TCR cascade, silent
at rest and moving 5,000+ genes once stimulated (CD3E 4 → 5,711). Finding 02: PD-1, TIM-3, CTLA-4
change almost nothing on knockdown, each a literature-vs-data contradiction cited to the review that
calls it a regulator.

**1:05 · The moat.** Finding 04, verifier transfer, then the substrate replay packet. The same claim,
run through `get_checker("marson")` and `get_checker("replogle")`. Essentiality genes reshape a
non-immune cell too (MED19 moves 3,716 genes in K562); the immune program stays inert (BCL10 moves
2). The substrate replay packet keeps the result `computationally_reproduced` across Marson CD4+ T
cells, Replogle K562, and Replogle RPE1, with no accepted-state mutation.

**1:30 · The loop.** Agent tab, campaign pressure summary. Claude proposed fifteen transcription
factors, then pressure-tested the campaign rows. The twenty probed rows became review work: six
aligned with deterministic review, eleven more-aggressive recommendations became assay gates, three
were more cautious, and all eleven gates returned proposal-only review evidence. Zero
accepted-state mutations occurred. Claude proposes; frozen code decides; a human key accepts state.

**1:50 · Close.** Frontier tab, executable bridge path. This is not a trace viewer. `./prospect mcp`
lets another workbench discover the receipt schema, validate a receipt, and submit it only as a
proposal. Agent tab, PGGT1B deep dive. The packet shows 3,014 Stim8hr DE genes, 175 Rest DE genes,
1 K562 DE gene, 0 CollecTRI targets, a 17.22x stimulation ratio, a 3014x transfer check, two
literature hooks, a released-matrix slice of 671 moved transcripts, missing evidence before acceptance,
and a stimulated CD4+ assay readout.
Then scroll to the lab assay packet, assay operations bundle, and pilot design. It gives five
assay-ready rows with expected positive results, weakening results, rejection results, missing
evidence before any status change, and 90 proposal-only culture arms across three donor replicates.
The campaign leaderboard keeps 20 proposal-only follow-ups ranked by the same frozen facts,
plus the review appendix with lane counts, audit questions, per-row decisions, and stop rules. The
campaign pressure summary shows Claude aligned on some rows, pushed harder on others, and still
caused zero accepted-state mutations. The disagreement triage turns that pressure into assay gates,
not accepted state. The campaign gate probe asks whether those gates are sufficient, need another
control, or should be lower priority. The whole frontier re-derives from frozen data with zero drift
and carries one human signature. Generation is cheap. Accepted state is the scarce thing, and it
compounds.
