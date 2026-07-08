"""Campaign probe audit tests.

The audit is deterministic review over a proposal-only campaign probe artifact.
It catches promotion blockers that do not require another model call.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop.campaign_probe import build_probe
from loop.campaign_probe_audit import audit_probe, write_audit


def _write_probe(path: Path, decisions: list[dict[str, str]], requested_genes: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    probe = build_probe(
        decisions=decisions,
        model="claude-opus-4-8",
        tool_calls=[],
        cost_usd=0.0,
        requested_limit=len(requested_genes),
        requested_genes=requested_genes,
    )
    path.write_text(json.dumps(probe, indent=2) + "\n")


def test_campaign_probe_audit_accepts_committed_probe_shape():
    audit = audit_probe(ROOT / "examples" / "data" / "campaign_agent_probe.json")

    assert audit["status"] == "computationally_reproduced"
    assert audit["trust_boundary"] == "frozen_audit_over_probe_artifact"
    assert audit["model_in_trust_path"] == "no"
    assert audit["accepted_state_mutations"] == 0
    assert audit["passed"] == "yes"
    assert audit["issue_count"] == 0
    assert audit["coverage"]["coverage_status"] == "complete"


def test_campaign_probe_audit_flags_rationale_that_contradicts_frozen_kd(tmp_path):
    probe_path = tmp_path / "bad_probe.json"
    _write_probe(
        probe_path,
        decisions=[
            {
                "gene": "CCDC136",
                "recommendation": "hold_as_ranked_backup",
                "rationale": "The regulator profile shows no on-target KD in any condition.",
            }
        ],
        requested_genes=["CCDC136"],
    )

    audit = audit_probe(probe_path)

    assert audit["passed"] == "no"
    assert audit["issue_count"] == 1
    assert audit["issues"][0]["gene"] == "CCDC136"
    assert audit["issues"][0]["issue_type"] == "rationale_contradicts_frozen_kd"
    assert "Stim48hr" in audit["issues"][0]["frozen_fact"]


def test_campaign_probe_audit_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "campaign_probe_audit.json"
    out_doc = tmp_path / "CAMPAIGN_PROBE_AUDIT.md"

    audit = write_audit(out_json=out_json, out_doc=out_doc)

    doc = out_doc.read_text()
    assert audit["passed"] == "yes"
    assert "Campaign probe audit" in doc
    assert "frozen audit over proposal-only model pressure" in doc
    assert "No accepted state changes" in doc
    assert "rationale_contradicts_frozen_kd" in doc
    assert "verified" not in json.dumps(audit).lower()
    assert "true" not in json.dumps(audit).lower()


def test_campaign_probe_audit_runs_from_prospect_cli(tmp_path):
    out_json = tmp_path / "campaign_probe_audit.json"
    out_doc = tmp_path / "CAMPAIGN_PROBE_AUDIT.md"
    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "campaign-probe-audit",
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
    assert "campaign_probe_audit.json" in proc.stdout
    assert json.loads(out_json.read_text())["passed"] == "yes"


if __name__ == "__main__":
    test_campaign_probe_audit_accepts_committed_probe_shape()
    test_campaign_probe_audit_flags_rationale_that_contradicts_frozen_kd(Path("/tmp/prospect-campaign-probe-audit-bad"))
    test_campaign_probe_audit_writes_json_and_markdown(Path("/tmp/prospect-campaign-probe-audit-write"))
    test_campaign_probe_audit_runs_from_prospect_cli(Path("/tmp/prospect-campaign-probe-audit-cli"))
    print("PASS: campaign probe audit")
