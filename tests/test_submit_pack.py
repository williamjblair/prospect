"""Copy-safe submission packet CLI contract."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cli.submit_pack import build_packet


def test_submit_pack_includes_copy_safe_submission_fields():
    packet = build_packet()

    assert packet["project_title"] == "Prospect"
    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["repo_url"] == "https://github.com/williamjblair/prospect"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"
    assert "ANTHROPIC_API_KEY" not in json.dumps(packet)

    for command in [
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect release-manifest",
        "./prospect verify",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
        "python examples/receipt_bridge_client.py --json",
    ]:
        assert command in packet["verification_commands"]

    assert packet["optional_operator_commands"] == [
        "cd web && npm run start",
        "./prospect browser-qa --target both",
    ]

    for path in [
        "docs/SUBMISSION_FORM_PACKET.md",
        "docs/DEMO_RECORDING_RUNBOOK.md",
        "docs/DEMO_TELEPROMPTER.md",
        "docs/JUDGE_HANDOUT.md",
        "docs/FINAL_SUBMISSION_CHECKLIST.md",
        "docs/FINAL_SUBMISSION_AUDIT.md",
        "docs/CAMPAIGN_PROBE_AUDIT.md",
        "docs/CROSS_SUBSTRATE_DISCOVERY.md",
        "docs/RELEASE_MANIFEST.md",
        "docs/RENDERED_QA_PACKET.md",
    ]:
        assert path in packet["source_docs"]


def test_submit_pack_lists_full_judge_public_artifact_surface():
    packet = build_packet()
    expected = [
        "/data/frontier.json",
        "/data/judge_packet.json",
        "/data/finding_index.json",
        "/data/receipt_bridge/receipt_contract.json",
        "/data/receipt_bridge/receipt_manifest.json",
        "/data/receipt_bridge/receipt_bundle.json",
        "/data/pggt1b_deep_dive.json",
        "/data/pggt1b_matrix_slice.json",
        "/data/agent_campaign.json",
        "/data/agent_campaign_review.json",
        "/data/campaign_agent_probe.json",
        "/data/campaign_probe_audit.json",
        "/data/campaign_triage.json",
        "/data/campaign_gate_probe.json",
        "/data/campaign_pressure_summary.json",
        "/data/transfer_replay_packet.json",
        "/data/substrate_replay_packet.json",
        "/data/cross_substrate_discovery.json",
        "/data/lab_packet.json",
        "/data/assay_operations_bundle.json",
        "/data/gladstone_pilot_design.json",
        "/data/final_submission_audit.json",
        "/data/release_manifest.json",
        "/data/rendered_qa_packet.json",
    ]

    assert packet["public_artifacts"] == expected


def test_submit_pack_cli_prints_human_packet():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submit-pack"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "Prospect submission packet" in proc.stdout
    assert "Live URL: https://prospect-sepia-six.vercel.app" in proc.stdout
    assert "Signed root: root_a8b0dcdd4024e12f" in proc.stdout
    assert "./prospect submit-smoke" in proc.stdout
    assert "./prospect submit-pack" in proc.stdout
    assert "./prospect demo-pack" in proc.stdout
    assert "./prospect browser-qa --target both" in proc.stdout
    assert "Do not paste secrets." in proc.stdout


def test_submit_pack_cli_can_emit_json():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submit-pack", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    packet = json.loads(proc.stdout)
    assert packet["project_title"] == "Prospect"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"


if __name__ == "__main__":
    test_submit_pack_includes_copy_safe_submission_fields()
    test_submit_pack_lists_full_judge_public_artifact_surface()
    test_submit_pack_cli_prints_human_packet()
    test_submit_pack_cli_can_emit_json()
    print("PASS: submit pack")
