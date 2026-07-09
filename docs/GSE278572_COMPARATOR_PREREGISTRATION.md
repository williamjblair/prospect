# GSE278572 corrective comparator pre-registration

## Purpose

This proposal-only comparator tests one interpretation attached to Prospect Finding 3. Prospect
measures high transcriptional reach at Rest for 139 genes. The current finding describes that
reach as evidence of housekeeping or essentiality. GSE278572 can test whether high Rest reach is
also compatible with a context-dependent regulator of T-cell rest and activation.

The measured Prospect DE counts are not under review. The interpretation of those counts is.

Status: `evidence_attached`  
Accepted: `false`  
Trust boundary: `proposal_only`

This is computation over released data, not wet-lab or clinical truth. It does not change the
signed Prospect frontier.

## Sources frozen before scoring

The authors' reduced tables were downloaded from Zenodo record 13924126 as `data_tables.zip`.
The archive is 57,967,623 bytes with SHA-256
`dc9e2efb04d24f1a6d4b8db6a8b1d5cd01c935777c3740088be339de5b5062b4`.

Three source tables are in scope:

| Table | Grain | Cardinality | SHA-256 |
| --- | --- | ---: | --- |
| S8 activation scoring | target by cell context | 116 rows, 29 labels, 4 contexts | `90c58844937d744465c6de4f3306c9b37c01983a72a6c1e816df1b7d7907ee57` |
| S9 significant pseudobulk DE | DE gene by target, lineage, and state | 705 rows | `962a17eefae7f720af2207f0d55065ab27f4f84e0abe6a2977fbb4e5f0ed7308` |
| S14 cell metadata | one retained cell | 100,087 rows, 2 donors | `ee33fc765234e073aaac9bf394ea067df63f196c22bb6c7b6dbbead09ee2343b` |

All 100,087 S14 cell barcodes occur in the 249,799-barcode GEO file. The frozen GEO barcode file
has SHA-256 `0c26723009bb4e507437c49ba92e382506f676c8e3c1ba19245db1208a2514b7`.

The compact committed projections preserve all 116 S8 rows and all 705 S9 rows. S14 is represented
by a frozen metadata summary because the per-cell workbook is 29 MB and is not required for the
locked comparison.

## Locked comparison

1. Freeze all 28 perturbation targets, the non-targeting control, and all four contexts before
   scoring.
2. Match GSE278572 resting Teff to Prospect `Rest`, and stimulated Teff at 48 hours to Prospect
   `Stim48hr`. Treg is an informative extension, not an exact Prospect match.
3. Define the activation-score effect as the target median minus the same-context non-targeting
   median from S8.
4. Call the activation-score effect significant only when the published S8 adjusted P value is
   below 0.01.
5. Count published significant pseudobulk DE rows from S9 for each target, lineage, and state.
6. A current high-Rest gene requires qualification only if, within the same lineage:
   - the Resting and Stimulated activation-score effects are both significant;
   - the two activation-score deltas have opposite signs; and
   - each state has more than 10 published significant pseudobulk DE genes.
7. A missing S9 row counts as zero only when S8 and S14 establish that the target-context pair was
   assayed.
8. MED12 is an inspected positive control. The source study and its MED12 result were read during
   planning, so this is not a blinded discovery analysis.

The threshold and direction rules may not change after scoring.

## Stop conditions

Stop without a biological interpretation if any of the following occurs:

- A source hash, source schema, target set, or cardinality differs from the frozen manifest.
- Donor, context, target, or guide labels cannot be recovered exactly.
- Any retained S14 cell barcode is absent from the GEO barcode file.
- A missing S9 row cannot be distinguished from an unassayed target-context pair.
- Reconstructing the raw 3.6 GB expression matrix becomes necessary.
- The result requires changing a threshold after inspecting MED12.

## Interpretation boundary

This is a selected 28-target CRISPRi library from the same research group as the broader Prospect
substrate. It has two donors, separates Teff and Treg, and uses different published analysis
thresholds. It can qualify an interpretation, but it is not an independent genome-scale
reproduction and cannot support a new accepted state without human review.

Replay after the compact projections are frozen:

```bash
python frontier/gse278572_comparator.py --check
python -m pytest tests/test_gse278572_comparator.py -q
```
