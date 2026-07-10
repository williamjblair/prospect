"""Tests for the sealed GSE271788 and GSE171737 calibration rules."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.gse271788_preregistration import (
    OUT_DOC,
    OUT_JSON,
    RAW_COUNTS_SHA256,
    build_preregistration,
    render_markdown,
)


def test_preregistration_locks_source_and_analysis_contract():
    packet = build_preregistration()
    source = packet["source_contract"]
    analysis = packet["primary_analysis"]

    assert packet["accepted"] is False
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert source["raw_counts_sha256"] == RAW_COUNTS_SHA256
    assert source["expected_count_columns"] == 311
    assert source["expected_targets"] == 84
    assert source["expected_donors_per_target"] == 3
    assert source["expected_marson_overlap"] == 79
    assert source["expected_not_assayed"] == 5
    assert source["missing_row_semantics"] == "not_assayed"
    assert analysis["decision_condition"] == "Stim48hr"
    assert analysis["permutations"] == 10000
    assert analysis["bootstrap_samples"] == 10000
    assert analysis["seed"] == 271788


def test_preregistration_locks_three_independent_kills_and_typing():
    packet = build_preregistration()

    assert [row["kill_id"] for row in packet["kill_rules"]] == [
        "batch_specificity",
        "general_machinery",
        "influential_target",
    ]
    assert packet["comparability"]["contradicted_allowed"] is False
    assert packet["typing_rule"]["orthogonal_phenotype"]
    assert packet["typing_rule"]["not_assayed"]
    assert "may change" in packet["goalpost_policy"]


def test_committed_preregistration_has_zero_drift():
    packet = build_preregistration()

    assert json.loads(OUT_JSON.read_text()) == packet
    assert OUT_DOC.read_text() == render_markdown(packet)


def test_preregistration_check_command_and_copy_discipline():
    proc = subprocess.run(
        [sys.executable, "frontier/gse271788_preregistration.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "accepted=false" in proc.stdout

    combined = "\n".join(
        [
            (ROOT / "frontier" / "gse271788_preregistration.py").read_text(),
            (ROOT / "tests" / "test_gse271788_preregistration.py").read_text(),
            OUT_DOC.read_text(),
            OUT_JSON.read_text(),
        ]
    )
    assert "\N{EM DASH}" not in combined
    lowered = combined.lower()
    forbidden = ("ve" + "la", "constel" + "late", "car" + "ina")
    assert not any(term in lowered for term in forbidden)
