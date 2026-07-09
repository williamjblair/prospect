# Public Robustness Report

Prospect accepts common AI-biology submission shapes and either types them honestly or fails cleanly. Every typed submission remains accepted=false with next=human_signature_required. The trust path is frozen code over released data plus a human key. Computation over released data, not wet-lab or clinical truth.

- Cases exercised: 118
- Typed cases: 103
- Clean failures: 15
- Crashes: 0
- Silent wrong answers found: 0
- Largest typed case: 163 unique genes
- Typed totals: 54 evidence_attached, 40 associative_only, 65 contradicted, 2679 not_assayed

## Input Classes

| class | typed | clean failures |
| --- | ---: | ---: |
| clean_failure | 0 | 15 |
| context_routing | 1 | 0 |
| de_table | 1 | 0 |
| duplicates | 20 | 0 |
| huge_list | 14 | 0 |
| injection_strings | 14 | 0 |
| mixed_identifier_mapping | 1 | 0 |
| plain_gene_list | 1 | 0 |
| ranked_markers | 1 | 0 |
| signature_json | 14 | 0 |
| unknown_and_nonhuman | 36 | 0 |

## Reproduce

```bash
./prospect robustness-fuzz
python -m pytest tests/test_public_robustness.py -q
```

The JSON packet is written to `examples/data/public_robustness_fuzz.json` and exported at `/data/public_robustness_fuzz.json`.
