"""Wet-lab validation shortlist tests.

The shortlist is derived from frozen verifier outputs only. It should surface
testable hypotheses with typed status, not claims of established biology.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.validation_sheet import rank_candidates


def test_rank_candidates_surfaces_pggt1b_as_testable_hypothesis():
    rows = rank_candidates(limit=20)
    by_gene = {r["gene"]: r for r in rows}

    assert "PGGT1B" in by_gene
    pg = by_gene["PGGT1B"]
    assert pg["status"] == "evidence_attached"
    assert pg["replayability"] == "attested"
    assert pg["k562_de"] <= 25
    assert pg["known_regulon_targets"] == 0
    assert "hypothesis to test" in pg["rationale"]


def test_rank_candidates_excludes_canonical_and_housekeeping_genes():
    rows = rank_candidates(limit=50)
    genes = {r["gene"] for r in rows}

    assert "PDCD1" not in genes
    assert "CTLA4" not in genes
    assert "MED19" not in genes
    assert all(r["status"] == "evidence_attached" for r in rows)


def test_rank_candidates_require_on_target_stimulated_evidence():
    rows = rank_candidates(limit=50)

    assert rows
    assert all(r["strongest_kd"] == "on-target KD" for r in rows)


def test_validation_sheet_runs_as_a_script():
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "frontier", "validation_sheet.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "validation_candidates.csv" in proc.stdout


if __name__ == "__main__":
    test_rank_candidates_surfaces_pggt1b_as_testable_hypothesis()
    test_rank_candidates_excludes_canonical_and_housekeeping_genes()
    test_rank_candidates_require_on_target_stimulated_evidence()
    test_validation_sheet_runs_as_a_script()
    print("PASS: validation candidate shortlist")
