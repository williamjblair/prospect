"""Endgame pre-registration tests for the defended discovery outcome."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.defended_discovery_endgame_preregistration import (
    build_defended_discovery_endgame_preregistration,
    write_defended_discovery_endgame_preregistration,
)


def _discovery() -> dict:
    return json.loads((ROOT / "examples" / "data" / "discovery_campaign.json").read_text())


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _strings(value)


def test_endgame_preregistration_locks_rank_order_and_outcome_bar():
    packet = build_defended_discovery_endgame_preregistration()
    discovery = _discovery()

    assert packet["phase"] == "defended_discovery_endgame_preregistration"
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["candidate_count"] == 18
    assert [row["gene"] for row in packet["ranked_candidates"]] == [
        row["gene"] for row in discovery["candidates"]
    ]
    assert packet["ranked_candidates"][0]["gene"] == "PGGT1B"
    assert packet["ranked_candidates"][4]["gene"] == "CCDC22"
    assert packet["candidate_order_policy"]["skip_allowed"] is False
    assert "rank 5" in packet["candidate_order_policy"]["prior_result_policy"]
    assert len(packet["discovery_bar"]["required_rungs"]) == 8
    assert packet["discovery_bar"]["minimum_orthogonal_public_datasets"] == 5
    specificity = next(
        row for row in packet["discovery_bar"]["required_rungs"]
        if row["rung"] == "cell_type_specificity"
    )
    assert "K562" in specificity["criterion"]
    assert "RPE1 only where covered" in specificity["criterion"]
    assert packet["discovery_bar"]["noncoverage_policy"]["rpe1"] == "not_assayed_context_not_failure"
    assert packet["honest_fallback"]["also_counts_as_outcome"] is True


def test_endgame_preregistration_freezes_sources_and_dataset_slots():
    packet = build_defended_discovery_endgame_preregistration()
    freeze = packet["dataset_freeze"]

    assert all(row["sha256"] for row in freeze["attached_frozen_artifacts"])
    assert all(row["content_addressed"] is True for row in freeze["attached_frozen_artifacts"])
    assert {row["slot"] for row in freeze["required_public_dataset_slots"]} == {
        "primary_t_cell_crispr_or_perturbseq",
        "gwas_catalog_immune_traits",
        "depmap_dependency",
        "protein_interaction_network",
        "immune_subset_expression_atlas",
        "drugbank_or_chembl_target_hook",
    }
    assert all(row["freeze_before_scoring"] is True for row in freeze["required_public_dataset_slots"])
    assert packet["comparability_rules"]["default_for_nonmatching_readout"] == "orthogonal_phenotype"
    assert "Schmidt" in packet["comparability_rules"]["locked_readout_mismatch"]["source"]


def test_endgame_preregistration_declares_adversarial_kills():
    packet = build_defended_discovery_endgame_preregistration()
    kills = packet["pre_registered_kill_attempts"]

    assert len(kills) >= 5
    assert {row["kill_id"] for row in kills} >= {
        "technical_confound",
        "essentiality_or_proliferation_artifact",
        "batch_or_donor_effect",
        "reverse_causality_or_passenger_marker",
        "better_alternative_mechanism",
    }
    assert all(row["candidate_fails_if"] for row in kills)
    assert all(row["dataset_or_evidence_needed"] for row in kills)
    assert packet["failure_policy"].startswith("Any landed pre-registered kill removes")
    assert packet["falsifiable_experiment"]["system"] == "stimulated primary human CD4+ T cells"


def test_endgame_preregistration_writes_clean_outputs(tmp_path):
    out_json = tmp_path / "defended_discovery_endgame_preregistration.json"
    out_doc = tmp_path / "DEFENDED_DISCOVERY_ENDGAME_PREREGISTRATION.md"

    packet = write_defended_discovery_endgame_preregistration(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_strings(packet)) + "\n" + doc

    assert packet["pre_registration_id"].startswith("endgame_prereg_")
    assert packet["content_signature"].startswith("endgame_prereg_sig_")
    assert packet["reproduce_command"] == "./prospect defended-discovery-endgame-preregister"
    assert "PGGT1B" in doc
    assert "ZC3H12A" in doc
    assert "computation over released data, not wet-lab or clinical truth" in doc
    assert "\u2014" not in text
    assert ("Generated" + " with") not in text
    assert ("Co-" + "Authored-By") not in text


def test_endgame_preregistration_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "defended-discovery-endgame-preregister"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "defended_discovery_endgame_preregistration.json" in proc.stdout
