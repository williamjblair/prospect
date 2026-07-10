"""Build the sealed GSE271788 and GSE171737 calibration pre-registration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "gse271788_preregistration.json"
OUT_DOC = ROOT / "docs" / "GSE271788_PREREGISTRATION.md"

RAW_COUNTS_SHA256 = "24f49fc8480a4b7b79fd2fd3ee03a2ca1429a6822f3b6d1ea6c30b13d02bf67c"
SEED = 271788


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def build_preregistration() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "schema_version": "prospect.gse271788.preregistration.v1",
        "phase": "independent_primary_cd4_calibration",
        "status": "evidence_attached",
        "accepted": False,
        "next": "freeze_sources_before_scoring",
        "trust_boundary": "proposal_only",
        "frontier_root": "root_a8b0dcdd4024e12f",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        "hypothesis": (
            "Perturbations with broader transcriptomic reach at Marson Stim48hr also have broader "
            "reach in the independent day-eight activated primary-CD4 knockout study."
        ),
        "sources": [
            {
                "accession": "GSE271788",
                "role": "60-target primary human CD4 knockout batch and combined count matrix",
                "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE271788",
            },
            {
                "accession": "GSE171737",
                "role": "24-target IL2RA-regulator primary human CD4 knockout batch",
                "url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE171737",
            },
            {
                "accession": "PMID:39395408",
                "role": "published methods and supplementary effect tables",
                "url": "https://pubmed.ncbi.nlm.nih.gov/39395408/",
            },
        ],
        "source_contract": {
            "raw_counts_filename": "GSE271788_dedup_counts.txt.gz",
            "raw_counts_sha256": RAW_COUNTS_SHA256,
            "expected_count_columns": 311,
            "expected_targets": 84,
            "expected_donors_per_target": 3,
            "expected_marson_overlap": 79,
            "expected_not_assayed": 5,
            "required_published_tables": ["S4", "S5", "S11", "S12"],
            "missing_row_semantics": "not_assayed",
            "abort_if_unpinned": [
                "published LFSR table",
                "batch labels",
                "target mapping",
                "source hashes",
            ],
        },
        "primary_analysis": {
            "population": "targets present in both the frozen Marson table and the published effect table",
            "expected_n": 79,
            "marson_measure": "released n_total_de_genes at Stim48hr",
            "independent_measure": "count of downstream genes with published mashr LFSR below 0.005",
            "statistic": "spearman_rho",
            "permutations": 10000,
            "bootstrap_samples": 10000,
            "seed": SEED,
            "reporting_conditions": ["Rest", "Stim8hr", "Stim48hr", "strongest_condition"],
            "decision_condition": "Stim48hr",
            "positive_rule": "permutation_p_value_at_most_0.01",
        },
        "comparability": {
            "status": "orthogonal_activation_context",
            "reason": (
                "The independent cells were activated for eight days, while Marson measures Rest, "
                "Stim8hr, and Stim48hr. The study can calibrate broad activated-CD4 reach but cannot "
                "earn contradicted for a Marson condition claim."
            ),
            "contradicted_allowed": False,
        },
        "kill_rules": [
            {
                "kill_id": "batch_specificity",
                "axis": "independent experimental batch",
                "rule": "Spearman rho must be positive in both the 24-target and 60-target batches.",
            },
            {
                "kill_id": "general_machinery",
                "axis": "broad K562 transcriptomic effect",
                "rule": "After excluding targets with Replogle K562 reach above 25, Spearman rho must remain positive.",
            },
            {
                "kill_id": "influential_target",
                "axis": "single-target leverage",
                "rule": "Every leave-one-target-out Spearman rho must remain positive.",
            },
        ],
        "typing_rule": {
            "evidence_attached": (
                "The primary permutation P value is at most 0.01 and all three kill rules pass."
            ),
            "orthogonal_phenotype": "The primary rule or any kill rule fails.",
            "not_assayed": "The target or required published effect row is absent.",
            "contradicted": "not available for this cross-context calibration",
        },
        "named_result_policy": (
            "MED12 is an inspected calibration control, not a newly selected discovery. Any other "
            "named result must emerge from a rule sealed before its effect is inspected."
        ),
        "goalpost_policy": (
            "No threshold, endpoint, missing-row rule, or kill criterion may change after this "
            "pre-registration is committed. A failed source contract aborts the analysis."
        ),
        "replay": "python frontier/gse271788_preregistration.py --check",
    }
    digest = hashlib.sha256(_canonical_json(packet)).hexdigest()
    return {
        **packet,
        "pre_registration_id": f"prereg_{digest[:16]}",
        "content_signature": f"prereg_sig_{digest}",
        "signature_scope": "content seal only, not accepted frontier state",
    }


def render_markdown(packet: dict[str, Any]) -> str:
    kills = "\n".join(
        f"- `{row['kill_id']}`: {row['rule']}" for row in packet["kill_rules"]
    )
    return f"""# GSE271788 and GSE171737 calibration pre-registration

Status: `evidence_attached`  
Accepted: `false`  
Pre-registration: `{packet['pre_registration_id']}`

## Locked question

{packet['hypothesis']}

This analysis is computation over released data, not wet-lab or clinical truth. The independent
day-eight activation context is not identical to any Marson condition. It can attach evidence about
broad activated-CD4 transcriptomic reach, but it cannot earn `contradicted` for a Marson claim.

## Frozen source contract

- Combined raw counts: `{packet['source_contract']['raw_counts_filename']}`.
- Expected SHA-256: `{packet['source_contract']['raw_counts_sha256']}`.
- Expected shape: 311 count columns, 84 targets, three donors per target.
- Expected Marson overlap: 79 targets, with five targets typed `not_assayed`.
- Required published tables before scoring: S4, S5, S11, and S12.
- Missing rows are `not_assayed`, never zero.

If the LFSR table, batch labels, target mapping, or source hashes cannot be pinned exactly, the
analysis stops. No substitute scoring rule is allowed after outcomes are inspected.

## Locked analysis

The primary comparison is frozen Marson `Stim48hr` `n_total_de_genes` against the count of published
downstream effects with mashr LFSR below 0.005. The statistic is Spearman rho over the overlapping
targets. The permutation P value and bootstrap interval use 10,000 iterations and seed 271788.
Rest, Stim8hr, and strongest-condition results are descriptive only.

## Adversarial kills

{kills}

The result earns `evidence_attached` only when the primary permutation P value is at most 0.01 and
all three kills pass. Otherwise it is `orthogonal_phenotype`. MED12 remains an inspected calibration
control, not a newly selected discovery.

## Seal and replay

The content signature is `{packet['content_signature']}`. It seals this pre-registration only and
does not change accepted state.

```bash
python frontier/gse271788_preregistration.py --check
```
"""


def write_preregistration(
    *, out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC
) -> dict[str, Any]:
    packet = build_preregistration()
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(render_markdown(packet))
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet = build_preregistration()
    if args.check:
        if not OUT_JSON.exists() or json.loads(OUT_JSON.read_text()) != packet:
            raise SystemExit("gse271788 pre-registration drift")
        if not OUT_DOC.exists() or OUT_DOC.read_text() != render_markdown(packet):
            raise SystemExit("gse271788 pre-registration document drift")
    else:
        write_preregistration()
    print(
        f"{packet['pre_registration_id']} status={packet['status']} "
        f"accepted={str(packet['accepted']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
