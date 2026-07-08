"""PGGT1B defended-evidence packet tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.pggt1b_defended_evidence import (
    SNAPSHOT_DIR,
    build_pggt1b_defended_evidence,
    write_pggt1b_defended_evidence,
)


def _string_values(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _string_values(value)


def test_pggt1b_packet_uses_only_frozen_snapshots():
    packet = build_pggt1b_defended_evidence()

    assert packet["phase"] == "rank_1_pggt1b_defended_evidence"
    assert packet["gene"] == "PGGT1B"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["pre_registration_id"] == "prereg_9f31fbf1e6c1cf10"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert packet["snapshot_dir"] == str(SNAPSHOT_DIR.relative_to(ROOT))
    assert all(row["sha256"] for row in packet["frozen_snapshots"])
    assert all((ROOT / row["path"]).exists() for row in packet["frozen_snapshots"])
    assert all(row["scored_from_frozen_snapshot"] is True for row in packet["scored_evidence"])


def test_pggt1b_packet_keeps_support_and_gaps_separate():
    packet = build_pggt1b_defended_evidence()
    evidence = {row["source"]: row for row in packet["scored_evidence"]}
    gaps = {row["source"]: row for row in packet["unscored_or_blocked_sources"]}

    assert evidence["marson_frontier"]["status"] == "computationally_reproduced"
    assert evidence["shifrut_2018_orcs_1107"]["status"] == "evidence_attached"
    assert evidence["string_interaction_partners"]["status"] == "evidence_attached"
    assert evidence["dice_expression"]["status"] == "evidence_attached"
    assert evidence["chembl_target_and_activity"]["status"] == "evidence_attached"
    assert evidence["ensembl_homology"]["status"] == "evidence_attached"
    assert evidence["gwas_catalog_gene_lookup"]["status"] == "evidence_attached"
    assert evidence["depmap_achilles_19q2"]["status"] == "evidence_attached"
    assert evidence["depmap_achilles_19q2"]["summary"] == (
        "563 cancer cell lines, median gene effect -0.1009, 0 lines below -1"
    )
    assert evidence["carnevale_2022_orcs_1905"]["status"] == "orthogonal_phenotype"
    assert evidence["carnevale_2022_orcs_1905"]["summary"] == (
        "primary T-cell proliferation screen, PGGT1B non-hit rank 19027 of 19362"
    )
    assert evidence["schmidt_2022_orcs_2427"]["status"] == "orthogonal_phenotype"
    assert "depmap_dependency" not in gaps
    assert packet["orthogonal_public_dataset_count"] >= 5
    assert packet["access_limited_public_dataset_count"] == 0


def test_pggt1b_packet_declares_kill_results_without_accepting_state():
    packet = build_pggt1b_defended_evidence()
    kills = {row["kill_id"]: row for row in packet["kill_attempts"]}

    assert set(kills) == {
        "technical_confound",
        "essentiality_or_proliferation_artifact",
        "batch_or_dataset_specificity",
        "alternative_mechanism",
    }
    assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
    assert kills["essentiality_or_proliferation_artifact"]["result"] == "survives_current_frozen_evidence"
    assert kills["batch_or_dataset_specificity"]["result"] == "not_cleared"
    assert kills["alternative_mechanism"]["result"] == "survives_current_frozen_evidence"
    assert packet["defended_discovery_status"] == "not_cleared_full_bar"
    assert packet["next_step"] == (
        "freeze a comparable activation-transcriptome or activation-marker primary T-cell screen, "
        "or demote PGGT1B if none exists"
    )
    assert "none" == kills["essentiality_or_proliferation_artifact"]["missing"]
    assert "activation-transcriptome or activation-marker primary T-cell screen" in kills["batch_or_dataset_specificity"]["missing"]


def test_pggt1b_packet_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "pggt1b_defended_evidence.json"
    out_doc = tmp_path / "PGGT1B_DEFENDED_EVIDENCE.md"

    packet = write_pggt1b_defended_evidence(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("pggt1b_defended_")
    assert "not cleared full bar" in doc
    assert "median gene effect -0.1009" in doc
    assert "primary T-cell proliferation screen" in doc
    assert "No unscored public source remains in this packet." in doc
    assert "activation-transcriptome or activation-marker primary T-cell screen" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_pggt1b_defended_evidence_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "pggt1b-defended-evidence"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "pggt1b_defended_evidence.json" in proc.stdout
