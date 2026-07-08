"""Phase 3 flagship hypothesis tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.flagship_module import build_flagship_module, write_flagship_module


def test_flagship_packet_selects_pggt1b_single_hypothesis():
    packet = build_flagship_module()
    hypothesis = packet["flagship_hypothesis"]

    assert packet["phase"] == "phase_3_single_gene_hypothesis"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert hypothesis["gene"] == "PGGT1B"
    assert hypothesis["rank"] == 1
    assert hypothesis["status"] == "evidence_attached"
    assert hypothesis["support_level"] == "rank_1_screen_supported_hypothesis"
    assert hypothesis["schmidt_status"] == "orthogonal_phenotype"
    assert hypothesis["accepted"] is False
    assert "hypothesis" in hypothesis["claim"].lower()
    assert "module" not in hypothesis["claim"].lower()


def test_flagship_packet_keeps_evidence_ladder_and_refutation_test():
    packet = build_flagship_module()
    hypothesis = packet["flagship_hypothesis"]
    rungs = {row["rung"]: row for row in hypothesis["evidence_ladder"]}

    assert rungs["marson_frontier"]["status"] == "computationally_reproduced"
    assert rungs["shifrut_primary_t_cell_screen"]["status"] == "evidence_attached"
    assert rungs["schmidt_cytokine_screen"]["status"] == "orthogonal_phenotype"
    assert rungs["protein_prenylation_context"]["status"] == "evidence_attached"
    assert hypothesis["refutation_experiment"]["system"] == "stimulated primary human CD4+ T cells"
    assert hypothesis["refutation_experiment"]["perturbations"] == ["PGGT1B"]
    assert "no reproducible activation-program shift" in hypothesis["refutation_experiment"]["refutes_if"]
    assert "not wet-lab" in hypothesis["why_not_accepted"]


def test_flagship_packet_keeps_supported_alternatives_visible():
    packet = build_flagship_module()
    visible = {row["gene"]: row for row in packet["supported_alternatives"]}

    assert set(visible) == {"CCDC22", "LETM2", "TNNC1"}
    assert all(row["tier"] == "screen_hit_plus_context" for row in visible.values())
    assert "rank-1" in packet["selection_rationale"]
    assert "silently dropped" not in json.dumps(packet).lower()


def test_flagship_module_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "flagship_module.json"
    out_doc = tmp_path / "FLAGSHIP_FINDING.md"

    packet = write_flagship_module(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = json.dumps(packet).lower() + doc.lower()

    assert packet["flagship_hypothesis"]["gene"] == "PGGT1B"
    assert "Flagship finding" in doc
    assert "single PGGT1B hypothesis" in doc
    assert "prenylation" in doc
    assert "CRISPRi" in doc
    assert "validated module" not in text
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text
    assert "\u2014" not in doc


def test_flagship_module_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "flagship-module"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "flagship_module.json" in proc.stdout


if __name__ == "__main__":
    test_flagship_packet_selects_pggt1b_single_hypothesis()
    test_flagship_packet_keeps_evidence_ladder_and_refutation_test()
    test_flagship_packet_keeps_supported_alternatives_visible()
    test_flagship_module_writes_json_and_markdown(Path("/tmp/prospect-flagship-module-test"))
    test_flagship_module_runs_from_cli()
    print("PASS: flagship hypothesis")
