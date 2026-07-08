"""Disease-genetics overlay packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.disease_genetics_overlay import build_packet, write_packet


def _by_gene(rows):
    return {row["gene"]: row for row in rows}


def test_disease_genetics_overlay_replays_frozen_external_context():
    packet = build_packet()

    assert packet["title"] == "Disease-genetics overlay packet"
    assert packet["status"] == "evidence_attached"
    assert packet["local_perturbation_status"] == "computationally_reproduced"
    assert packet["trust_boundary"] == "frozen_external_association_extract"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["method"]["model_in_trust_path"] == "no"
    assert packet["method"]["replay_command"] == "./prospect disease-overlay"
    assert packet["method"]["source_regeneration_command"] == "./prospect disease-overlay --refresh-source"
    assert packet["counts"] == {
        "campaign_rows": 20,
        "rows_with_external_context": 20,
        "immune_or_hematologic_context": 10,
        "immune_or_hematologic_genetic_context": 4,
        "immune_or_hematologic_non_genetic_context": 6,
        "no_immune_or_hematologic_context": 10,
    }
    assert packet["thresholds"] == {
        "min_selected_association_score": 0.05,
    }

    rows = _by_gene(packet["rows"])
    assert rows["PGGT1B"]["overlay_class"] == "immune_or_hematologic_non_genetic_context"
    assert rows["PGGT1B"]["top_context"]["disease_or_trait"] == "psoriasis"
    assert rows["PGGT1B"]["top_context"]["evidence_type"] == "literature"
    assert rows["PGGT1B"]["why_it_does_not_accept_state"]

    assert rows["CCDC22"]["overlay_class"] == "immune_or_hematologic_genetic_context"
    assert "immune dysregulation" in rows["CCDC22"]["top_context"]["disease_or_trait"]
    assert rows["GZMB"]["overlay_class"] == "immune_or_hematologic_genetic_context"
    assert rows["IRF4"]["overlay_class"] == "immune_or_hematologic_genetic_context"
    assert rows["RCC1L"]["overlay_class"] == "no_immune_or_hematologic_context"
    assert rows["SCO2"]["overlay_class"] == "immune_or_hematologic_genetic_context"
    assert rows["ZC3H12A"]["overlay_class"] == "immune_or_hematologic_non_genetic_context"

    assert "clinical truth" not in json.dumps(packet).lower()
    assert "verified" not in json.dumps(packet).lower()


def test_disease_genetics_overlay_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "disease_genetics_overlay.json"
    out_doc = tmp_path / "DISEASE_GENETICS_OVERLAY.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "evidence_attached"
    assert data["counts"]["immune_or_hematologic_context"] == 10
    assert "Disease-genetics overlay packet" in doc
    assert "No accepted state changes" in doc
    assert "./prospect disease-overlay" in doc
    assert "PGGT1B" in doc
    assert "CCDC22" in doc


def test_disease_genetics_overlay_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "disease-overlay"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "disease_genetics_overlay.json" in proc.stdout


if __name__ == "__main__":
    test_disease_genetics_overlay_replays_frozen_external_context()
    test_disease_genetics_overlay_writes_json_and_markdown(Path("/tmp/prospect-disease-overlay-test"))
    test_disease_genetics_overlay_runs_from_prospect_cli()
    print("PASS: disease-genetics overlay")
