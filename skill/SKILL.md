---
name: prospect
description: >
  Check which biological claims in an AI-generated analysis are actually supported by the
  released ground-truth data, before you put them in a slide, grant, or paper. Use this when
  a user has interpreted a single-cell / CRISPR Perturb-seq result (especially CD4+ T-cell
  gene regulation) and wants to know which confident claims they can stand behind. Catches
  overstated "major regulator" and "promising target" claims against a frozen released table.
---

# Prospect — check AI biological claims against the data

You help a scientist decide which of an AI analysis's claims are real. The verdict must come
from **frozen code checking a frozen released table**, never from your own judgment.

## When to use

The user has an AI-written interpretation of a CD4+ T-cell CRISPRi Perturb-seq result and asks
things like "which of these can I trust / stand behind / report", "is X really a regulator",
or "check this before I present it."

## How to run it

1. **Extract each claim into a typed row** — do NOT verify in prose. For every gene the analysis
   makes a claim about, produce one JSON object:
   ```json
   {"text": "<the original sentence>", "gene": "SYMBOL",
    "condition": "Rest" | "Stim8hr" | "Stim48hr" | null,
    "asserts_major": true/false,        // claims it's a "major"/"key"/"broad" regulator
    "strength": "quantitative" | "promising_target" | "mechanism" | "clinical"}
   ```
   Use `null` condition when the claim is unqualified. Use `promising_target` / `mechanism` /
   `clinical` for interpretive claims (drug targets, causal mechanism) — those are never graded
   as true from this data.
2. Write the array to `claims.json`, then run the bundled checker:
   ```
   python scripts/check.py claims.json
   ```
3. **Report the card it prints verbatim.** Each claim gets one of:
   - `supported` — knockdown confirmed and the effect is real. *They can stand behind it.*
   - `refuted` — knockdown worked but the effect is too small for the "major" claim. *Do not report as-is.*
   - `unsupported` — no on-target knockdown; the perturbation didn't work. *Cannot conclude.*
   - `needs_qualification` — real only under a condition the claim didn't state. *Qualify it.*
   - `asserted` — interpretive (target/mechanism/clinical); not gradeable from this data.

## Hard rules

- **Never say "verified" or "true."** The strongest thing you may say is that the data
  *reproduces* / *supports* the quantitative claim.
- **"unsupported" (no knockdown) is not the same as "refuted" (contradicted).** Keep them
  distinct — one means the screen couldn't test it, the other means the data disagrees.
- This proves the *computation*, never the *biology*. Wet-lab and clinical truth are out of scope.
