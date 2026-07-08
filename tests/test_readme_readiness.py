"""README must match the current submission surface."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.submit_pack import PUBLIC_ARTIFACTS

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
        "./prospect judge-handout",
        "./prospect submission-audit",
        "./prospect release-manifest",
        "./prospect rendered-qa",
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

    for artifact in PUBLIC_ARTIFACTS:
        assert artifact in text

    assert "Five findings" in findings
    assert "Three findings" not in findings
    assert "docs/GLADSTONE_ASSAY_HANDOFF.md" in text
    assert "docs/TRANSFER_REPLAY_PACKET.md" in text
    assert "docs/FINAL_SUBMISSION_CHECKLIST.md" in text
    assert "docs/DEMO_TELEPROMPTER.md" in text
    assert "docs/JUDGE_HANDOUT.md" in text


if __name__ == "__main__":
    test_readme_lists_current_commands_and_artifacts()
    print("PASS: README readiness")
