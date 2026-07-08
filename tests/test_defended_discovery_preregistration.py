"""Pre-registration tests for the defended discovery outcome."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.defended_discovery_preregistration import (
    build_defended_discovery_preregistration,
    write_defended_discovery_preregistration,
)


def _discovery() -> dict:
    return json.loads((ROOT / "examples" / "data" / "discovery_campaign.json").read_text())


def _string_values(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _string_values(value)


def test_preregistration_freezes_ranked_candidate_order_and_bar():
    packet = build_defended_discovery_preregistration()
    discovery = _discovery()

    assert packet["phase"] == "defended_discovery_preregistration"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["candidate_set_id"] == discovery["candidate_set_id"]
    assert packet["candidate_count"] == 18
    assert [row["gene"] for row in packet["ranked_candidates"]] == [
        row["gene"] for row in discovery["candidates"]
    ]
    assert packet["ranked_candidates"][0]["gene"] == "PGGT1B"
    assert packet["ranked_candidates"][-1]["gene"] == "ZC3H12A"
    assert packet["win_condition"]["minimum_orthogonal_public_datasets"] == 5
    assert len(packet["win_condition"]["required_rungs"]) == 8
    assert packet["goalpost_policy"].startswith("candidate fails")


def test_preregistration_declares_dataset_freeze_and_comparability_rules():
    packet = build_defended_discovery_preregistration()
    attached = packet["dataset_freeze"]["attached_frozen_artifacts"]
    planned = packet["dataset_freeze"]["planned_public_dataset_slots"]

    assert attached
    assert all(row["sha256"] for row in attached)
    assert all(row["frozen"] is True for row in attached)
    assert all(row["freeze_required_before_scoring"] is True for row in planned)
    assert {row["slot"] for row in planned} >= {
        "additional_primary_t_cell_crispr_screen",
        "gwas_catalog_immune_traits",
        "depmap_dependency",
        "protein_interaction_network",
        "immune_subset_expression_atlas",
        "evolutionary_conservation",
        "drugbank_or_chembl_target_hook",
    }

    comparable = packet["comparable_phenotype_rules"]
    assert comparable["default_noncomparable_status"] == "orthogonal_phenotype"
    assert comparable["agreement_requires"] == [
        "same perturbed gene",
        "primary human T-cell or justified immune-cell context",
        "activation-regulation readout or a stated bridge to activation-transcriptome breadth",
        "direction and timepoint interpretable against the Marson stimulated phenotype",
    ]
    assert comparable["locked_examples"]["schmidt_2022_2427"]["status"] == "orthogonal_phenotype"


def test_preregistration_declares_independent_kill_attempts_and_failure_policy():
    packet = build_defended_discovery_preregistration()
    kills = packet["pre_registered_kill_attempts"]

    assert len(kills) >= 4
    assert {row["kill_id"] for row in kills} >= {
        "technical_confound",
        "essentiality_or_proliferation_artifact",
        "batch_or_dataset_specificity",
        "alternative_mechanism",
    }
    assert all(row["independent_axis"] for row in kills)
    assert all(row["candidate_fails_if"] for row in kills)
    assert packet["failure_policy"] == (
        "A candidate is removed from the defended-discovery lane if any pre-registered kill "
        "criterion is met. The kill threshold cannot be edited after this packet id is committed."
    )
    assert packet["falsifiable_experiment_template"]["system"] == (
        "stimulated primary human CD4+ T cells"
    )


def test_preregistration_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "defended_discovery_preregistration.json"
    out_doc = tmp_path / "DEFENDED_DISCOVERY_PREREGISTRATION.md"

    packet = write_defended_discovery_preregistration(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["pre_registration_id"].startswith("prereg_")
    assert packet["content_signature"].startswith("prereg_sig_")
    assert packet["signature_scope"] == "content seal only, not accepted frontier state"
    assert "human_signature_required" in packet["next_step"]
    assert "PGGT1B" in doc
    assert "ZC3H12A" in doc
    assert "computation over released data, not wet-lab or clinical truth" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_preregistration_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "defended-discovery-preregister"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "defended_discovery_preregistration.json" in proc.stdout
