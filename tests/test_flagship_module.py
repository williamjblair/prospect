"""Phase 3 flagship module tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.flagship_module import build_flagship_module, write_flagship_module


def test_flagship_module_selects_pggt1b_trafficking_hypothesis():
    packet = build_flagship_module()
    flagship = packet["flagship_module"]

    assert packet["phase"] == "phase_3_flagship_module"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert flagship["module_id"] == "prenylation_small_gtpase_trafficking"
    assert flagship["anchor_gene"] == "PGGT1B"
    assert flagship["members"] == ["PGGT1B", "CCDC22", "SNAP29", "MITD1"]
    assert flagship["screen_supported_members"] == ["PGGT1B", "CCDC22"]
    assert flagship["contradicting_screen"] == "schmidt_2022_2427"
    assert flagship["status"] == "evidence_attached"
    assert "hypothesis" in flagship["claim"].lower()


def test_flagship_module_keeps_evidence_ladder_and_refutation_test():
    packet = build_flagship_module()
    flagship = packet["flagship_module"]
    by_gene = {row["gene"]: row for row in flagship["member_evidence"]}

    assert by_gene["PGGT1B"]["evidence_ladder"][0]["status"] == "computationally_reproduced"
    assert by_gene["PGGT1B"]["evidence_ladder"][1]["status"] == "evidence_attached"
    assert by_gene["CCDC22"]["tier"] == "screen_hit_plus_context"
    assert by_gene["SNAP29"]["tier"] == "context_only"
    assert by_gene["MITD1"]["tier"] == "context_only"
    assert flagship["refutation_experiment"]["system"] == "stimulated primary human CD4+ T cells"
    assert flagship["refutation_experiment"]["perturbations"] == ["PGGT1B", "CCDC22", "SNAP29", "MITD1"]
    assert "no reproducible activation-program shift" in flagship["refutation_experiment"]["refutes_if"]
    assert "not wet-lab" in flagship["why_not_accepted"]


def test_flagship_module_ranks_competing_modules():
    packet = build_flagship_module()
    modules = {module["module_id"]: module for module in packet["modules"]}

    assert modules["prenylation_small_gtpase_trafficking"]["rank"] == 1
    assert modules["rna_decay_and_effector_context"]["rank"] == 2
    assert modules["mitochondrial_metabolic_activation"]["rank"] == 3
    assert modules["prenylation_small_gtpase_trafficking"]["score"] > modules["rna_decay_and_effector_context"]["score"]
    assert modules["mitochondrial_metabolic_activation"]["members"] == ["RCC1L", "MCAT", "SCO2", "BCKDHA"]


def test_flagship_module_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "flagship_module.json"
    out_doc = tmp_path / "FLAGSHIP_FINDING.md"

    packet = write_flagship_module(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = json.dumps(packet).lower() + doc.lower()

    assert packet["flagship_module"]["anchor_gene"] == "PGGT1B"
    assert "Flagship finding" in doc
    assert "prenylation" in doc
    assert "CRISPRi" in doc
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
    test_flagship_module_selects_pggt1b_trafficking_hypothesis()
    test_flagship_module_keeps_evidence_ladder_and_refutation_test()
    test_flagship_module_ranks_competing_modules()
    test_flagship_module_writes_json_and_markdown(Path("/tmp/prospect-flagship-module-test"))
    test_flagship_module_runs_from_cli()
    print("PASS: flagship module")
