"""Submission text must point judges at current artifacts."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.submit_pack import PUBLIC_ARTIFACTS

SUBMISSION = ROOT / "docs" / "SUBMISSION.md"


def test_submission_lists_current_replay_and_artifact_commands():
    text = SUBMISSION.read_text()

    for command in [
        "./prospect verify",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect judge-handout",
        "./prospect submission-audit",
        "./prospect release-manifest",
        "./prospect rendered-qa",
        "./prospect browser-qa --target both",
        "./prospect mcp",
        "python examples/receipt_bridge_client.py",
        "./prospect campaign",
        "./prospect campaign-probe",
        "./prospect campaign-triage",
        "./prospect campaign-gate-probe",
        "./prospect transfer-replay",
        "./prospect lab-pack",
        "./prospect assay-ops",
        "./prospect pilot-design",
        "./prospect judge-pack",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
    ]:
        assert command in text

    assert "remaining gates" not in text
    assert "complete gate coverage" in text


def test_submission_points_to_current_public_artifacts():
    text = SUBMISSION.read_text()

    for artifact in PUBLIC_ARTIFACTS:
        assert artifact in text

    assert "GLADSTONE_ASSAY_HANDOFF.md" in text
    assert "TRANSFER_REPLAY_PACKET.md" in text
    assert "FINAL_SUBMISSION_CHECKLIST.md" in text
    assert "FINAL_SUBMISSION_AUDIT.md" in text
    assert "DEMO_TELEPROMPTER.md" in text
    assert "JUDGE_HANDOUT.md" in text


def test_submission_names_durable_build_track_artifact():
    text = SUBMISSION.read_text()

    for phrase in [
        "What outlasts the week",
        "skeptical immunologist or computational biologist",
        "working software",
        "replayable CLI",
        "public data endpoints",
        "receipt bridge",
        "wet-lab handoff",
        "human signature",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_submission_lists_current_replay_and_artifact_commands()
    test_submission_points_to_current_public_artifacts()
    test_submission_names_durable_build_track_artifact()
    print("PASS: submission readiness")
