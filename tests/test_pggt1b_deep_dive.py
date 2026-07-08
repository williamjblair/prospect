"""PGGT1B deep-dive artifact tests.

The deep dive turns the signed agent hypothesis into a concise lab-facing
evidence packet without upgrading its status beyond evidence_attached.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.pggt1b_deep_dive import build_deep_dive, write_deep_dive


def test_pggt1b_deep_dive_keeps_status_and_exact_facts(tmp_path):
    dive = build_deep_dive()
    facts = dive["facts"]

    assert dive["gene"] == "PGGT1B"
    assert dive["status"] == "evidence_attached"
    assert dive["claim_scope"] == "hypothesis_to_test"
    assert facts["rest_de"] == 175
    assert facts["stim8hr_de"] == 3014
    assert facts["stim8hr_kd"] == "on-target KD"
    assert facts["k562_de"] == 1
    assert facts["collectri_targets"] == 0
    assert "verified" not in json.dumps(dive).lower()
    assert "true" not in json.dumps(dive).lower()


def test_pggt1b_deep_dive_includes_assay_decision_plan():
    dive = build_deep_dive()
    facts = dive["facts"]
    plan = dive["validation_plan"]

    assert facts["condition_summary"]["Stim8hr"]["n_up_genes"] == 2172
    assert facts["condition_summary"]["Stim8hr"]["n_down_genes"] == 842
    assert facts["condition_summary"]["Stim8hr"]["n_cells_target"] == 102
    assert facts["condition_summary"]["Rest"]["n_total_de_genes"] == 175
    assert plan["sample"] == "primary human CD4+ T cells"
    assert "targeted RNA-seq at 8h and 48h" in plan["primary_readout"]
    assert "non-targeting guide" in plan["negative_controls"]
    assert "VAV1" in plan["positive_controls"]
    assert any("failed on-target knockdown" in rule for rule in plan["stop_rules"])
    assert plan["status"] == "evidence_attached"
    assert plan["trust_boundary"] == "proposal_only"


def test_pggt1b_deep_dive_includes_evidence_capsule():
    dive = build_deep_dive()
    capsule = dive["evidence_capsule"]

    assert capsule["title"] == "PGGT1B evidence capsule"
    assert capsule["status"] == "evidence_attached"
    assert capsule["trust_boundary"] == "proposal_only"
    assert capsule["decision"] == "advance_to_orthogonal_assay"
    assert capsule["strongest_condition"] == "Stim8hr"
    assert capsule["stimulated_to_rest_ratio"] == 17.22
    assert capsule["stimulated_to_k562_ratio"] == 3014.0
    assert capsule["effect_balance"]["Stim8hr"]["up_genes"] == 2172
    assert capsule["effect_balance"]["Stim8hr"]["down_genes"] == 842
    assert capsule["effect_balance"]["Stim8hr"]["up_fraction"] == 0.721
    assert capsule["evidence_ladder"][0]["claim"] == "stimulated CD4+ footprint"
    assert capsule["evidence_ladder"][0]["status"] == "computationally_reproduced"
    assert capsule["evidence_ladder"][-1]["status"] == "evidence_attached"
    assert "target-level summary" in capsule["missing_for_acceptance"][0]
    assert any("orthogonal knockdown" in gate for gate in capsule["assay_gates"])
    assert "verified" not in json.dumps(capsule).lower()
    assert "true" not in json.dumps(capsule).lower()


def test_pggt1b_deep_dive_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "pggt1b_deep_dive.json"
    out_doc = tmp_path / "PGGT1B_DEEP_DIVE.md"

    write_deep_dive(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["facts"]["stim8hr_de"] == 3014
    assert "PGGT1B deep dive" in doc
    assert "evidence_attached" in doc
    assert "hypothesis to test" in doc
    assert "10.1053/j.gastro.2019.07.007" in doc
    assert "10.1016/j.cmet.2020.10.022" in doc
    assert "Assay decision plan" in doc
    assert "Evidence capsule" in doc
    assert "17.22x" in doc
    assert "target-level summary" in doc
    assert "Stim8hr | 102 | 2,172 | 842 | 3,014" in doc
    assert "failed on-target knockdown" in doc


def test_pggt1b_deep_dive_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "pggt1b"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "pggt1b_deep_dive.json" in proc.stdout


def test_pggt1b_evidence_capsule_is_visible_in_agent_tab():
    page = open(os.path.join(ROOT, "web", "app", "page.tsx")).read()
    gen_data = open(os.path.join(ROOT, "web", "gen_data.py")).read()

    assert "pggt1b_deep_dive" in gen_data
    assert "evidence_capsule" in page
    assert "Evidence capsule" in page
    assert "stimulated_to_rest_ratio" in page
    assert "missing_for_acceptance" in page


if __name__ == "__main__":
    test_pggt1b_deep_dive_keeps_status_and_exact_facts(__import__("pathlib").Path("/tmp/prospect-pggt1b-test"))
    test_pggt1b_deep_dive_includes_assay_decision_plan()
    test_pggt1b_deep_dive_includes_evidence_capsule()
    test_pggt1b_deep_dive_writes_json_and_markdown(__import__("pathlib").Path("/tmp/prospect-pggt1b-test"))
    test_pggt1b_deep_dive_runs_from_prospect_cli()
    test_pggt1b_evidence_capsule_is_visible_in_agent_tab()
    print("PASS: PGGT1B deep dive")
