"""Donor-condition replay packet tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.donor_condition_replay import build_packet, write_packet


def _by_gene(rows):
    return {row["gene"]: row for row in rows}


def test_donor_condition_replay_classifies_campaign_rows_from_frozen_source_extract():
    packet = build_packet()

    assert packet["title"] == "Donor-condition replay packet"
    assert packet["status"] == "computationally_reproduced"
    assert packet["trust_boundary"] == "frozen_donor_rows_extracted_from_released_h5ad"
    assert packet["accepted_state_mutation"] == "none"
    assert packet["method"]["model_in_trust_path"] == "no"
    assert packet["method"]["replay_command"] == "./prospect donor-replay"
    assert packet["method"]["source_regeneration_command"] == "./prospect donor-replay --refresh-source"
    assert packet["thresholds"] == {
        "actionable_de_genes": 50,
        "donor_supported_hits_min": 0.5,
        "donor_supported_hits_mean": 0.6,
        "donor_fragile_hits_min_lt": 0.35,
        "min_guides_for_full_support": 2,
    }
    assert packet["counts"] == {
        "campaign_rows": 20,
        "strongest_condition_rows": 20,
        "donor_supported": 13,
        "donor_intermediate": 2,
        "donor_fragile": 4,
        "guide_limited": 1,
        "donor_not_estimated": 0,
        "aggregate_not_actionable": 0,
    }
    rows = _by_gene(packet["rows"])
    assert rows["PGGT1B"]["donor_replay_class"] == "donor_supported"
    assert rows["PGGT1B"]["condition"] == "Stim8hr"
    assert rows["PGGT1B"]["n_total_de_genes"] == 3014
    assert rows["PGGT1B"]["donor_correlation_hits_min"] == 0.6045
    assert rows["PGGT1B"]["donor_correlation_hits_mean"] == 0.7185
    assert rows["PGGT1B"]["guide_n_signif_ontarget"] == 2
    assert rows["RWDD2B"]["donor_replay_class"] == "donor_fragile"
    assert rows["RWDD2B"]["donor_correlation_hits_min"] == 0.2946
    assert rows["SNAP29"]["donor_replay_class"] == "guide_limited"
    assert rows["SNAP29"]["single_guide_estimate"] == "yes"
    assert rows["IRF4"]["donor_replay_class"] == "donor_fragile"
    assert packet["promotion_candidates"][0]["gene"] == "PGGT1B"
    assert packet["capacity_warnings"][0]["gene"] == "RWDD2B"
    assert "wet-lab" in packet["limitations"]
    assert "verified" not in json.dumps(packet).lower()
    assert "true" not in json.dumps(packet).lower()


def test_donor_condition_replay_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "donor_condition_replay.json"
    out_doc = tmp_path / "DONOR_CONDITION_REPLAY.md"

    write_packet(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["status"] == "computationally_reproduced"
    assert data["counts"]["donor_supported"] == 13
    assert "Donor-condition replay packet" in doc
    assert "No accepted state changes" in doc
    assert "./prospect donor-replay" in doc
    assert "./prospect donor-replay --refresh-source" in doc
    assert "PGGT1B" in doc
    assert "RWDD2B" in doc


def test_donor_condition_replay_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "donor-replay"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "donor_condition_replay.json" in proc.stdout


if __name__ == "__main__":
    test_donor_condition_replay_classifies_campaign_rows_from_frozen_source_extract()
    test_donor_condition_replay_writes_json_and_markdown(Path("/tmp/prospect-donor-condition-replay-test"))
    test_donor_condition_replay_runs_from_prospect_cli()
    print("PASS: donor-condition replay")
