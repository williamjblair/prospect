"""CCDC22 rank-5 defended-evidence packet tests."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.ccdc22_defended_evidence import (
    SNAPSHOT_DIR,
    build_ccdc22_defended_evidence,
    write_ccdc22_defended_evidence,
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


def test_ccdc22_packet_uses_frozen_rank_5_rows():
    packet = build_ccdc22_defended_evidence()

    assert packet["phase"] == "rank_5_ccdc22_defended_evidence"
    assert packet["gene"] == "CCDC22"
    assert packet["candidate_rank"] == 5
    assert packet["status"] == "evidence_attached"
    assert packet["accepted"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["pre_registration_id"] == "prereg_9f31fbf1e6c1cf10"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert packet["snapshot_dir"] == str(SNAPSHOT_DIR.relative_to(ROOT))
    assert len(packet["frozen_snapshots"]) >= 9
    assert all(row["sha256"] for row in packet["frozen_snapshots"])
    assert all((ROOT / row["path"]).exists() for row in packet["frozen_snapshots"])
    assert all(row["scored_from_frozen_snapshot"] is True for row in packet["scored_evidence"])


def test_ccdc22_packet_records_current_support():
    packet = build_ccdc22_defended_evidence()
    evidence = {row["source"]: row for row in packet["scored_evidence"]}
    gates = {row["gate"]: row for row in packet["open_gates"]}

    assert evidence["marson_frontier"]["summary"] == "619 stimulated DE genes, 116 Rest DE genes"
    assert evidence["replogle_specificity"]["summary"] == "K562 13; RPE1 None"
    assert evidence["primary_t_cell_screen_support"]["summary"] == "supporting hit: shifrut_2018_1107"
    assert evidence["string_network"]["summary"] == "top partners: CCDC93, VPS35L, COMMD1, COMMD8, COMMD2"
    assert evidence["dice_expression"]["summary"] == "activated CD4 mean TPM 30.218"
    assert evidence["open_targets_overlay"]["summary"] == (
        "immune dysregulation-polyendocrinopathy-enteropathy-X-linked syndrome, genetic association score 0.1945"
    )
    assert evidence["chembl_target_and_activity"]["summary"] == (
        "CHEMBL6066516 with 4 activity rows for coiled-coil domain-containing protein 22"
    )
    assert evidence["ensembl_homology"]["summary"] == "195 orthology rows from Ensembl homology"
    assert evidence["gwas_catalog_gene_lookup"]["summary"] == (
        "GWAS Catalog gene endpoint returned no CCDC22 object"
    )
    assert evidence["depmap_24q2_crispr_gene_effect"]["summary"] == (
        "1150 cancer cell lines, median gene effect -0.2020, 6 lines below -1"
    )
    assert gates["human_acceptance"]["reason"] == (
        "no human key has accepted a CCDC22 state transition"
    )
    assert gates["shifrut_replication_depth"]["reason"] == (
        "one Shifrut row supports CCDC22, while the second Shifrut row is missing from the frozen packet"
    )
    assert "expanded_external_freeze" not in gates


def test_ccdc22_packet_survives_current_kills_but_does_not_accept():
    packet = build_ccdc22_defended_evidence()
    kills = {row["kill_id"]: row for row in packet["kill_attempts"]}

    assert packet["defended_discovery_status"] == "computational_bar_cleared_pending_human_key"
    assert packet["decision_recommendation"] == "hold_and_deepen"
    assert packet["next_candidate"] is None
    assert packet["orthogonal_public_dataset_count"] >= 8
    assert kills["technical_confound"]["result"] == "survives_current_frozen_evidence"
    assert kills["essentiality_or_proliferation_artifact"]["result"] == "survives_current_frozen_evidence"
    assert kills["batch_or_dataset_specificity"]["result"] == "survives_current_frozen_evidence"
    assert kills["alternative_mechanism"]["result"] == "survives_current_frozen_evidence"
    assert packet["next_step"] == "human review of the CCDC22 proposal, then optional human-key acceptance"


def test_ccdc22_packet_writes_clean_json_and_markdown(tmp_path):
    out_json = tmp_path / "ccdc22_defended_evidence.json"
    out_doc = tmp_path / "CCDC22_DEFENDED_EVIDENCE.md"

    packet = write_ccdc22_defended_evidence(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = "\n".join(_string_values(packet)).lower() + doc.lower()

    assert packet["packet_id"].startswith("ccdc22_defended_")
    assert "CCDC22" in doc
    assert "computational bar cleared, pending human key" in doc
    assert "shifrut_2018_1107" in doc
    assert "COMMD1" in doc
    assert "median gene effect -0.2020" in doc
    assert "CHEMBL6066516" in doc
    assert "\u2014" not in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text


def test_ccdc22_defended_evidence_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "ccdc22-defended-evidence"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "ccdc22_defended_evidence.json" in proc.stdout
