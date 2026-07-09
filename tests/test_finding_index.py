"""Scannable finding index tests."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontier.finding_index import build_index, write_index


def test_finding_index_tracks_all_signed_findings_in_order():
    index = build_index()
    rows = index["items"]

    assert index["status"] == "computationally_reproduced"
    assert len(rows) == 5
    assert [r["kind"] for r in rows] == [
        "activation_module",
        "regulator_vs_effector",
        "essentiality_artifact",
        "cross_cell_type_transfer",
        "regulon_recovery",
    ]
    assert rows[0]["rank"] == 1
    assert rows[0]["n_genes"] == 245
    assert rows[0]["status"] == "computationally_reproduced"
    assert rows[1]["challenge_status"] == "none"
    assert "broad driver claim" in rows[1]["takeaway"]
    assert all(r["cid"].startswith("cid_") for r in rows)
    assert "verified" not in json.dumps(index).lower()
    assert "true" not in json.dumps(index).lower()


def test_finding_index_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "finding_index.json"
    out_doc = tmp_path / "FINDING_INDEX.md"

    write_index(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["items"][0]["kind"] == "activation_module"
    assert "Scannable findings index" in doc
    assert "computationally_reproduced" in doc
    assert "regulator_vs_effector" in doc


def test_finding_index_runs_as_a_script():
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "frontier", "finding_index.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "finding_index.json" in proc.stdout


def test_finding_index_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "findings-index"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "finding_index.json" in proc.stdout


if __name__ == "__main__":
    test_finding_index_tracks_all_signed_findings_in_order()
    test_finding_index_writes_json_and_markdown(__import__("pathlib").Path("/tmp/prospect-finding-index-test"))
    test_finding_index_runs_as_a_script()
    test_finding_index_runs_from_prospect_cli()
    print("PASS: finding index")
