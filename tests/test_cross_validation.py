"""Phase 2 external cross-validation packet tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.cross_validation import build_cross_validation, write_cross_validation


def test_cross_validation_attaches_independent_evidence_to_all_survivors():
    packet = build_cross_validation()

    assert packet["phase"] == "phase_2_independent_cross_validation"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert packet["candidate_count"] == 18
    assert packet["counts"]["candidates_with_external_screen_hit"] == 4
    assert packet["counts"]["candidates_with_schmidt_non_hit"] == 18
    assert packet["counts"]["candidates_with_schmidt_orthogonal_phenotype"] == 18
    assert packet["counts"]["candidates_with_comparable_external_contradiction"] == 0
    assert packet["counts"]["candidates_with_string_network"] >= 15
    assert packet["counts"]["candidates_with_dice_cd4_expression"] == 18
    assert packet["counts"]["candidates_with_open_targets_context"] == 18
    assert packet["source_bundle_id"].startswith("external_sources_")
    assert packet["packet_id"].startswith("cross_validation_")
    schmidt = packet["readout_comparability"]["schmidt_2022_2427"]
    assert schmidt["typed_status"] == "orthogonal_phenotype"
    assert "cytokine production" in schmidt["schmidt_readout"].lower()
    assert "activation transcriptome" in schmidt["marson_readout"].lower()


def test_cross_validation_keeps_pggt1b_strong_but_honest():
    packet = build_cross_validation()
    rows = {row["gene"]: row for row in packet["candidates"]}
    pg = rows["PGGT1B"]

    assert pg["tier"] == "screen_hit_plus_context"
    assert pg["status"] == "evidence_attached"
    assert pg["external_screen_summary"]["supporting_hits"] == ["shifrut_2018_1107"]
    assert pg["external_screen_summary"]["orthogonal_phenotypes"] == ["schmidt_2022_2427"]
    assert pg["external_screen_summary"]["contradictions"] == []
    assert pg["string_network"]["top_partners"][:3] == ["FNTA", "HEYL", "RABGGTA"]
    assert pg["dice_expression"]["activated_cd4_mean_tpm"] == 16.101
    assert pg["open_targets"]["overlay_class"] == "immune_or_hematologic_non_genetic_context"
    assert "not wet-lab" in pg["why_not_accepted"]


def test_cross_validation_retypes_schmidt_non_hits_as_orthogonal_phenotype():
    packet = build_cross_validation()
    rows = {row["gene"]: row for row in packet["candidates"]}

    assert rows["RCC1L"]["tier"] == "context_only"
    assert rows["RCC1L"]["external_screen_summary"]["supporting_hits"] == []
    assert rows["RCC1L"]["external_screen_summary"]["contradictions"] == []
    assert "schmidt_2022_2427" in rows["RCC1L"]["external_screen_summary"]["orthogonal_phenotypes"]
    assert rows["LETM2"]["external_screen_summary"]["supporting_hits"] == ["shifrut_2018_1109"]
    assert rows["CCDC22"]["external_screen_summary"]["supporting_hits"] == ["shifrut_2018_1107"]
    assert rows["TNNC1"]["external_screen_summary"]["supporting_hits"] == ["shifrut_2018_1107"]
    assert rows["CCDC22"]["disease_context"] == "genetic_context"


def test_cross_validation_writes_json_csv_and_markdown(tmp_path):
    out_json = tmp_path / "cross_validation.json"
    out_csv = tmp_path / "cross_validation.csv"
    out_doc = tmp_path / "CROSS_VALIDATION.md"

    packet = write_cross_validation(out_json=out_json, out_csv=out_csv, out_doc=out_doc)
    doc = out_doc.read_text()
    text = json.dumps(packet).lower() + doc.lower()

    assert packet["candidates"][0]["gene"] == "PGGT1B"
    assert "Phase 2 cross-validation" in doc
    assert "Shifrut 2018" in doc
    assert "Schmidt 2022" in doc
    assert "PGGT1B" in out_csv.read_text()
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text
    assert "\u2014" not in doc


def test_cross_validation_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "cross-validation"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "cross_validation.json" in proc.stdout


if __name__ == "__main__":
    test_cross_validation_attaches_independent_evidence_to_all_survivors()
    test_cross_validation_keeps_pggt1b_strong_but_honest()
    test_cross_validation_retypes_schmidt_non_hits_as_orthogonal_phenotype()
    test_cross_validation_writes_json_csv_and_markdown(Path("/tmp/prospect-cross-validation-test"))
    test_cross_validation_runs_from_cli()
    print("PASS: cross-validation")
