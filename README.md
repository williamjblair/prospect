# Second Opinion

**Check which of your AI's biological claims the data actually supports — before you share them.**

Built for *Maya*, a scientist who runs a single-cell / CRISPR analysis, asks an AI
(Claude Science) to interpret it, and gets back a confident paragraph:

> *"CRISPRi of A1BG drives a broad activation program in stimulated CD4 T cells — a promising target."*

She has to present Thursday. Which of those claims can she actually stand behind?
Today she'd have to dig back into the data for each one. Most people don't. So
overstated results walk into lab meetings, grants, and papers.

**Second Opinion** reads an AI-generated analysis, extracts each scientific claim
into a typed contract, and independently checks it against the **released ground-truth
data** — deterministically, no model in the trust path. It hands back one page:

- ✅ **VAV1 is a major regulator** — on-target knockdown confirmed, 3,575 DE genes. *Stand behind it.*
- ❌ **A1BG is a promising target** — no knockdown detected, zero DE genes. *Do not report this.*
- ⚠️ **BCL10 regulates CD4 T-cell state** — only under stimulation (silent at rest). *Qualify it.*

It never says "verified." It tells you what the data supports.

## Why it's trustworthy

The verdict comes from **frozen code checking a frozen released table**, not from a
model's judgment. The AI decides *when* to check; the deterministic engine decides
*what's true*. Reproducible bit-for-bit, on a laptop, no GPU.

## Layers

1. **Engine** (`engine/`) — pluggable deterministic checkers, one per (dataset, claim-type).
   `marson_perturbseq` (CD4+ T-cell CRISPRi screen) and `op3` (perturbation-prediction) to start.
2. **Skill + CLI** (`skill/`, `cli/`) — an Agent Skill you invoke inside Claude Science, and a standalone CLI.
3. **Report + ledger** (`report/`) — the one-page card, and a persistent record of what's been checked.
4. **Benchmark** (`benchmark/`) — a measured rate of how often AI overstates biological claims, and how well this catches it.

## Quickstart

```bash
python3 tests/test_marson.py   # runs the checker on the real released Marson DE slice
```

## Data

- Marson CD4+ T-cell Perturb-seq (Zhu, Dann, … Marson 2025), MIT-licensed, CZI VCP:
  `s3://genome-scale-tcell-perturb-seq/marson2025_data/suppl_tables/DE_stats.suppl_table.csv`
- OpenProblems OP3 perturbation prediction (MIT):
  `s3://openproblems-data/resources/perturbation_prediction/datasets/neurips-2023-data/`

Ground-truth artifacts are frozen releases; the engine never re-runs a DE test.

## License

MIT. Built during Built with Claude: Life Sciences (Jul 7–13, 2026). See `NEW_WORK.md`.
