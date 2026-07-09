"""Proposal-only GSE278572 comparator for Prospect Finding 3.

The comparator re-derives a narrow corrective result from frozen projections of
the authors' reduced Zenodo tables. It does not mutate the signed frontier.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
SOURCE_DIR = DATA / "gse278572"
OUT_JSON = DATA / "gse278572_comparator.json"

STATUS = "evidence_attached"
REST_HIGH_DE = 1000
ACTIVATION_PADJ_MAX = 0.01
MIN_PSEUDOBULK_DE_EXCLUSIVE = 10

EXPECTED_HASHES = {
    "activation_scores.csv": "39c89339d5fe09561714c4ee4c09e3b6c2c2c48fd8dd919f9b17a7b7ea3e0b9b",
    "pseudobulk_de.csv": "0fce9262a55bf97b5e8452208699421767cb0ce68a0a81aed9a00e24df97fd03",
    "metadata_summary.json": "4ef02c8ee15e68e5f92fb33b6b0f1babd05e77f9b5c1f3e71cd9152ccc76a0b7",
}
EXPECTED_SOURCE_HASHES = {
    "archive": "dc9e2efb04d24f1a6d4b8db6a8b1d5cd01c935777c3740088be339de5b5062b4",
    "barcodes": "0c26723009bb4e507437c49ba92e382506f676c8e3c1ba19245db1208a2514b7",
    "S8": "90c58844937d744465c6de4f3306c9b37c01983a72a6c1e816df1b7d7907ee57",
    "S9": "962a17eefae7f720af2207f0d55065ab27f4f84e0abe6a2977fbb4e5f0ed7308",
    "S14": "ee33fc765234e073aaac9bf394ea067df63f196c22bb6c7b6dbbead09ee2343b",
}
EXPECTED_CONTEXTS = (
    "Resting-Teff",
    "Resting-Treg",
    "Stimulated-Teff",
    "Stimulated-Treg",
)


class DataConstraintError(RuntimeError):
    """Raised when a frozen source or pre-registered data constraint fails."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise DataConstraintError(f"{label}: expected {expected!r}, found {actual!r}")


def validate_frozen_inputs(source_dir: Path = SOURCE_DIR) -> dict[str, Any]:
    """Validate hashes, schemas, cardinalities, and the GEO barcode linkage summary."""
    manifest_path = source_dir / "source_manifest.json"
    if not manifest_path.exists():
        raise DataConstraintError(f"missing source manifest: {manifest_path}")
    manifest = _read_json(manifest_path)

    _assert_equal(
        manifest["sources"]["zenodo_archive"]["sha256"],
        EXPECTED_SOURCE_HASHES["archive"],
        "Zenodo archive sha256",
    )
    _assert_equal(
        manifest["sources"]["geo_barcodes"]["sha256"],
        EXPECTED_SOURCE_HASHES["barcodes"],
        "GEO barcode sha256",
    )
    for table in ("S8", "S9", "S14"):
        _assert_equal(
            manifest["source_tables"][table]["sha256"],
            EXPECTED_SOURCE_HASHES[table],
            f"{table} source sha256",
        )

    for filename, expected_hash in EXPECTED_HASHES.items():
        path = source_dir / filename
        if not path.exists():
            raise DataConstraintError(f"missing frozen projection: {path}")
        _assert_equal(_sha256(path), expected_hash, f"{filename} sha256")
        _assert_equal(
            manifest["frozen_projections"][filename]["sha256"],
            expected_hash,
            f"manifest hash for {filename}",
        )

    activation = _read_csv(source_dir / "activation_scores.csv")
    pseudobulk = _read_csv(source_dir / "pseudobulk_de.csv")
    metadata = _read_json(source_dir / "metadata_summary.json")

    _assert_equal(len(activation), 116, "S8 projection row count")
    activation_keys = {(row["sg_target"], row["context"]) for row in activation}
    _assert_equal(len(activation_keys), 116, "S8 target-context uniqueness")
    _assert_equal(
        sorted({row["context"] for row in activation}),
        list(EXPECTED_CONTEXTS),
        "S8 contexts",
    )
    _assert_equal(len({row["sg_target"] for row in activation}), 29, "S8 target labels")

    _assert_equal(len(pseudobulk), 705, "S9 projection row count")
    if any(float(row["padj"]) >= 0.05 for row in pseudobulk):
        raise DataConstraintError("S9 projection contains a row with padj >= 0.05")

    _assert_equal(metadata["n_cells"], 100087, "S14 cell count")
    _assert_equal(metadata["n_unique_cells"], 100087, "S14 unique cell count")
    _assert_equal(metadata["n_donors"], 2, "S14 donor count")
    _assert_equal(metadata["n_contexts"], 4, "S14 context count")
    _assert_equal(metadata["n_target_labels"], 29, "S14 target labels")
    _assert_equal(metadata["n_perturbation_targets"], 28, "S14 perturbation targets")
    _assert_equal(metadata["n_guides"], 65, "S14 guide count")
    _assert_equal(metadata["n_non_targeting_guides"], 9, "S14 non-targeting guides")
    _assert_equal(metadata["n_target_context_pairs"], 116, "S14 target-context pairs")
    _assert_equal(metadata["all_cells_singlet"], True, "S14 singlet filter")
    _assert_equal(
        metadata["geo_barcode_linkage"]["n_s14_cells_missing"],
        0,
        "S14 cells missing from GEO barcodes",
    )
    return {"manifest": manifest, "metadata": metadata}


def _condition_de(node: dict[str, Any], condition: str) -> int:
    return int(node.get("conditions", {}).get(condition, {}).get("n_de", 0))


def _rank(values: Iterable[float]) -> list[float]:
    values = list(values)
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average = (start + 1 + end) / 2.0
        for index in order[start:end]:
            ranks[index] = average
        start = end
    return ranks


def _spearman(left: list[int], right: list[int]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise DataConstraintError("Spearman inputs must have equal length greater than one")
    x = _rank(left)
    y = _rank(right)
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    x_scale = math.sqrt(sum((a - x_mean) ** 2 for a in x))
    y_scale = math.sqrt(sum((b - y_mean) ** 2 for b in y))
    if not x_scale or not y_scale:
        raise DataConstraintError("Spearman input is constant")
    return numerator / (x_scale * y_scale)


def _canonical_id(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return "proposal_" + hashlib.sha256(encoded).hexdigest()[:16]


def _activation_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    by_target: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_target.setdefault(row["sg_target"], {})[row["context"]] = row
    return by_target


def _pseudobulk_counts(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], int]:
    counts: dict[tuple[str, str, str], int] = {}
    for row in rows:
        key = (row["KO"], row["cell_type"], row["stimulation"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def _lineage_rule(
    target_rows: dict[str, dict[str, str]],
    counts: dict[tuple[str, str, str], int],
    gene: str,
    lineage: str,
) -> dict[str, Any]:
    rest = target_rows[f"Resting-{lineage}"]
    stimulated = target_rows[f"Stimulated-{lineage}"]
    rest_delta = float(rest["median_delta_vs_control"])
    stimulated_delta = float(stimulated["median_delta_vs_control"])
    rest_padj = float(rest["padj"])
    stimulated_padj = float(stimulated["padj"])
    rest_de = counts.get((gene, lineage, "Resting"), 0)
    stimulated_de = counts.get((gene, lineage, "Stimulated"), 0)
    significant_both = rest_padj < ACTIVATION_PADJ_MAX and stimulated_padj < ACTIVATION_PADJ_MAX
    opposite_direction = rest_delta * stimulated_delta < 0
    transcriptome_breadth = (
        rest_de > MIN_PSEUDOBULK_DE_EXCLUSIVE
        and stimulated_de > MIN_PSEUDOBULK_DE_EXCLUSIVE
    )
    return {
        "lineage": lineage,
        "rest_median_delta_vs_control": round(rest_delta, 6),
        "stimulated_median_delta_vs_control": round(stimulated_delta, 6),
        "rest_padj": float(f"{rest_padj:.8g}"),
        "stimulated_padj": float(f"{stimulated_padj:.8g}"),
        "rest_pseudobulk_de": rest_de,
        "stimulated_pseudobulk_de": stimulated_de,
        "significant_both": significant_both,
        "opposite_direction": opposite_direction,
        "more_than_10_de_both": transcriptome_breadth,
        "qualifies_interpretation": significant_both and opposite_direction and transcriptome_breadth,
    }


def build_comparator(
    source_dir: Path = SOURCE_DIR,
    backbone_path: Path = DATA / "atlas_backbone.json",
) -> dict[str, Any]:
    integrity = validate_frozen_inputs(source_dir)
    activation_rows = _read_csv(source_dir / "activation_scores.csv")
    pseudobulk_rows = _read_csv(source_dir / "pseudobulk_de.csv")
    activation = _activation_rows(activation_rows)
    counts = _pseudobulk_counts(pseudobulk_rows)
    backbone = {node["gene"]: node for node in json.loads(backbone_path.read_text())}
    _assert_equal(len(backbone), 11526, "Prospect backbone gene count")

    source_targets = sorted(set(activation) - {"Non-Targeting"})
    overlap = sorted(set(source_targets) & set(backbone))
    not_in_backbone = sorted(set(source_targets) - set(backbone))
    _assert_equal(len(source_targets), 28, "GSE278572 perturbation targets")
    _assert_equal(len(overlap), 24, "GSE278572 and Prospect overlap")

    per_gene: list[dict[str, Any]] = []
    for gene in overlap:
        rules = [_lineage_rule(activation[gene], counts, gene, lineage) for lineage in ("Teff", "Treg")]
        rest_de = _condition_de(backbone[gene], "Rest")
        current_high_rest = rest_de > REST_HIGH_DE
        qualifying_lineages = [row["lineage"] for row in rules if row["qualifies_interpretation"]]
        per_gene.append(
            {
                "gene": gene,
                "prospect_rest_de": rest_de,
                "prospect_stim48hr_de": _condition_de(backbone[gene], "Stim48hr"),
                "current_high_rest_label": current_high_rest,
                "lineages": rules,
                "finding3_assessment": (
                    "needs_qualification"
                    if current_high_rest and qualifying_lineages
                    else "does_not_meet_qualification_rule"
                    if current_high_rest
                    else "not_in_high_rest_scope"
                ),
                "qualifying_lineages": qualifying_lineages,
            }
        )

    high_rest = [row for row in per_gene if row["current_high_rest_label"]]
    qualified = [row["gene"] for row in high_rest if row["finding3_assessment"] == "needs_qualification"]
    not_qualified = [
        row["gene"] for row in high_rest if row["finding3_assessment"] == "does_not_meet_qualification_rule"
    ]

    rest_left = [row["prospect_rest_de"] for row in per_gene]
    rest_right = [counts.get((row["gene"], "Teff", "Resting"), 0) for row in per_gene]
    stim_left = [row["prospect_stim48hr_de"] for row in per_gene]
    stim_right = [counts.get((row["gene"], "Teff", "Stimulated"), 0) for row in per_gene]

    body: dict[str, Any] = {
        "schema_version": "prospect.gse278572.comparator.v1",
        "status": STATUS,
        "accepted": False,
        "next": "human_review_required",
        "trust_boundary": "proposal_only",
        "claim": {
            "current_interpretation": (
                "High transcriptional reach at Rest identifies housekeeping or essentiality artifacts."
            ),
            "corrective_interpretation": (
                "High Rest reach identifies broad, context-spanning regulators and general machinery. "
                "It is evidence against activation specificity, but is not sufficient by itself to "
                "label a gene housekeeping or an essentiality artifact. MED12 is the inspected exception."
            ),
            "ceiling": (
                "Computation over released data, not wet-lab or clinical truth. This proposal does not "
                "change the signed frontier."
            ),
        },
        "pre_registered_rule": {
            "activation_padj_lt": ACTIVATION_PADJ_MAX,
            "activation_effect": "median activation-score delta against same-context non-targeting control",
            "direction_test": "opposite delta signs between Resting and Stimulated in the same lineage",
            "pseudobulk_de_requirement": "more than 10 published significant DE genes in both states",
            "missing_s9_rule": (
                "count as zero only when S8 and S14 establish target-context coverage"
            ),
            "inspected_positive_control": "MED12",
        },
        "source_integrity": {
            "zenodo_archive_sha256": EXPECTED_SOURCE_HASHES["archive"],
            "geo_barcodes_sha256": EXPECTED_SOURCE_HASHES["barcodes"],
            "s8_rows": 116,
            "s9_rows": 705,
            "s14_cells": integrity["metadata"]["n_cells"],
            "s14_cells_missing_from_geo": integrity["metadata"]["geo_barcode_linkage"]["n_s14_cells_missing"],
        },
        "comparison": {
            "source_perturbation_targets": len(source_targets),
            "prospect_overlap": len(overlap),
            "overlap_genes": overlap,
            "not_in_prospect_backbone": not_in_backbone,
            "matched_conditions": {
                "Resting-Teff": "Prospect Rest",
                "Stimulated-Teff": "Prospect Stim48hr",
                "Treg": "informative extension, not an exact Prospect match",
            },
            "rank_agreement": {
                "resting_teff_vs_prospect_rest": {
                    "n": len(overlap),
                    "spearman_rho": round(_spearman(rest_left, rest_right), 6),
                },
                "stimulated_teff_vs_prospect_stim48hr": {
                    "n": len(overlap),
                    "spearman_rho": round(_spearman(stim_left, stim_right), 6),
                },
            },
        },
        "finding3_review": {
            "high_rest_genes_in_overlap": [row["gene"] for row in high_rest],
            "n_high_rest_genes_in_overlap": len(high_rest),
            "needs_qualification": qualified,
            "n_needs_qualification": len(qualified),
            "does_not_meet_qualification_rule": not_qualified,
            "decision": (
                "Qualify the interpretation for MED12. Preserve the measured high Rest reach, but do "
                "not infer housekeeping or essentiality from that measurement alone."
            ),
        },
        "per_gene": per_gene,
        "replay": "python frontier/gse278572_comparator.py --check",
    }
    return {"proposal_id": _canonical_id(body), **body}


def write_comparator(out_path: Path = OUT_JSON) -> dict[str, Any]:
    result = build_comparator()
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def check_comparator(out_path: Path = OUT_JSON) -> dict[str, Any]:
    expected = build_comparator()
    if not out_path.exists():
        raise DataConstraintError(f"missing comparator artifact: {out_path}")
    actual = _read_json(out_path)
    if actual != expected:
        raise DataConstraintError(f"comparator drift: regenerate {out_path}")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="re-derive and compare the committed artifact")
    args = parser.parse_args()
    result = check_comparator() if args.check else write_comparator()
    print(
        f"{result['proposal_id']} status={result['status']} accepted={str(result['accepted']).lower()} "
        f"overlap={result['comparison']['prospect_overlap']} "
        f"needs_qualification={result['finding3_review']['n_needs_qualification']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
