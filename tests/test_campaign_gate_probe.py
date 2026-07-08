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

import loop.campaign_gate_probe as gate_probe_module
from loop.campaign_gate_probe import build_gate_probe, merge_probe_decisions, parse_gene_list, write_gate_probe


FIXTURE_DECISIONS = [
    {
        "gene": "RCC1L",
        "gate_recommendation": "gate_sufficient",
        "rationale": "The existing matched Rest, Stim8hr, and Stim48hr orthogonal knockdown gate covers the main risk.",
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
    {
        "gene": "CYB5RL",
        "gate_recommendation": "gate_sufficient",
        "rationale": "The K562-inert specificity and matched-condition gate cover the main promotion risk.",
    },
]


def test_campaign_gate_probe_scores_existing_assay_gates_without_accepting_state():
    probe = build_gate_probe(
        decisions=FIXTURE_DECISIONS,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_genes=["RCC1L", "RWDD2B", "CCDC22", "CYB5RL"],
    )

    rows = probe["rows"]
    by_gene = {row["gene"]: row for row in rows}

    assert probe["title"] == "Campaign gate probe"
    assert probe["status"] == "evidence_attached"
    assert probe["trust_boundary"] == "proposal_only"
    assert probe["acceptance"] is False
    assert probe["candidate_count"] == 4
    assert probe["coverage"] == {
        "requested_limit": 4,
        "returned_decisions": 4,
        "coverage_status": "complete",
        "missing_decisions": 0,
        "requested_genes": ["RCC1L", "RWDD2B", "CCDC22", "CYB5RL"],
        "returned_genes": ["RCC1L", "RWDD2B", "CCDC22", "CYB5RL"],
        "missing_genes": [],
    }
    assert probe["summary"] == {"add_control": 1, "gate_sufficient": 2, "lower_priority": 1}
    assert [row["gene"] for row in rows] == ["RCC1L", "RWDD2B", "CCDC22", "CYB5RL"]
    assert by_gene["RCC1L"]["source_triage_decision"] == "secondary_assay_queue"
    assert by_gene["RCC1L"]["gate_recommendation"] == "gate_sufficient"
    assert "orthogonal knockdown" in by_gene["RCC1L"]["assay_gate"]
    assert by_gene["RWDD2B"]["gate_recommendation"] == "add_control"
    assert by_gene["CCDC22"]["gate_recommendation"] == "lower_priority"
    assert all(row["status"] == "evidence_attached" for row in rows)
    assert all(row["trust_boundary"] == "proposal_only" for row in rows)
    assert "verified" not in json.dumps(probe).lower()
    assert "true" not in json.dumps(probe).lower()


def test_campaign_gate_probe_deduplicates_and_filters_to_requested_genes():
    probe = build_gate_probe(
        decisions=[
            {
                "gene": "RCC1L",
                "gate_recommendation": "gate_sufficient",
                "rationale": "First grounded rationale.",
            },
            {
                "gene": "RCC1L",
                "gate_recommendation": "add_control",
                "rationale": "Duplicate should not inflate coverage.",
            },
            {
                "gene": "SCO2",
                "gate_recommendation": "add_control",
                "rationale": "Unrequested row should be ignored.",
            },
        ],
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_genes=["RCC1L", "RWDD2B"],
    )

    assert probe["candidate_count"] == 1
    assert [row["gene"] for row in probe["rows"]] == ["RCC1L"]
    assert probe["coverage"] == {
        "requested_limit": 2,
        "returned_decisions": 1,
        "coverage_status": "partial",
        "missing_decisions": 1,
        "requested_genes": ["RCC1L", "RWDD2B"],
        "returned_genes": ["RCC1L"],
        "missing_genes": ["RWDD2B"],
    }


def test_campaign_gate_probe_parses_focused_gene_list_in_triage_order():
    assert parse_gene_list("MITD1, ccdc136, MITD1") == ["CCDC136", "MITD1"]


def test_campaign_gate_probe_rejects_genes_outside_disagreement_triage():
    try:
        parse_gene_list("PGGT1B")
    except ValueError as exc:
        assert "not in campaign disagreement triage" in str(exc)
    else:
        raise AssertionError("expected PGGT1B to be rejected")


def test_campaign_gate_probe_live_focuses_requested_genes_and_custom_paths(tmp_path):
    out_json = tmp_path / "focused_gate_probe.json"
    out_doc = tmp_path / "FOCUSED_GATE_PROBE.md"
    default_before = (ROOT / "examples" / "data" / "campaign_gate_probe.json").read_text()
    calls = []

    def fake_run_live_prompt(goal, requested_genes=None):
        calls.append((goal, requested_genes))
        assert "CCDC136, MITD1" in goal
        assert "RCC1L" not in goal
        return {
            "decisions": [
                {
                    "gene": "CCDC136",
                    "gate_recommendation": "gate_sufficient",
                    "rationale": "The matched stimulated and Rest gate covers the main promotion risk.",
                },
                {
                    "gene": "MITD1",
                    "gate_recommendation": "add_control",
                    "rationale": "The missing non-immune transfer evidence needs a matched transfer control.",
                },
            ],
            "tool_calls": [],
            "cost_usd": 0.0,
        }

    original = gate_probe_module._run_live_prompt
    try:
        gate_probe_module._run_live_prompt = fake_run_live_prompt
        probe = gate_probe_module.run_live(
            chunk_size=2,
            requested_genes=["CCDC136", "MITD1"],
            out_json=out_json,
            out_doc=out_doc,
        )
    finally:
        gate_probe_module._run_live_prompt = original

    assert calls == [(gate_probe_module._goal_for_genes(["CCDC136", "MITD1"]), ["CCDC136", "MITD1"])]
    assert probe["coverage"]["coverage_status"] == "complete"
    assert probe["coverage"]["requested_genes"] == ["CCDC136", "MITD1"]
    assert [row["gene"] for row in probe["rows"]] == ["CCDC136", "MITD1"]
    assert out_json.exists()
    assert out_doc.exists()
    assert (ROOT / "examples" / "data" / "campaign_gate_probe.json").read_text() == default_before


def test_campaign_gate_probe_merges_existing_and_followup_decisions():
    existing = build_gate_probe(
        decisions=[{
            "gene": "RCC1L",
            "gate_recommendation": "gate_sufficient",
            "rationale": "Existing decision.",
        }],
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_genes=["RCC1L", "CCDC136"],
    )
    followup = build_gate_probe(
        decisions=[{
            "gene": "CCDC136",
            "gate_recommendation": "add_control",
            "rationale": "Follow-up decision.",
        }],
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_genes=["CCDC136"],
    )

    merged = merge_probe_decisions(existing, followup)

    assert merged == [
        {
            "gene": "RCC1L",
            "gate_recommendation": "gate_sufficient",
            "rationale": "Existing decision.",
        },
        {
            "gene": "CCDC136",
            "gate_recommendation": "add_control",
            "rationale": "Follow-up decision.",
        },
    ]


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
        requested_genes=["RCC1L", "RWDD2B", "CCDC22", "CYB5RL"],
    )

    doc = out_doc.read_text()
    assert probe["rows"][0]["gene"] == "RCC1L"
    assert "Campaign gate probe" in doc
    assert "proposal only" in doc
    assert "gate_sufficient" in doc
    assert "add_control" in doc
    assert "lower_priority" in doc
    assert "python loop/campaign_gate_probe.py --sample" in doc
    assert "Coverage: 4 returned / 4 requested. Complete: yes." in doc
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
    assert json.loads(out_json.read_text())["coverage"]["coverage_status"] == "complete"


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
    assert json.loads(out_json.read_text())["coverage"]["coverage_status"] == "complete"


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
    test_campaign_gate_probe_deduplicates_and_filters_to_requested_genes()
    test_campaign_gate_probe_writes_json_and_markdown(Path("/tmp/prospect-campaign-gate-probe-test"))
    test_campaign_gate_probe_sample_cli_runs_without_api_key(Path("/tmp/prospect-campaign-gate-probe-cli-test"))
    test_campaign_gate_probe_runs_from_prospect_cli(Path("/tmp/prospect-campaign-gate-probe-prospect-test"))
    test_campaign_gate_probe_is_in_public_web_bundle()
    test_campaign_gate_probe_is_visible_in_agent_tab()
    print("PASS: campaign gate probe")
