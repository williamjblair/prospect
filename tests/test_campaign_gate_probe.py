"""Campaign gate probe tests.

The gate probe asks a model or fixture reviewer to inspect the deterministic
assay gates produced from campaign disagreements. It can prioritize controls,
but it never accepts state.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop.campaign_gate_probe import build_gate_probe, write_gate_probe


FIXTURE_DECISIONS = [
    {
        "gene": "RCC1L",
        "gate_recommendation": "gate_sufficient",
        "rationale": "The existing matched Rest, Stim8hr, and Stim48hr orthogonal knockdown gate covers the main risk.",
    },
    {
        "gene": "MCAT",
        "gate_recommendation": "add_control",
        "rationale": "The Rest knockdown caveat needs a second guide and transfer check before capacity is spent.",
    },
    {
        "gene": "RWDD2B",
        "gate_recommendation": "add_control",
        "rationale": "The higher Rest signal makes matched unstimulated culture a required control.",
    },
    {
        "gene": "CCDC22",
        "gate_recommendation": "lower_priority",
        "rationale": "The gate is reasonable, but lower magnitude makes it less urgent than stronger rows.",
    },
]


def test_campaign_gate_probe_scores_existing_assay_gates_without_accepting_state():
    probe = build_gate_probe(
        decisions=FIXTURE_DECISIONS,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
    )

    rows = probe["rows"]
    by_gene = {row["gene"]: row for row in rows}

    assert probe["title"] == "Campaign gate probe"
    assert probe["status"] == "evidence_attached"
    assert probe["trust_boundary"] == "proposal_only"
    assert probe["acceptance"] is False
    assert probe["candidate_count"] == 4
    assert probe["summary"] == {"add_control": 2, "gate_sufficient": 1, "lower_priority": 1}
    assert [row["gene"] for row in rows] == ["RCC1L", "MCAT", "RWDD2B", "CCDC22"]
    assert by_gene["RCC1L"]["source_triage_decision"] == "secondary_assay_queue"
    assert by_gene["RCC1L"]["gate_recommendation"] == "gate_sufficient"
    assert "orthogonal knockdown" in by_gene["RCC1L"]["assay_gate"]
    assert by_gene["MCAT"]["gate_recommendation"] == "add_control"
    assert by_gene["CCDC22"]["gate_recommendation"] == "lower_priority"
    assert all(row["status"] == "evidence_attached" for row in rows)
    assert all(row["trust_boundary"] == "proposal_only" for row in rows)
    assert "verified" not in json.dumps(probe).lower()
    assert "true" not in json.dumps(probe).lower()


def test_campaign_gate_probe_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_gate_probe.json"
    out_doc = tmp_path / "CAMPAIGN_GATE_PROBE.md"

    probe = write_gate_probe(
        out_json=out_json,
        out_doc=out_doc,
        decisions=FIXTURE_DECISIONS,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
    )

    doc = out_doc.read_text()
    assert probe["rows"][0]["gene"] == "RCC1L"
    assert "Campaign gate probe" in doc
    assert "proposal only" in doc
    assert "gate_sufficient" in doc
    assert "add_control" in doc
    assert "lower_priority" in doc
    assert "python loop/campaign_gate_probe.py --sample" in doc
    assert "RCC1L" in out_json.read_text()


def test_campaign_gate_probe_sample_cli_runs_without_api_key(tmp_path):
    out_json = tmp_path / "campaign_gate_probe.json"
    out_doc = tmp_path / "CAMPAIGN_GATE_PROBE.md"
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(ROOT, "loop", "campaign_gate_probe.py"),
            "--sample",
            "--out-json",
            str(out_json),
            "--out-doc",
            str(out_doc),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "campaign_gate_probe.json" in proc.stdout
    assert json.loads(out_json.read_text())["trust_boundary"] == "proposal_only"


def test_campaign_gate_probe_runs_from_prospect_cli(tmp_path):
    out_json = tmp_path / "campaign_gate_probe.json"
    out_doc = tmp_path / "CAMPAIGN_GATE_PROBE.md"
    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "campaign-gate-probe",
            "--sample",
            "--out-json",
            str(out_json),
            "--out-doc",
            str(out_doc),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.returncode == 0, proc.stderr
    assert "campaign_gate_probe.json" in proc.stdout
    assert json.loads(out_json.read_text())["candidate_count"] == 4


def test_campaign_gate_probe_is_in_public_web_bundle():
    data = json.loads((ROOT / "web" / "public" / "data" / "frontier.json").read_text())
    probe = data["campaign_gate_probe"]

    assert probe["status"] == "evidence_attached"
    assert probe["trust_boundary"] == "proposal_only"
    assert probe["acceptance"] is False
    assert probe["rows"][0]["gene"] == "RCC1L"


def test_campaign_gate_probe_is_visible_in_agent_tab():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    gen_data = (ROOT / "web" / "gen_data.py").read_text()

    assert "campaign_gate_probe" in gen_data
    assert "CampaignGateProbe" in page
    assert "Campaign gate probe" in page
    assert "/data/campaign_gate_probe.json" in page
    assert "d.campaign_gate_probe" in page


if __name__ == "__main__":
    test_campaign_gate_probe_scores_existing_assay_gates_without_accepting_state()
    test_campaign_gate_probe_writes_json_and_markdown(Path("/tmp/prospect-campaign-gate-probe-test"))
    test_campaign_gate_probe_sample_cli_runs_without_api_key(Path("/tmp/prospect-campaign-gate-probe-cli-test"))
    test_campaign_gate_probe_runs_from_prospect_cli(Path("/tmp/prospect-campaign-gate-probe-prospect-test"))
    test_campaign_gate_probe_is_in_public_web_bundle()
    test_campaign_gate_probe_is_visible_in_agent_tab()
    print("PASS: campaign gate probe")
