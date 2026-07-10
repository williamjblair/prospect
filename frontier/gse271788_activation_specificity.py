"""Re-derive the pre-registered activation-specificity sensitivity proposal."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gse271788_calibration import (  # noqa: E402
    DATA,
    K562,
    MARSON,
    SOURCE_DIR,
    DataConstraintError,
    _canonical_id,
    _rank,
    _sha256,
    validate_frozen_inputs,
)
from receipt.schema import Artifact, EvidenceAtom, Receipt, Verifier  # noqa: E402


PREREG = DATA / "gse271788_activation_specificity_preregistration.json"
OUT_JSON = DATA / "gse271788_activation_specificity.json"
OUT_DOC = ROOT / "docs" / "GSE271788_ACTIVATION_SPECIFICITY.md"
EXPECTED_PREREG_ID = "prereg_2fd47506461840d1"
SEED = 271789
SAMPLES = 10000
BATCHES = ("gse171737_il2ra_regulators", "gse271788_iei_background")


def _canonical_prereg_id(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("pre_registration_id", None)
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return "prereg_" + hashlib.sha256(encoded).hexdigest()[:16]


def validate_preregistration() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    actual = prereg.get("pre_registration_id")
    if actual != EXPECTED_PREREG_ID or actual != _canonical_prereg_id(prereg):
        raise DataConstraintError("activation-specificity pre-registration id drift")
    if prereg.get("frontier_root") != "root_a8b0dcdd4024e12f":
        raise DataConstraintError("activation-specificity frontier root drift")
    if prereg.get("accepted") is not False:
        raise DataConstraintError("activation-specificity pre-registration must remain proposal only")
    for binding in prereg.get("source_bindings", []):
        path = ROOT / binding["path"]
        if not path.exists() or _sha256(path) != binding["sha256"]:
            raise DataConstraintError(f"activation-specificity source drift: {binding['path']}")
    if len(prereg.get("source_bindings", [])) != 6:
        raise DataConstraintError("activation-specificity source binding count drift")
    return prereg


def _orthonormal_basis(columns: list[list[float]]) -> list[list[float]]:
    basis: list[list[float]] = []
    for column in columns:
        vector = [float(value) for value in column]
        for unit in basis:
            scale = sum(value * component for value, component in zip(vector, unit))
            vector = [value - scale * component for value, component in zip(vector, unit)]
        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 1e-10:
            basis.append([value / norm for value in vector])
    return basis


def _residualize(values: list[float], basis: list[list[float]]) -> list[float]:
    residual = [float(value) for value in values]
    for unit in basis:
        scale = sum(value * component for value, component in zip(values, unit))
        residual = [value - scale * component for value, component in zip(residual, unit)]
    return residual


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 3:
        raise DataConstraintError("partial-correlation inputs must have equal length above two")
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    denominator = math.sqrt(
        sum((x - left_mean) ** 2 for x in left)
        * sum((y - right_mean) ** 2 for y in right)
    )
    if denominator <= 1e-12:
        raise DataConstraintError("partial-correlation residual is constant")
    return numerator / denominator


def _partial_components(
    rows: list[dict[str, Any]],
    extra_covariates: tuple[str, ...] = (),
) -> dict[str, Any]:
    if len(rows) < 5:
        raise DataConstraintError("partial-correlation model needs at least five rows")
    stim_rank = _rank([float(row["stim48_reach"]) for row in rows])
    independent_rank = _rank([float(row["independent_reach"]) for row in rows])
    rest_rank = _rank([float(row["rest_reach"]) for row in rows])
    batch_rank = [float(BATCHES.index(row["batch"])) for row in rows]
    columns = [[1.0] * len(rows), rest_rank, batch_rank]
    for key in extra_covariates:
        columns.append(_rank([float(row[key]) for row in rows]))
    basis = _orthonormal_basis(columns)
    if len(rows) <= len(basis) + 1:
        raise DataConstraintError("partial-correlation model has insufficient residual degrees of freedom")
    stim_residual = _residualize(stim_rank, basis)
    independent_residual = _residualize(independent_rank, basis)
    return {
        "rho": _pearson(stim_residual, independent_residual),
        "stim_rank": stim_rank,
        "independent_rank": independent_rank,
        "stim_residual": stim_residual,
        "independent_residual": independent_residual,
        "independent_fitted": [
            value - residual for value, residual in zip(independent_rank, independent_residual)
        ],
        "basis": basis,
        "model_rank": len(basis),
    }


def _partial_spearman(
    rows: list[dict[str, Any]],
    extra_covariates: tuple[str, ...] = (),
) -> float:
    return float(_partial_components(rows, extra_covariates)["rho"])


def _freedman_lane_p(rows: list[dict[str, Any]], observed: float) -> float:
    components = _partial_components(rows)
    residual = components["independent_residual"]
    fitted = components["independent_fitted"]
    stim_residual = components["stim_residual"]
    basis = components["basis"]
    indices_by_batch: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        indices_by_batch[row["batch"]].append(index)
    rng = random.Random(SEED)
    at_least_observed = 0
    for _ in range(SAMPLES):
        permuted_residual = list(residual)
        for batch in BATCHES:
            indices = indices_by_batch[batch]
            values = [residual[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                permuted_residual[index] = value
        pseudo_outcome = [base + value for base, value in zip(fitted, permuted_residual)]
        pseudo_residual = _residualize(pseudo_outcome, basis)
        if _pearson(stim_residual, pseudo_residual) >= observed:
            at_least_observed += 1
    return (at_least_observed + 1) / (SAMPLES + 1)


def _stratified_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows_by_batch = {
        batch: [row for row in rows if row["batch"] == batch]
        for batch in BATCHES
    }
    rng = random.Random(SEED)
    estimates: list[float] = []
    discarded = 0
    while len(estimates) < SAMPLES:
        sampled = []
        for batch in BATCHES:
            batch_rows = rows_by_batch[batch]
            sampled.extend(batch_rows[rng.randrange(len(batch_rows))] for _ in batch_rows)
        try:
            estimates.append(_partial_spearman(sampled))
        except DataConstraintError:
            discarded += 1
            if discarded > 100:
                raise DataConstraintError("too many singular stratified bootstrap samples")
    estimates.sort()
    return {
        "interval": [
            round(estimates[int(0.025 * len(estimates))], 6),
            round(estimates[int(0.975 * len(estimates)) - 1], 6),
        ],
        "samples": len(estimates),
        "discarded_singular_samples": discarded,
    }


def _load_rows(source_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with (source_dir / "target_reach.csv").open(newline="") as handle:
        target_rows = list(csv.DictReader(handle))
    target_by_gene = {row["gene"]: row for row in target_rows}
    with MARSON.open(newline="") as handle:
        marson = {
            (row["target_contrast_gene_name"], row["culture_condition"]): row
            for row in csv.DictReader(handle)
        }
    with K562.open(newline="") as handle:
        k562 = {row["gene"]: int(float(row["k562_de"])) for row in csv.DictReader(handle)}

    marson_genes = {gene for gene, _ in marson}
    overlap = sorted(set(target_by_gene) & marson_genes)
    missing_rows = []
    complete = []
    for gene in overlap:
        missing = [
            condition
            for condition in ("Rest", "Stim48hr")
            if (gene, condition) not in marson
        ]
        if missing:
            missing_rows.append({"gene": gene, "missing_conditions": missing})
            continue
        source = target_by_gene[gene]
        complete.append({
            "gene": gene,
            "batch": source["batch"],
            "independent_reach": int(source["published_mashr_lfsr_lt_0_005"]),
            "rest_reach": int(marson[(gene, "Rest")]["n_total_de_genes"]),
            "stim48_reach": int(marson[(gene, "Stim48hr")]["n_total_de_genes"]),
            "k562_reach": k562.get(gene),
            "live_cell_count_median": float(source["live_cell_count_median"]),
            "editing_efficiency_median": (
                float(source["editing_efficiency_median"])
                if source["editing_efficiency_median"]
                else None
            ),
        })
    if len(overlap) != 79 or len(complete) != 76:
        raise DataConstraintError("activation-specificity complete-case cardinality drift")
    return complete, {
        "starting_targets": len(overlap),
        "complete_cases": len(complete),
        "complete_case_targets": [row["gene"] for row in complete],
        "missing_complete_case_rows": missing_rows,
        "batch_complete_cases": {
            batch: sum(row["batch"] == batch for row in complete)
            for batch in BATCHES
        },
    }


def _kill_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    batch_results = {}
    for batch in BATCHES:
        subset = [row for row in rows if row["batch"] == batch]
        rho = _partial_spearman(subset)
        batch_results[batch] = {"n": len(subset), "partial_spearman_rho": round(rho, 6)}

    k562_not_assayed = sorted(row["gene"] for row in rows if row["k562_reach"] is None)
    k562_excluded = sorted(
        row["gene"] for row in rows
        if row["k562_reach"] is not None and row["k562_reach"] > 25
    )
    machinery_rows = [row for row in rows if row["gene"] not in k562_excluded]
    machinery_rho = _partial_spearman(machinery_rows)

    leave_one_out = []
    for excluded in rows:
        subset = [row for row in rows if row["gene"] != excluded["gene"]]
        leave_one_out.append({
            "excluded_gene": excluded["gene"],
            "partial_spearman_rho": round(_partial_spearman(subset), 6),
        })
    minimum_leave_one_out = min(leave_one_out, key=lambda row: row["partial_spearman_rho"])

    rng = random.Random(SEED)
    leave_five_estimates = []
    genes = [row["gene"] for row in rows]
    for _ in range(SAMPLES):
        excluded = set(rng.sample(genes, 5))
        subset = [row for row in rows if row["gene"] not in excluded]
        leave_five_estimates.append(_partial_spearman(subset))
    positive = sum(value > 0 for value in leave_five_estimates)

    cell_count_rho = _partial_spearman(rows, ("live_cell_count_median",))
    return {
        "batch_direction": {
            "passed": all(row["partial_spearman_rho"] > 0 for row in batch_results.values()),
            "batches": batch_results,
        },
        "general_machinery": {
            "passed": machinery_rho > 0,
            "n": len(machinery_rows),
            "partial_spearman_rho": round(machinery_rho, 6),
            "excluded_k562_above_25": k562_excluded,
            "k562_not_assayed": k562_not_assayed,
            "missing_coverage_policy": "retained in the model and reported as not_assayed",
        },
        "influential_target": {
            "passed": minimum_leave_one_out["partial_spearman_rho"] > 0,
            "runs": len(leave_one_out),
            "minimum_leave_one_out": minimum_leave_one_out,
            "maximum_partial_spearman_rho": max(
                row["partial_spearman_rho"] for row in leave_one_out
            ),
        },
        "subset_instability": {
            "passed": positive / SAMPLES >= 0.95,
            "runs": SAMPLES,
            "leave_five": 5,
            "positive_runs": positive,
            "positive_fraction": round(positive / SAMPLES, 6),
            "minimum_partial_spearman_rho": round(min(leave_five_estimates), 6),
            "median_partial_spearman_rho": round(statistics.median(leave_five_estimates), 6),
            "maximum_partial_spearman_rho": round(max(leave_five_estimates), 6),
            "seed": SEED,
        },
        "cell_count_confound": {
            "passed": cell_count_rho > 0,
            "n": len(rows),
            "partial_spearman_rho": round(cell_count_rho, 6),
            "covariate": "ranked median live-cell count",
        },
    }


def build_result(source_dir: Path = SOURCE_DIR) -> dict[str, Any]:
    prereg = validate_preregistration()
    source_integrity = validate_frozen_inputs(source_dir)
    rows, coverage = _load_rows(source_dir)

    observed = _partial_spearman(rows)
    permutation_p = _freedman_lane_p(rows, observed)
    bootstrap = _stratified_bootstrap(rows)
    kills = _kill_results(rows)
    all_kills_pass = all(row["passed"] for row in kills.values())
    primary_pass = permutation_p <= 0.01 and bootstrap["interval"][0] > 0
    status = "evidence_attached" if primary_pass and all_kills_pass else "orthogonal_phenotype"

    editing_rows = [row for row in rows if row["editing_efficiency_median"] is not None]
    editing = {
        "decision_role": "descriptive_only_systematically_missing_in_older_batch",
        "n": len(editing_rows),
        "batches": sorted({row["batch"] for row in editing_rows}),
        "partial_spearman_rho_without_editing_covariate": round(
            _partial_spearman(editing_rows), 6
        ),
        "partial_spearman_rho_with_editing_covariate": round(
            _partial_spearman(editing_rows, ("editing_efficiency_median",)), 6
        ),
    }

    interpretation = (
        "The sensitivity analysis attaches evidence that Stim48hr reach retains positive "
        "association after controlling for Rest reach and batch."
        if status == "evidence_attached"
        else "Broad cross-study perturbation reach remains reproduced, but incremental "
        "activation-specific reach is not established under the locked sensitivity rule."
    )
    result_core = {
        "schema_version": "prospect.gse271788.activation_specificity.v1",
        "pre_registration_id": prereg["pre_registration_id"],
        "status": status,
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "frontier_root": "root_a8b0dcdd4024e12f",
        "claim": {
            "text": (
                "Stim48hr transcriptomic reach retains positive association with independent "
                "day-eight activated primary-CD4 knockout reach after controlling for Rest reach "
                "and independent-study batch."
            ),
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
            "comparability": "orthogonal_activation_context",
            "interpretation": interpretation,
            "contradicted_allowed": False,
        },
        "coverage": coverage,
        "primary_result": {
            "n": len(rows),
            "partial_spearman_rho": round(observed, 6),
            "permutation_p_value_one_sided": round(permutation_p, 8),
            "bootstrap_95_percent_interval": bootstrap["interval"],
            "bootstrap_discarded_singular_samples": bootstrap["discarded_singular_samples"],
            "permutations": SAMPLES,
            "bootstrap_samples": bootstrap["samples"],
            "seed": SEED,
            "passed": primary_pass,
        },
        "adversarial_kills": kills,
        "editing_efficiency_sensitivity": editing,
        "source_integrity": {
            "bindings": prereg["source_bindings"],
            "substrate_id": source_integrity["manifest"]["substrate_id"],
            "source_manifest_sha256": _sha256(source_dir / "source_manifest.json"),
        },
        "replay": "python frontier/gse271788_activation_specificity.py --check",
    }

    artifacts = [
        Artifact(PREREG.name, _sha256(PREREG), "examples/data/" + PREREG.name),
        Artifact("source_manifest.json", _sha256(source_dir / "source_manifest.json"), "examples/data/gse271788/source_manifest.json"),
        Artifact("target_reach.csv", _sha256(source_dir / "target_reach.csv"), "examples/data/gse271788/target_reach.csv"),
        Artifact("metadata_summary.json", _sha256(source_dir / "metadata_summary.json"), "examples/data/gse271788/metadata_summary.json"),
        Artifact(MARSON.name, _sha256(MARSON), "examples/data/" + MARSON.name),
        Artifact(K562.name, _sha256(K562), "examples/data/" + K562.name),
    ]
    receipt = Receipt(
        frontier="prospect_independent_cd4_activation_specificity",
        claim=result_core["claim"]["text"],
        kind="cross_study_sensitivity",
        subject=coverage["complete_case_targets"],
        producer={"kind": "deterministic_analysis", "name": "ProspectActivationSpecificityAudit"},
        artifacts=artifacts,
        evidence=[
            EvidenceAtom("complete-case perturbation targets", str(len(rows)), "frozen source join"),
            EvidenceAtom("partial Spearman rho", f"{observed:.6f}", "locked residual-rank analysis"),
            EvidenceAtom("one-sided permutation P value", f"{permutation_p:.8f}", "10000 within-batch Freedman-Lane permutations"),
            EvidenceAtom("bootstrap lower bound", f"{bootstrap['interval'][0]:.6f}", "10000 within-batch bootstrap samples"),
            EvidenceAtom("status-determining kills passed", str(sum(row["passed"] for row in kills.values())), "five frozen kill rules"),
        ],
        verifier=Verifier(
            name="ProspectActivationSpecificityAudit",
            method="frozen partial-rank analysis plus five pre-registered adversarial kills",
            replay="python frontier/gse271788_activation_specificity.py --check",
        ),
        status=status,
        replayability="exact",
        conditions=[
            "Marson Stim48hr outcome",
            "Marson Rest and independent-study batch covariates",
            "day-eight activated primary-CD4 knockout comparator",
            "orthogonal activation context",
            "proposal only",
        ],
        verification_requirements=[
            "frozen_source_hashes_match",
            "committed_pre_registration_matches",
            "locked_partial_rank_analysis_rederives",
            "human_ed25519_signature",
        ],
        state_diff={
            "accepted": False,
            "model_can_apply": False,
            "effect": "proposal_only_no_state_mutation",
            "target": "prospect_independent_cd4_activation_specificity",
        },
        replay_metadata={
            "command": "python frontier/gse271788_activation_specificity.py --check",
            "verifier": "ProspectActivationSpecificityAudit",
            "replayability": "exact",
            "pre_registration_id": prereg["pre_registration_id"],
            "ceiling": result_core["claim"]["ceiling"],
        },
    ).freeze().to_dict()
    result_core["receipt"] = receipt
    result_core["proposal_id"] = _canonical_id("proposal_", {"receipt_id": receipt["receipt_id"]})
    return result_core


def render_markdown(result: dict[str, Any]) -> str:
    primary = result["primary_result"]
    kills = result["adversarial_kills"]
    batch = kills["batch_direction"]["batches"]
    machinery = kills["general_machinery"]
    influential = kills["influential_target"]
    subset = kills["subset_instability"]
    cell_count = kills["cell_count_confound"]
    editing = result["editing_efficiency_sensitivity"]
    kill_label = lambda value: "pass" if value else "fail"
    return f"""# Activation-specificity sensitivity audit

Status: `{result['status']}`
Accepted: `false`
Proposal: `{result['proposal_id']}`
Receipt: `{result['receipt']['receipt_id']}`
Pre-registration: `{result['pre_registration_id']}`

## Result

Across {primary['n']} complete-case perturbation targets, the partial Spearman association between
Marson `Stim48hr` reach and independent day-eight activated primary-CD4 knockout reach is
{primary['partial_spearman_rho']:.6f} after controlling for Marson `Rest` reach and study batch.
The one-sided 10,000-permutation P value is {primary['permutation_p_value_one_sided']:.8f}. The
within-batch bootstrap 95 percent interval is [{primary['bootstrap_95_percent_interval'][0]:.6f},
{primary['bootstrap_95_percent_interval'][1]:.6f}].

This sensitivity is typed `{result['status']}` under pre-registration
`{result['pre_registration_id']}`. {result['claim']['interpretation']} This is computation over
released data, not wet-lab or clinical truth. The independent day-eight context is not identical to
a Marson condition, so this analysis cannot earn `contradicted`.

## Adversarial kills

| Kill | Result | Detail |
| --- | --- | --- |
| Batch direction | {kill_label(kills['batch_direction']['passed'])} | GSE171737 n={batch['gse171737_il2ra_regulators']['n']}, partial rho={batch['gse171737_il2ra_regulators']['partial_spearman_rho']:.6f}; GSE271788 n={batch['gse271788_iei_background']['n']}, partial rho={batch['gse271788_iei_background']['partial_spearman_rho']:.6f}. |
| General machinery | {kill_label(machinery['passed'])} | n={machinery['n']}, partial rho={machinery['partial_spearman_rho']:.6f}; {len(machinery['excluded_k562_above_25'])} targets above 25 excluded; {len(machinery['k562_not_assayed'])} K562 gaps retained and typed `not_assayed`. |
| Influential target | {kill_label(influential['passed'])} | Minimum leave-one-out partial rho={influential['minimum_leave_one_out']['partial_spearman_rho']:.6f} after excluding {influential['minimum_leave_one_out']['excluded_gene']}. |
| Subset instability | {kill_label(subset['passed'])} | {subset['positive_runs']} of {subset['runs']} leave-five-out runs positive; minimum={subset['minimum_partial_spearman_rho']:.6f}. |
| Cell-count confound | {kill_label(cell_count['passed'])} | n={cell_count['n']}, partial rho={cell_count['partial_spearman_rho']:.6f} after adding ranked median live-cell count. |

## Missingness and descriptive sensitivity

- Starting overlap: {result['coverage']['starting_targets']} targets.
- Complete cases: {result['coverage']['complete_cases']} targets.
- Missing condition rows: {json.dumps(result['coverage']['missing_complete_case_rows'], sort_keys=True)}.
- Editing-efficiency subset: n={editing['n']}, available batches={', '.join(editing['batches'])}.
- Editing-efficiency partial rho changes from
  {editing['partial_spearman_rho_without_editing_covariate']:.6f} to
  {editing['partial_spearman_rho_with_editing_covariate']:.6f} when ranked editing efficiency is
  added. This is descriptive only and cannot determine status.

No output changes accepted state. The signed root remains `root_a8b0dcdd4024e12f`.

## Replay

```bash
python frontier/gse271788_activation_specificity.py --check
```
"""


def write_result() -> dict[str, Any]:
    result = build_result()
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_DOC.write_text(render_markdown(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result()
    if args.check:
        if not OUT_JSON.exists() or json.loads(OUT_JSON.read_text()) != result:
            raise SystemExit("activation-specificity result drift")
        if not OUT_DOC.exists() or OUT_DOC.read_text() != render_markdown(result):
            raise SystemExit("activation-specificity document drift")
    else:
        OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        OUT_DOC.write_text(render_markdown(result))
    primary = result["primary_result"]
    print(
        f"status={result['status']} accepted=false n={primary['n']} "
        f"partial_rho={primary['partial_spearman_rho']:.6f} "
        f"p={primary['permutation_p_value_one_sided']:.8f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
