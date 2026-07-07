# Prospect · Built with Claude: Life Sciences

**A verified regulatory frontier of human CD4+ T-cell biology.**

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app) ·
Repo: [github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

## The problem

AI generates biology faster than anyone can check it. A model asserts that a gene is a key
regulator or a promising target in a sentence; confirming that against the data takes longer than
most people spend. So overstated claims walk into slides, grants, and papers. On the Marson lab's
own CD4+ T-cell screen, four frontier models overstate "major regulator" claims 48% of the time,
and 64% of the time on the genes the field targets most.

## What we built

Prospect is a linked, content-addressed graph of gene regulation where every node and edge
re-derives from released CRISPRi Perturb-seq data and carries a human signature. No model enters
the graph on its own word. On top of the graph:

- **Four signed findings** mined deterministically from the released table: the TCR activation
  module recovered from perturbation alone; the field's most-targeted genes shown to be effectors
  rather than drivers, each cited to PubMed; the essentiality artifact that a naive ranking mistakes
  for immunology; and a cross-cell-type transfer that confirms the split against a second dataset.
- **An overclaiming benchmark** across Haiku, Sonnet, Opus, and Fable on one frozen corpus.
- **A closed loop**: Claude proposes candidate regulators, the frozen verifier decides, a human
  signs the accepted set.

## How it uses Claude

- **Measured**: the benchmark grades Claude and other frontier models against ground truth, turning
  overclaiming into a number the substrate catches deterministically.
- **In the loop**: `prospect propose` uses Claude (Opus 4.8, adaptive thinking) to propose
  regulators; the frozen verifier gates them and a human key accepts them. Claude is useful at
  proposing, and is never in the trust path.
- **For literature**: finding contradictions are grounded in real reviews resolved through PubMed.
- **To build**: the whole system was written in Claude Code during the event.

## Results

- 11,526 genes, 37,106 regulatory edges, 4 signed findings, one signed root, 0 drift on re-derivation.
- 48% of confident AI major-regulator claims contradicted (4 models); 64% on checkpoints and cytokines.
- Cross-cell transfer: essentiality artifacts move a median of 71 genes in K562, the activation
  module 4. MED19 moves 3,716; BCL10 moves 2.
- The propose loop admitted 6 of Claude's 15 proposals and rejected FOXP3.
- The mutation-pack floor admits zero tampered claims; a parity test pins the Skill checker to the engine.

## Verify it yourself

```bash
./prospect verify                 # re-derive 53k objects from frozen data, 0 drift
./prospect propose --n 15         # Claude proposes; the data decides
python benchmark/mutation_pack.py # zero tampered claim is ever admitted
```

## Stack

Python (deterministic engine, frozen-table checkers, Ed25519 signing), Next.js 16 + Tailwind +
sigma.js (the frontier viewer, on the Constellate design system), Anthropic SDK for the benchmark
and the propose loop. Public data only. MIT-licensed. See `NEW_WORK.md`.
