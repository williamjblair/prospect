# Prospect

A verified regulatory frontier of human CD4+ T-cell biology.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

An AI can assert a claim about any gene in a second. Confirming it against the data takes
longer than most people spend, so overstated biology walks into slides, grants, and papers.
Prospect inverts that. It holds a linked graph of gene regulation where every node and edge is
re-derived from released CRISPRi Perturb-seq data and signed by a human. Nothing a model says
enters the graph on the model's word. You see what the data holds.

The dataset is the Marson lab's genome-scale CRISPRi Perturb-seq screen in primary human CD4+ T
cells: 11,526 genes classified, 37,106 gene-to-gene regulatory edges sliced from the released
matrix, contradictions and open questions kept as first-class terrain. Every object carries a
sha256 over its frozen source fields, so `prospect verify` re-derives the whole frontier from
scratch with zero drift, and `prospect sign` accepts a root hash with one Ed25519 signature. No
model sits in that path.

The deeper idea is a boundary: `Activity < Receipt < Proposal < Review < Verification < Accepted <
State`. Generation is cheap; verified, replayable, human-accepted state is the scarce thing. A
**receipt** is the portable object that carries an AI's activity across that boundary, with a typed
status that never launders weak evidence as strong. See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the
full reasoning.

## What the data says

Four findings, mined deterministically from the released table and signed into the frontier.
Full definitions and thresholds live in [docs/FINDINGS.md](docs/FINDINGS.md).

1. **The activation module, rebuilt from perturbation.** The TCR-proximal cascade (CD3D/E/G,
   LAT, LCP2, PLCG1, ITK, BCL10, MALT1) is inert in a resting cell and moves thousands of genes
   once stimulated. The screen recovers a textbook pathway from knockout effects alone, and the
   frontier types every edge as condition-gated.
2. **Regulator vs effector.** The genes the field targets most, PD-1, TIM-3, CTLA-4, LAG-3,
   IL-2, IFN-γ, change almost nothing on knockdown even under stimulation. They are outputs of
   the program, not its drivers. Each is a literature-vs-data contradiction, cited to the review
   that calls it a regulator.
3. **Reach is not regulation.** Rank genes by raw effect and the top of the list is SAGA and
   Mediator machinery, essentiality dressed as immunology. Reach at rest separates housekeeping
   from activation-specific control.
4. **Verifier transfer.** The same major-regulator claim, checked against a second Perturb-seq
   dataset in K562 (a non-immune line, Replogle 2022). Essentiality artifacts reshape the K562
   transcriptome too (median 71 DE genes); the activation module stays inert (median 4). The
   second dataset confirms the split with independent data.

## The overclaiming benchmark

Ask four frontier models, blind, to name major regulators, then check every claim against the
frozen table. On one 220-gene sample, **48% of confident "major regulator" claims are
contradicted** by the data. On the genes the field targets most, the overclaim rate is **64%**:
models overstate the famous checkpoints and cytokines more often than random genes. Generation
is cheap. The scarce thing is knowing which claims survive the data.

## The loop

`prospect propose` closes it. Claude proposes candidate regulators, the frozen verifier decides,
a human signs the accepted set. In one run Claude proposed fifteen well-argued transcription
factors; the data admitted six and rejected nine, including FOXP3, the textbook master regulator,
because its knockdown does not broadly reshape the transcriptome in this assay. Claude is genuinely
useful at proposing. The admission decision stays a deterministic re-derivation plus a human key.

## Run it

```bash
./prospect verify                 # re-derive every object from frozen data (EXACT lane, 0 drift)
./prospect check claims.json --data <released_table.csv>   # grade typed claims
./prospect propose --n 15         # Claude proposes; the frozen verifier decides
./prospect agent                  # autonomous agent: search → verify → converge on a hypothesis
./prospect receipt                # emit portable receipts (activity → signed replayable state)
./prospect sign                   # the human ceremony: accept the frontier root
python benchmark/mutation_pack.py # the floor: zero tampered claim is ever admitted
```

The web app reads a single signed `frontier.json`; it runs credential-free and offline.

## Guarantees

- Deterministic findings from frozen released data, never a live DE recompute.
- Typed status only. The frontier never says "verified" or "true."
- Content-addressed and reproducible: `verify` re-derives 53k objects with zero drift.
- Human Ed25519 signature over the root. No model in any trust path.
- The mutation pack proves the floor: a tampered claim is never admitted as supported.
- The Skill ships a dependency-free checker; a parity test pins it to the engine, so the two
  copies cannot drift.

## Data

- Marson CD4+ T-cell CRISPRi Perturb-seq (Zhu, Dann, … Marson 2025), MIT-licensed:
  `s3://genome-scale-tcell-perturb-seq/marson2025_data/`
- Replogle genome-scale Perturb-seq, K562 (Replogle et al., Cell 2022, PMID 35688146), for the
  cross-cell-type transfer. Figshare article 20029387.

Ground-truth artifacts are frozen releases. The engine never re-runs a DE test.

## License

MIT. Built during Built with Claude: Life Sciences (Jul 7–13, 2026). See
[NEW_WORK.md](NEW_WORK.md).
