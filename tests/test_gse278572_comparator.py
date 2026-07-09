"""Tests for the proposal-only GSE278572 corrective comparator."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gse278572_comparator import (
    DATA,
    EXPECTED_HASHES,
    EXPECTED_SOURCE_HASHES,
    SOURCE_DIR,
    DataConstraintError,
    build_comparator,
    validate_frozen_inputs,
)


def test_source_manifest_and_cardinalities_are_pinned():
    validated = validate_frozen_inputs()
    manifest = validated["manifest"]
    metadata = validated["metadata"]

    assert manifest["sources"]["zenodo_archive"]["sha256"] == EXPECTED_SOURCE_HASHES["archive"]
    assert manifest["sources"]["geo_barcodes"]["sha256"] == EXPECTED_SOURCE_HASHES["barcodes"]
    assert manifest["source_tables"]["S8"]["rows"] == 116
    assert manifest["source_tables"]["S9"]["rows"] == 705
    assert manifest["source_tables"]["S14"]["rows"] == 100087
    assert metadata["n_cells"] == 100087
    assert metadata["n_donors"] == 2
    assert metadata["n_contexts"] == 4
    assert metadata["n_perturbation_targets"] == 28
    assert metadata["n_guides"] == 65
    assert metadata["n_non_targeting_guides"] == 9
    assert metadata["geo_barcode_linkage"]["n_geo_barcodes"] == 249799
    assert metadata["geo_barcode_linkage"]["n_s14_cells_matched"] == 100087
    assert metadata["geo_barcode_linkage"]["n_s14_cells_missing"] == 0


def test_source_projection_hashes_are_exact():
    manifest = json.loads((SOURCE_DIR / "source_manifest.json").read_text())
    for filename, expected in EXPECTED_HASHES.items():
        assert manifest["frozen_projections"][filename]["sha256"] == expected


def test_comparator_has_exact_target_overlap():
    result = build_comparator()
    comparison = result["comparison"]

    assert comparison["source_perturbation_targets"] == 28
    assert comparison["prospect_overlap"] == 24
    assert comparison["not_in_prospect_backbone"] == ["DNMT1", "MED11", "PRDM1", "ZNF217"]
    assert "MED12" in comparison["overlap_genes"]


def test_med12_is_the_only_locked_rule_qualification():
    result = build_comparator()
    review = result["finding3_review"]
    med12 = next(row for row in result["per_gene"] if row["gene"] == "MED12")

    assert review["high_rest_genes_in_overlap"] == ["FOXO1", "MED12", "MED24", "MYB", "STAT5B", "USP22"]
    assert review["needs_qualification"] == ["MED12"]
    assert review["does_not_meet_qualification_rule"] == ["FOXO1", "MED24", "MYB", "STAT5B", "USP22"]
    assert med12["prospect_rest_de"] == 2843
    assert med12["prospect_stim48hr_de"] == 2046
    assert med12["finding3_assessment"] == "needs_qualification"
    assert med12["qualifying_lineages"] == ["Teff", "Treg"]

    teff = next(row for row in med12["lineages"] if row["lineage"] == "Teff")
    assert teff["rest_median_delta_vs_control"] == 97.132305
    assert teff["stimulated_median_delta_vs_control"] == -70.261674
    assert teff["rest_pseudobulk_de"] == 28
    assert teff["stimulated_pseudobulk_de"] == 50
    assert teff["significant_both"] is True
    assert teff["opposite_direction"] is True
    assert teff["more_than_10_de_both"] is True
    assert teff["qualifies_interpretation"] is True


def test_cross_study_rank_agreement_is_rederived():
    agreement = build_comparator()["comparison"]["rank_agreement"]

    assert agreement["resting_teff_vs_prospect_rest"] == {"n": 24, "spearman_rho": 0.456973}
    assert agreement["stimulated_teff_vs_prospect_stim48hr"] == {"n": 24, "spearman_rho": 0.644507}


def test_output_is_proposal_only_and_content_addressed():
    first = build_comparator()
    second = build_comparator()

    assert first == second
    assert first["proposal_id"].startswith("proposal_")
    assert first["status"] == "evidence_attached"
    assert first["accepted"] is False
    assert first["next"] == "human_review_required"
    assert first["trust_boundary"] == "proposal_only"
    assert "Computation over released data" in first["claim"]["ceiling"]


def test_tampered_projection_fails_closed(tmp_path):
    copied = tmp_path / "gse278572"
    shutil.copytree(SOURCE_DIR, copied)
    path = copied / "activation_scores.csv"
    path.write_text(path.read_text().replace("MED12", "MED13", 1))

    with pytest.raises(DataConstraintError, match="activation_scores.csv sha256"):
        validate_frozen_inputs(copied)


def test_committed_artifact_has_zero_drift():
    expected = build_comparator()
    actual = json.loads((DATA / "gse278572_comparator.json").read_text())
    assert actual == expected


def test_module_check_command_passes():
    proc = subprocess.run(
        [sys.executable, "frontier/gse278572_comparator.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "status=evidence_attached accepted=false overlap=24 needs_qualification=1" in proc.stdout


def test_owned_artifacts_keep_copy_discipline():
    paths = [
        ROOT / "frontier" / "gse278572_comparator.py",
        ROOT / "tests" / "test_gse278572_comparator.py",
        ROOT / "docs" / "GSE278572_COMPARATOR_PREREGISTRATION.md",
        ROOT / "docs" / "GSE278572_COMPARATOR.md",
        DATA / "gse278572_comparator.json",
        *(SOURCE_DIR.glob("*")),
    ]
    combined = "\n".join(path.read_text(errors="ignore") for path in paths if path.exists())
    lowered = combined.lower()
    assert "\N{EM DASH}" not in combined
    forbidden = ("ve" + "la", "constel" + "late", "car" + "ina")
    assert not any(term in lowered for term in forbidden)
