"""Submission text must point judges at current artifacts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "docs" / "SUBMISSION.md"


def test_submission_lists_current_replay_and_artifact_commands():
    text = SUBMISSION.read_text()

    for command in [
        "./prospect verify",
        "./prospect mcp",
        "python examples/receipt_bridge_client.py",
        "./prospect campaign",
        "./prospect campaign-probe",
        "./prospect campaign-triage",
        "./prospect lab-pack",
        "./prospect judge-pack",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
    ]:
        assert command in text


def test_submission_points_to_current_public_artifacts():
    text = SUBMISSION.read_text()

    for artifact in [
        "/data/frontier.json",
        "/data/judge_packet.json",
        "/data/receipt_bridge/receipt_manifest.json",
        "/data/pggt1b_matrix_slice.json",
        "/data/campaign_agent_probe.json",
        "/data/campaign_triage.json",
        "/data/lab_packet.json",
    ]:
        assert artifact in text

    assert "GLADSTONE_ASSAY_HANDOFF.md" in text


if __name__ == "__main__":
    test_submission_lists_current_replay_and_artifact_commands()
    test_submission_points_to_current_public_artifacts()
    print("PASS: submission readiness")
