"""README must match the current submission surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_lists_current_commands_and_artifacts():
    text = README.read_text()
    findings = (ROOT / "docs" / "FINDINGS.md").read_text()

    for command in [
        "./prospect verify",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect mcp",
        "python examples/receipt_bridge_client.py",
        "./prospect campaign",
        "./prospect campaign-probe",
        "./prospect campaign-triage",
        "./prospect campaign-gate-probe",
        "./prospect transfer-replay",
        "./prospect lab-pack",
        "./prospect judge-pack",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
    ]:
        assert command in text

    for artifact in [
        "/data/frontier.json",
        "/data/judge_packet.json",
        "/data/finding_index.json",
        "/data/receipt_bridge/receipt_contract.json",
        "/data/receipt_bridge/receipt_manifest.json",
        "/data/receipt_bridge/receipt_bundle.json",
        "/data/pggt1b_deep_dive.json",
        "/data/campaign_agent_probe.json",
        "/data/agent_campaign.json",
        "/data/agent_campaign_review.json",
        "/data/campaign_triage.json",
        "/data/campaign_gate_probe.json",
        "/data/transfer_replay_packet.json",
        "/data/lab_packet.json",
    ]:
        assert artifact in text

    assert "Five findings" in findings
    assert "Three findings" not in findings
    assert "docs/GLADSTONE_ASSAY_HANDOFF.md" in text
    assert "docs/TRANSFER_REPLAY_PACKET.md" in text
    assert "docs/FINAL_SUBMISSION_CHECKLIST.md" in text
    assert "docs/DEMO_TELEPROMPTER.md" in text


if __name__ == "__main__":
    test_readme_lists_current_commands_and_artifacts()
    print("PASS: README readiness")
