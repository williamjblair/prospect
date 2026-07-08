"""Campaign agent probe tests.

The probe compares Claude's proposal-only campaign recommendations to the
deterministic review lanes. Tests use fixture recommendations, not the API.
"""
import json
from pathlib import Path

import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import loop.campaign_probe as campaign_probe_module
from loop.campaign_probe import build_probe, chunk_gene_batches, campaign_genes, write_probe


FIXTURE_DECISIONS = [
    {
        "gene": "PGGT1B",
        "recommendation": "advance_to_assay_design",
        "rationale": "Largest stimulated footprint and low non-immune transfer.",
    },
    {
        "gene": "RCC1L",
        "recommendation": "advance_if_capacity_allows",
        "rationale": "Strong stimulated signal, but not the top assay row.",
    },
    {
        "gene": "MCAT",
        "recommendation": "hold_as_ranked_backup",
        "rationale": "Useful backup with a smaller signal.",
    },
]


def test_campaign_probe_compares_model_recommendations_to_review_lanes():
    probe = build_probe(
        decisions=FIXTURE_DECISIONS,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_limit=5,
        requested_genes=["PGGT1B", "RCC1L", "MCAT", "SNAP29", "LETM2"],
    )

    rows = probe["rows"]
    by_gene = {row["gene"]: row for row in rows}

    assert probe["status"] == "evidence_attached"
    assert probe["trust_boundary"] == "proposal_only"
    assert probe["acceptance"] is False
    assert probe["candidate_count"] == 3
    assert probe["coverage"] == {
        "requested_limit": 5,
        "returned_decisions": 3,
        "coverage_status": "partial",
        "missing_decisions": 2,
        "requested_genes": ["PGGT1B", "RCC1L", "MCAT", "SNAP29", "LETM2"],
        "returned_genes": ["PGGT1B", "RCC1L", "MCAT"],
        "missing_genes": ["SNAP29", "LETM2"],
    }
    assert probe["summary"]["aligned"] == 2
    assert probe["summary"]["more_aggressive"] == 1
    assert by_gene["PGGT1B"]["deterministic_decision"] == "advance_to_assay_design"
    assert by_gene["PGGT1B"]["agent_recommendation"] == "advance_to_assay_design"
    assert by_gene["PGGT1B"]["alignment"] == "aligned"
    assert by_gene["RCC1L"]["deterministic_decision"] == "hold_as_ranked_backup"
    assert by_gene["RCC1L"]["alignment"] == "more_aggressive"
    assert "verified" not in json.dumps(probe).lower()
    assert "true" not in json.dumps(probe).lower()


def test_campaign_probe_builds_ranked_gene_batches():
    genes = campaign_genes(limit=10)

    assert genes[:3] == ["PGGT1B", "RCC1L", "MCAT"]
    assert genes[-1] == "DAPK2"
    assert chunk_gene_batches(genes, chunk_size=4) == [
        ["PGGT1B", "RCC1L", "MCAT", "RWDD2B"],
        ["CCDC22", "GAS2L1", "SNAP29", "CYB5RL"],
        ["LETM2", "DAPK2"],
    ]


def test_campaign_probe_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_agent_probe.json"
    out_doc = tmp_path / "CAMPAIGN_AGENT_PROBE.md"

    probe = write_probe(
        out_json=out_json,
        out_doc=out_doc,
        decisions=FIXTURE_DECISIONS,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
    )

    doc = out_doc.read_text()
    assert probe["rows"][0]["gene"] == "PGGT1B"
    assert "Campaign agent probes" in doc
    assert "proposal only" in doc
    assert "No candidate enters accepted state" in doc
    assert "more_aggressive" in doc
    assert "python loop/campaign_probe.py --limit 3" in doc
    assert "Coverage: 3 returned / 3 requested. Complete: yes." in doc
    assert "PGGT1B" in out_json.read_text()


def test_campaign_probe_sample_cli_runs_without_api_key(tmp_path):
    out_json = tmp_path / "campaign_agent_probe.json"
    out_doc = tmp_path / "CAMPAIGN_AGENT_PROBE.md"
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(ROOT, "loop", "campaign_probe.py"),
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
    assert "campaign_agent_probe.json" in proc.stdout
    data = json.loads(out_json.read_text())
    assert data["candidate_count"] == 3
    assert data["coverage"]["coverage_status"] == "complete"


def test_campaign_probe_runs_from_prospect_cli(tmp_path):
    out_json = tmp_path / "campaign_agent_probe.json"
    out_doc = tmp_path / "CAMPAIGN_AGENT_PROBE.md"
    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "campaign-probe",
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
    assert "campaign_agent_probe.json" in proc.stdout
    data = json.loads(out_json.read_text())
    assert data["trust_boundary"] == "proposal_only"
    assert data["coverage"]["returned_decisions"] == 3


def test_campaign_probe_custom_live_path_does_not_write_default(tmp_path):
    out_json = tmp_path / "campaign_agent_probe.json"
    out_doc = tmp_path / "CAMPAIGN_AGENT_PROBE.md"
    default_before = (ROOT / "examples" / "data" / "campaign_agent_probe.json").read_text()

    def fake_run_live(**kwargs):
        return write_probe(
            out_json=kwargs["out_json"],
            out_doc=kwargs["out_doc"],
            decisions=FIXTURE_DECISIONS,
            model="claude-opus-4-8",
            tool_calls=[],
            cost_usd=0.0,
            requested_limit=kwargs["limit"],
            requested_genes=["PGGT1B", "RCC1L", "MCAT"],
        )

    original = campaign_probe_module.run_live
    try:
        campaign_probe_module.run_live = fake_run_live
        campaign_probe_module.main([
            "--out-json",
            str(out_json),
            "--out-doc",
            str(out_doc),
        ])
    finally:
        campaign_probe_module.run_live = original

    assert out_json.exists()
    assert (ROOT / "examples" / "data" / "campaign_agent_probe.json").read_text() == default_before


def test_campaign_probe_is_in_public_web_bundle():
    data = json.loads((ROOT / "web" / "public" / "data" / "frontier.json").read_text())
    probe = data["campaign_agent_probe"]

    assert probe["status"] == "evidence_attached"
    assert probe["trust_boundary"] == "proposal_only"
    assert probe["acceptance"] is False
    assert probe["rows"][0]["gene"] == "PGGT1B"
    assert probe["coverage"]["returned_decisions"] == probe["candidate_count"]
    assert probe["coverage"]["coverage_status"] == "complete"


def test_campaign_probe_is_visible_in_agent_tab():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    gen_data = (ROOT / "web" / "gen_data.py").read_text()

    assert "campaign_agent_probe" in gen_data
    assert "CampaignAgentProbe" in page
    assert "Campaign agent probes" in page
    assert "Coverage:" in page
    assert "/data/campaign_agent_probe.json" in page
    assert "d.campaign_agent_probe" in page


if __name__ == "__main__":
    test_campaign_probe_compares_model_recommendations_to_review_lanes()
    test_campaign_probe_builds_ranked_gene_batches()
    test_campaign_probe_writes_json_and_markdown(Path("/tmp/prospect-campaign-probe-test"))
    test_campaign_probe_sample_cli_runs_without_api_key(Path("/tmp/prospect-campaign-probe-cli-test"))
    test_campaign_probe_runs_from_prospect_cli(Path("/tmp/prospect-campaign-probe-prospect-test"))
    test_campaign_probe_custom_live_path_does_not_write_default(Path("/tmp/prospect-campaign-probe-custom-path-test"))
    test_campaign_probe_is_in_public_web_bundle()
    test_campaign_probe_is_visible_in_agent_tab()
    print("PASS: campaign agent probe")
