"""Tests for the sealed activation-specificity sensitivity analysis."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gse271788_activation_specificity import (
    EXPECTED_PREREG_ID,
    OUT_DOC,
    OUT_JSON,
    PREREG,
    SOURCE_DIR,
    DataConstraintError,
    _canonical_prereg_id,
    build_result,
    render_markdown,
    validate_preregistration,
)
from receipt.schema import receipt_id_for


@pytest.fixture(scope="module")
def result():
    return build_result()


def test_pre_registration_is_content_addressed_and_source_bound():
    prereg = validate_preregistration()

    assert prereg["pre_registration_id"] == EXPECTED_PREREG_ID
    assert _canonical_prereg_id(prereg) == EXPECTED_PREREG_ID
    assert prereg["accepted"] is False
    assert prereg["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert len(prereg["source_bindings"]) == 6
    assert len(prereg["kill_rules"]) == 5
    assert all(row["status_determining"] is True for row in prereg["kill_rules"])


def test_locked_primary_result_does_not_earn_activation_specificity(result):
    primary = result["primary_result"]

    assert result["status"] == "orthogonal_phenotype"
    assert result["accepted"] is False
    assert result["next"] == "human_signature_required"
    assert result["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert primary == {
        "n": 76,
        "partial_spearman_rho": 0.045808,
        "permutation_p_value_one_sided": 0.35246475,
        "bootstrap_95_percent_interval": [-0.166003, 0.260058],
        "bootstrap_discarded_singular_samples": 0,
        "permutations": 10000,
        "bootstrap_samples": 10000,
        "seed": 271789,
        "passed": False,
    }
    assert "incremental activation-specific reach is not established" in result["claim"]["interpretation"]
    assert result["claim"]["contradicted_allowed"] is False


def test_all_five_kills_rederive_with_exact_failure_modes(result):
    kills = result["adversarial_kills"]

    assert set(kills) == {
        "batch_direction",
        "general_machinery",
        "influential_target",
        "subset_instability",
        "cell_count_confound",
    }
    assert kills["batch_direction"] == {
        "passed": False,
        "batches": {
            "gse171737_il2ra_regulators": {"n": 21, "partial_spearman_rho": 0.107485},
            "gse271788_iei_background": {"n": 55, "partial_spearman_rho": -0.023537},
        },
    }
    assert kills["general_machinery"]["passed"] is False
    assert kills["general_machinery"]["n"] == 58
    assert kills["general_machinery"]["partial_spearman_rho"] == -0.07209
    assert kills["general_machinery"]["k562_not_assayed"] == ["IL2RA", "TNFAIP3"]
    assert len(kills["general_machinery"]["excluded_k562_above_25"]) == 18
    assert kills["influential_target"]["minimum_leave_one_out"] == {
        "excluded_gene": "RBCK1",
        "partial_spearman_rho": -0.010307,
    }
    assert kills["influential_target"]["passed"] is False
    assert kills["subset_instability"]["positive_runs"] == 9362
    assert kills["subset_instability"]["positive_fraction"] == 0.9362
    assert kills["subset_instability"]["passed"] is False
    assert kills["cell_count_confound"] == {
        "passed": True,
        "n": 76,
        "partial_spearman_rho": 0.055116,
        "covariate": "ranked median live-cell count",
    }


def test_missing_rows_and_editing_efficiency_stay_explicit(result):
    assert result["coverage"]["starting_targets"] == 79
    assert result["coverage"]["complete_cases"] == 76
    assert result["coverage"]["missing_complete_case_rows"] == [
        {"gene": "BCL11B", "missing_conditions": ["Rest"]},
        {"gene": "KMT2A", "missing_conditions": ["Rest"]},
        {"gene": "SREBF1", "missing_conditions": ["Rest"]},
    ]
    assert result["editing_efficiency_sensitivity"] == {
        "decision_role": "descriptive_only_systematically_missing_in_older_batch",
        "n": 55,
        "batches": ["gse271788_iei_background"],
        "partial_spearman_rho_without_editing_covariate": -0.023537,
        "partial_spearman_rho_with_editing_covariate": -0.016593,
    }


def test_receipt_binds_result_and_stays_proposal_only(result):
    receipt = result["receipt"]

    assert receipt["schema_version"] == "prospect.receipt.v1"
    assert receipt["status"] == "orthogonal_phenotype"
    assert receipt["accepted"] is False
    assert receipt["state_diff"]["accepted"] is False
    assert receipt["state_diff"]["model_can_apply"] is False
    assert receipt["verification_requirements"][-1] == "human_ed25519_signature"
    assert receipt_id_for(receipt) == receipt["receipt_id"]

    mutated = copy.deepcopy(receipt)
    mutated["claim"] += " changed"
    assert receipt_id_for(mutated) != receipt["receipt_id"]


def test_tampered_projection_fails_closed(tmp_path):
    copied = tmp_path / "gse271788"
    shutil.copytree(SOURCE_DIR, copied)
    path = copied / "target_reach.csv"
    path.write_text(path.read_text().replace("MED12", "MED13", 1))

    with pytest.raises(DataConstraintError, match="projection hash drift"):
        build_result(copied)


def test_committed_outputs_have_zero_drift_and_check_command_passes(result):
    assert json.loads(OUT_JSON.read_text()) == result
    assert OUT_DOC.read_text() == render_markdown(result)
    proc = subprocess.run(
        [sys.executable, "frontier/gse271788_activation_specificity.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "status=orthogonal_phenotype accepted=false n=76" in proc.stdout


def test_owned_artifacts_keep_copy_discipline():
    paths = [
        ROOT / "frontier" / "gse271788_activation_specificity.py",
        ROOT / "tests" / "test_gse271788_activation_specificity.py",
        PREREG,
        OUT_JSON,
        OUT_DOC,
        ROOT / "docs" / "GSE271788_ACTIVATION_SPECIFICITY_PREREGISTRATION.md",
    ]
    combined = "\n".join(path.read_text(errors="ignore") for path in paths)
    assert "\N{EM DASH}" not in combined
    lowered = combined.lower()
    forbidden = ("ve" + "la", "constel" + "late", "car" + "ina")
    assert not any(term in lowered for term in forbidden)
