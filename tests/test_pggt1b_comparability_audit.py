"""Tests for the frozen PGGT1B comparability audit."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.pggt1b_comparability_audit import (
    ORCS_SHA256,
    ORCS_SNAPSHOT,
    OUT_DOC,
    OUT_JSON,
    build_pggt1b_comparability_audit,
)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def test_audit_keeps_pggt1b_proposal_only():
    packet = build_pggt1b_comparability_audit()

    assert packet["schema_version"] == "prospect.pggt1b_comparability_audit.v1"
    assert packet["gene"] == "PGGT1B"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["audit_id"].startswith("pggt1b_comparability_")


def test_audit_pins_exact_public_source_hashes():
    packet = build_pggt1b_comparability_audit()
    sources = {source["source_id"]: source for source in packet["source_files"]}

    assert ORCS_SNAPSHOT.exists()
    assert sources["biogrid_orcs_pggt1b_tcell_rows"]["sha256"] == ORCS_SHA256
    assert sources["biogrid_orcs_pggt1b_tcell_rows"]["bytes"] == 47826
    assert sources["shifrut_gse119450_d1_no_stim_guide_assignments"]["sha256"] == (
        "5a64ffdc48c03466f30d6734112e671626f1cf77e12f140b3308c6a3bc3e663d"
    )
    assert sources["schmidt_gse190604_guide_calls"]["sha256"] == (
        "0ffd5a3050a69d013ddc09a43fae63642a7659cdb778f78c865e0829207e17b7c"
    )


def test_nonmatching_screen_readouts_remain_orthogonal():
    packet = build_pggt1b_comparability_audit()
    studies = {study["study_id"]: study for study in packet["studies"]}

    shifrut = studies["shifrut_2018"]["genome_wide_screens"]
    assert [(row["screen_id"], row["hit_status"], row["rank"], row["total"]) for row in shifrut] == [
        ("1107", "hit", 1095, 19108),
        ("1109", "non_hit", 18667, 19089),
    ]
    schmidt = studies["schmidt_2022"]["genome_wide_screens"]
    assert [(row["screen_id"], row["rank"], row["total"]) for row in schmidt] == [
        ("2423", 8935, 18920),
        ("2424", 18016, 18900),
        ("2427", 4529, 18894),
    ]
    assert all(row["typed_status"] == "orthogonal_phenotype" for row in shifrut + schmidt)
    assert all(row["comparability"] == "nonmatching_readout" for row in shifrut + schmidt)


def test_transcriptomic_target_manifests_type_pggt1b_not_assayed():
    packet = build_pggt1b_comparability_audit()
    studies = {study["study_id"]: study for study in packet["studies"]}

    shifrut = studies["shifrut_2018"]["transcriptomic_panel"]
    assert shifrut["guide_count"] == 48
    assert shifrut["gene_target_count"] == 20
    assert shifrut["non_targeting_control_count"] == 8
    assert shifrut["pggt1b_targeted"] is False
    assert "PGGT1B" not in shifrut["gene_targets"]
    assert shifrut["typed_status"] == "not_assayed"

    schmidt = studies["schmidt_2022"]["transcriptomic_panel"]
    assert schmidt["target_label_count_in_public_guide_calls"] == 74
    assert schmidt["gene_target_count"] == 73
    assert schmidt["control_target_labels"] == ["NO-TARGET"]
    assert schmidt["pggt1b_targeted"] is False
    assert "PGGT1B" not in schmidt["gene_targets"]
    assert schmidt["typed_status"] == "not_assayed"


def test_audit_records_no_comparable_reproduction_and_stop_rule():
    packet = build_pggt1b_comparability_audit()
    determination = packet["determination"]
    stop = packet["stop_criteria"]

    assert determination["comparable_pggt1b_transcriptomic_reproduction_found"] is False
    assert determination["batch_or_dataset_specificity_kill"] == "not_cleared"
    assert determination["status_after_audit"] == "evidence_attached"
    assert stop["action"] == "stop_public_search_and_retain_evidence_attached"
    assert len(stop["resume_only_if_one_accession_meets_all"]) == 7
    assert "direct PGGT1B loss-of-function with guide identity and on-target evidence" in (
        stop["resume_only_if_one_accession_meets_all"]
    )
    assert "cytokine abundance alone" in stop["nonqualifying_readouts"]


def test_committed_artifacts_are_deterministic_and_clean():
    packet = build_pggt1b_comparability_audit()
    committed = json.loads(OUT_JSON.read_text())
    doc = OUT_DOC.read_text()
    text = "\n".join(_strings(packet)) + "\n" + doc

    assert committed == packet
    assert "No independent public dataset in this audit directly perturbs PGGT1B" in doc
    assert "rank 1095 of 19108" in doc
    assert "PGGT1B absent from 20-gene target manifest" in doc
    assert "PGGT1B absent from 73-gene target manifest" in doc
    assert "\u2014" not in text
    assert '"typed_status": "true"' not in OUT_JSON.read_text().lower()
    assert ("Ve" + "la") not in text
    assert ("Constel" + "late") not in text
    assert ("veri" + "fied") not in text.lower()
    assert ("tr" + "ue") not in text.lower()


def test_standalone_check_command_passes():
    proc = subprocess.run(
        [sys.executable, "frontier/pggt1b_comparability_audit.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 0, proc.stderr
    assert "pggt1b_comparability_audit.json" in proc.stdout
