# Exhaustive coverage expansion pre-registration

ID: `exhaustive_coverage_prereg_941caf798f718e0e`

Frontier root: `root_a8b0dcdd4024e12f`. accepted=false. next=human_signature_required.

Ceiling: Computation over released data, not wet-lab or clinical truth.

No model is in the trust path. Anthropic budget: $0.

## Source

- ORCS: `https://orcs.thebiogrid.org/scripts/datatableTools.php`
- NCBI gene mapping: `https://clinicaltables.nlm.nih.gov/api/ncbi_genes/v3/search`

## Target Scale

all 11,526 genes in the current frozen atlas.

## Coverage Rules

- `covered`: NCBI maps the symbol and ORCS returns at least one T-cell filtered row
- `mapped_no_tcell_rows`: NCBI maps the symbol but ORCS returns zero T-cell filtered rows
- `unmapped`: NCBI does not map the symbol to a human gene id
- `network_error`: the lookup failed and must be retried before final freezing
- `noncoverage_policy`: noncoverage is never a contradiction

## Checkpoint Contract

- State: `output/exhaustive_coverage/coverage_state.json`
- Rows: `output/exhaustive_coverage/orcs_tcell_gene_rows.jsonl`
- Snapshot: `output/exhaustive_coverage/coverage_snapshot.json`
- Log: `output/exhaustive_coverage/coverage.log`

## Public Artifact

- `/data/exhaustive_coverage_preregistration.json`

## Reproduce

```bash
./prospect exhaustive-coverage --phase preregister
```
