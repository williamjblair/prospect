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


def test_pggt1b_packet_downgrades_novelty_against_prior_art():
    packet = build_pggt1b_defended_evidence()
    novelty = packet["novelty_assessment"]

    assert novelty["status"] == "prior_art_established_narrowed_claim"
    assert novelty["downgraded_novelty"] is True
    assert "not a first report" in novelty["plain_language"].lower()
    assert {row["pmid"] for row in novelty["citations"]} >= {
        "31302143",
        "33207246",
        "30449619",
        "36002574",
    }
    assert novelty["kept_claim"] == (
        "Prospect contributes independent released-data support that PGGT1B is a testable "
        "activation-transcriptome hypothesis in primary human CD4+ cells."
    )


def test_pggt1b_packet_has_expert_dossier_sections():
    packet = build_pggt1b_defended_evidence()

    mechanism = packet["mechanism_dossier"]
    assert "3014 stimulated DE genes" in mechanism["data_shows"][0]
    assert "prenylation-dependent small-GTPase" in mechanism["inference"][0]
    assert {"FNTA", "RABGGTA", "RAP1A", "CDC42"} <= set(mechanism["partners"])

    druggability = packet["druggability"]
    assert druggability["target_chembl_id"] == "CHEMBL4135"
    assert druggability["caveat"] == "existing compounds and activity rows, not a validated therapy"
    assert len(druggability["example_compounds"]) >= 3
    assert all(row["molecule_chembl_id"].startswith("CHEMBL") for row in druggability["example_compounds"])

    signature = packet["sade_feldman_signature_summary"]
    assert signature["genes"] == 52
    assert signature["typed_status_counts"]["evidence_attached"] == 12
    assert signature["coverage_report"]["after"]["not_assayed"] == 5


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


def test_pggt1b_wet_lab_protocol_is_runnable_and_falsifiable():
    packet = build_pggt1b_defended_evidence()
    protocol = packet["wet_lab_protocol"]

    assert protocol["system"] == "stimulated primary human CD4+ T cells"
    assert protocol["minimum_donors"] >= 3
    assert {"non_targeting_control", "PGGT1B_CRISPRi", "FNTA_or_FNTB_pathway_control", "viability_control"} <= {
        arm["id"] for arm in protocol["arms"]
    }
    assert {"PGGT1B_knockdown", "activation_transcriptome", "viability", "prenylation_or_small_GTPase_localization"} <= set(protocol["readouts"])
    assert "no candidate-specific activation-program shift" in protocol["decision_gates"]["refute"]


def test_pggt1b_packet_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "pggt1b_defended_evidence.json"
    out_doc = tmp_path / "PGGT1B_DEFENDED_EVIDENCE.md"

    packet = write_pggt1b_defended_evidence(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("pggt1b_defended_")
    assert "not cleared full bar" in doc
    assert "median gene effect -0.1009" in doc
    assert "Novelty downgrade" in doc
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
