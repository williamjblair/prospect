"""Tests for the frozen independent primary-CD4 calibration."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gse271788_calibration import (
    DATA,
    EXPECTED_SOURCE_HASHES,
    OUT_DOC,
    OUT_JSON,
    SOURCE_DIR,
    DataConstraintError,
    build_calibration,
    render_markdown,
    validate_frozen_inputs,
)


def test_source_manifest_and_cardinalities_are_pinned():
    validated = validate_frozen_inputs()
    manifest = validated["manifest"]
    metadata = validated["metadata"]

    assert manifest["schema_version"] == "prospect.substrate_manifest.v1"
    assert manifest["substrate_id"] == "weinstock_freimer_activated_cd4_ko"
    assert manifest["comparability"] == "orthogonal_activation_context"
    assert manifest["missing_semantics"] == "not_assayed"
    assert {name: row["sha256"] for name, row in manifest["sources"].items()} == EXPECTED_SOURCE_HASHES
    assert metadata["count_columns"] == 311
    assert metadata["targets"] == 84
    assert metadata["donors_per_target"] == 3
    assert metadata["mashr_rows_lfsr_lt_0_005"] == 226763
    assert metadata["deseq2_rows"] == 129727
    assert metadata["editing_efficiency_rows"] == 212
    assert metadata["live_cell_count_rows"] == 310
    assert metadata["marson_overlap"] == 79
    assert metadata["marson_not_assayed"] == ["JAK3", "POU2F1", "SON", "ZNF217", "ZNF341"]


def test_primary_result_and_all_three_kills_rederive():
    result = build_calibration()
    primary = result["primary_result"]
    kills = result["adversarial_kills"]

    assert result["status"] == "evidence_attached"
    assert result["accepted"] is False
    assert primary["n"] == 79
    assert primary["spearman_rho"] == 0.373895
    assert primary["permutation_p_value_one_sided"] == 0.00039996
    assert primary["passed"] is True
    assert set(kills) == {"batch_specificity", "general_machinery", "influential_target"}
    assert all(row["passed"] is True for row in kills.values())
    assert kills["batch_specificity"]["batches"]["gse171737_il2ra_regulators"] == {
        "n": 22,
        "spearman_rho": 0.233267,
    }
    assert kills["batch_specificity"]["batches"]["gse271788_iei_background"] == {
        "n": 57,
        "spearman_rho": 0.132866,
    }
    assert kills["general_machinery"]["n"] == 59
    assert kills["general_machinery"]["spearman_rho"] == 0.282219
    assert kills["general_machinery"]["k562_not_assayed"] == ["IL2RA", "TNFAIP3"]
    assert kills["influential_target"]["minimum_leave_one_out"] == {
        "excluded_gene": "MED12",
        "spearman_rho": 0.352218,
    }


def test_descriptive_results_and_on_target_sensitivity_are_separate():
    result = build_calibration()

    assert result["descriptive_results"] == {
        "Rest": {"n": 76, "spearman_rho": 0.43627},
        "Stim48hr": {"n": 79, "spearman_rho": 0.373895},
        "Stim8hr": {"n": 79, "spearman_rho": 0.460262},
        "strongest_condition": {"n": 79, "spearman_rho": 0.504072},
    }
    assert result["on_target_sensitivity"] == {
        "decision_role": "descriptive_only_not_pre_registered_primary",
        "n": 60,
        "spearman_rho": 0.528999,
    }
    assert result["claim"]["comparability"] == "orthogonal_activation_context"
    assert "cannot earn contradicted" in result["claim"]["interpretation"]


def test_receipt_binds_sources_and_keeps_state_pending():
    result = build_calibration()
    receipt = result["receipt"]

    assert receipt["schema_version"] == "prospect.receipt.v1"
    assert receipt["status"] == "evidence_attached"
    assert receipt["accepted"] is False
    assert receipt["state_diff"]["accepted"] is False
    assert receipt["state_diff"]["model_can_apply"] is False
    assert receipt["verification_requirements"][-1] == "human_ed25519_signature"
    assert {row["name"] for row in receipt["artifacts"]} >= {
        "gse271788_preregistration.json",
        "target_reach.csv",
        "metadata_summary.json",
        "source_manifest.json",
        "marson_de_full.csv",
        "replogle_k562_de.csv",
    }


def test_tampered_projection_fails_closed(tmp_path):
    copied = tmp_path / "gse271788"
    shutil.copytree(SOURCE_DIR, copied)
    path = copied / "target_reach.csv"
    path.write_text(path.read_text().replace("MED12", "MED13", 1))

    with pytest.raises(DataConstraintError, match="projection hash drift"):
        validate_frozen_inputs(copied)


def test_committed_outputs_have_zero_drift_and_check_command_passes():
    result = build_calibration()

    assert json.loads(OUT_JSON.read_text()) == result
    assert OUT_DOC.read_text() == render_markdown(result)
    proc = subprocess.run(
        [sys.executable, "frontier/gse271788_calibration.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "status=evidence_attached accepted=false n=79" in proc.stdout


def test_owned_artifacts_keep_copy_discipline():
    paths = [
        ROOT / "frontier" / "gse271788_calibration.py",
        ROOT / "tests" / "test_gse271788_calibration.py",
        OUT_DOC,
        OUT_JSON,
        *(SOURCE_DIR.glob("*")),
    ]
    combined = "\n".join(path.read_text(errors="ignore") for path in paths if path.exists())
    assert "\N{EM DASH}" not in combined
    lowered = combined.lower()
    forbidden = ("ve" + "la", "constel" + "late", "car" + "ina")
    assert not any(term in lowered for term in forbidden)
