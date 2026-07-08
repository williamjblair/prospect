"""Perturbation-atlas scout packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.perturbation_atlas_scout import build_packet, write_packet


def test_perturbation_atlas_scout_ranks_sources_without_ingesting_large_data():
    packet = build_packet()

    assert packet["title"] == "Perturbation-atlas scout packet"
    assert packet["status"] == "evidence_attached"
    assert packet["trust_boundary"] == "source_backed_scout_no_ingest"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["model_in_trust_path"] == "no"
    assert packet["replay_command"] == "./prospect perturbation-scout"
    assert packet["counts"] == {
        "candidate_sources": 5,
        "go_now": 0,
        "scout_only": 3,
        "no_go_large_ingest": 2,
        "public_app_surface": 0,
    }
    assert packet["recommendation"]["decision"] == "do_not_ingest_new_large_dataset_before_submission"
    assert packet["recommendation"]["next_best_action"] == "campaign_challenger_ledger"

    candidates = {item["id"]: item for item in packet["candidate_sources"]}
    assert candidates["czi_k562_essential"]["decision"] == "scout_only"
    assert candidates["czi_k562_essential"]["replay_fit"] == "highest"
    assert candidates["czi_k562_essential"]["reason"] == "single processed h5ad, but overlaps an already shipped Replogle substrate"
    assert candidates["scperturb"]["decision"] == "scout_only"
    assert candidates["scperturb"]["download_size"] == "25.01 GB"
    assert candidates["perturbase"]["decision"] == "scout_only"
    assert candidates["tahoe_100m"]["decision"] == "no_go_large_ingest"
    assert candidates["tahoe_100m"]["risk"] == "too large and chemical-only for a rushed accepted-state boundary"
    assert candidates["pertpy_replogle_loader"]["decision"] == "no_go_large_ingest"

    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_perturbation_atlas_scout_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "perturbation_atlas_scout.json"
    out_doc = tmp_path / "PERTURBATION_ATLAS_SCOUT.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "evidence_attached"
    assert data["counts"]["candidate_sources"] == 5
    assert "Perturbation-atlas scout packet" in doc
    assert "No accepted state changes" in doc
    assert "./prospect perturbation-scout" in doc
    assert "Tahoe-100M" in doc
    assert "do_not_ingest_new_large_dataset_before_submission" in doc


def test_perturbation_atlas_scout_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "perturbation-scout"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "perturbation_atlas_scout.json" in proc.stdout


if __name__ == "__main__":
    test_perturbation_atlas_scout_ranks_sources_without_ingesting_large_data()
    test_perturbation_atlas_scout_writes_json_and_markdown(Path("/tmp/prospect-perturbation-atlas-scout-test"))
    test_perturbation_atlas_scout_runs_from_prospect_cli()
    print("PASS: perturbation-atlas scout")
