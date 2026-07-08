"""Phase 4 overclaim counter tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.overclaim_counter import build_overclaim_counter, write_overclaim_counter


def test_overclaim_counter_quantifies_benchmark_and_discovery_refusals():
    packet = build_overclaim_counter()
    counts = packet["counts"]

    assert packet["phase"] == "phase_4_overclaim_counter"
    assert packet["status"] == "evidence_attached"
    assert packet["acceptance"] is False
    assert packet["trust_boundary"] == "proposal_only"
    assert packet["honest_ceiling"] == "computation over released data, not wet-lab or clinical truth"
    assert counts["model_major_claims"] == 137
    assert counts["model_checkable_claims"] == 96
    assert counts["model_contradicted_claims"] == 46
    assert counts["model_contradicted_rate"] == 0.4792
    assert counts["effector_overclaimed"] == 46
    assert counts["effector_total"] == 72
    assert counts["phase1_frontier_genes"] == 11526
    assert counts["phase1_survivors"] == 18
    assert counts["phase1_refused_total"] == 11508
    assert counts["phase2_without_external_screen_hit"] == 14
    assert counts["phase2_schmidt_non_hits"] == 18
    assert counts["phase2_schmidt_orthogonal_phenotypes"] == 18
    assert counts["phase2_comparable_external_contradictions"] == 0
    assert counts["flagship_hypotheses"] == 1


def test_overclaim_counter_has_rung_by_rung_refusals():
    packet = build_overclaim_counter()
    rungs = {rung["rung"]: rung for rung in packet["rungs"]}

    assert rungs["frozen_marson_checker"]["contradicted"] == 46
    assert rungs["mutation_floor"]["false_admissions"] == 0
    assert rungs["novelty_filter"]["refused"] == 11508
    assert rungs["external_screen_ladder"]["no_supporting_screen_hit"] == 14
    assert rungs["external_screen_ladder"]["schmidt_non_hits"] == 18
    assert rungs["external_screen_ladder"]["status"] == "orthogonal_phenotype"
    assert rungs["single_hypothesis_boundary"]["flagship_gene"] == "PGGT1B"
    assert all(
        rung["status"] in {"evidence_attached", "contradicted", "refuted", "orthogonal_phenotype"}
        for rung in packet["rungs"]
    )


def test_overclaim_counter_records_model_breakdown_and_flagship_boundary():
    packet = build_overclaim_counter()

    assert [row["label"] for row in packet["model_breakdown"]] == ["Haiku 4.5", "Sonnet 5", "Opus 4.8", "Fable 5"]
    assert packet["model_breakdown"][0]["refuted_rate"] == 0.56
    assert packet["flagship_boundary"]["gene"] == "PGGT1B"
    assert packet["flagship_boundary"]["claim_kind"] == "single_gene_hypothesis"
    assert packet["flagship_boundary"]["accepted_state"] == "none"
    assert "human key" in packet["flagship_boundary"]["next_acceptance_step"]


def test_overclaim_counter_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "overclaim_counter.json"
    out_doc = tmp_path / "OVERCLAIM_COUNTER.md"

    packet = write_overclaim_counter(out_json=out_json, out_doc=out_doc)
    doc = out_doc.read_text()
    text = json.dumps(packet).lower() + doc.lower()

    assert "Overclaim counter" in doc
    assert "46 of 96" in doc
    assert "14 of 18" in doc
    assert "PGGT1B" in doc
    assert ("veri" + "fied") not in text
    assert ("tr" + "ue") not in text
    assert "\u2014" not in doc


def test_overclaim_counter_runs_from_cli():
    proc = subprocess.run(
        [sys.executable, "-m", "cli", "overclaim-counter"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "overclaim_counter.json" in proc.stdout


if __name__ == "__main__":
    test_overclaim_counter_quantifies_benchmark_and_discovery_refusals()
    test_overclaim_counter_has_rung_by_rung_refusals()
    test_overclaim_counter_records_model_breakdown_and_flagship_boundary()
    test_overclaim_counter_writes_json_and_markdown(Path("/tmp/prospect-overclaim-counter-test"))
    test_overclaim_counter_runs_from_cli()
    print("PASS: overclaim counter")
