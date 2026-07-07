"""README must match the current submission surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_lists_current_commands_and_artifacts():
    text = README.read_text()
    findings = (ROOT / "docs" / "FINDINGS.md").read_text()

    for command in [
        "./prospect verify",
        "./prospect mcp",
        "./prospect campaign",
        "./prospect lab-pack",
        "./prospect judge-pack",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
    ]:
        assert command in text

    for artifact in [
        "/data/frontier.json",
        "/data/judge_packet.json",
        "/data/receipt_bridge/receipt_manifest.json",
        "/data/lab_packet.json",
    ]:
        assert artifact in text

    assert "Five findings" in findings
    assert "Three findings" not in findings


if __name__ == "__main__":
    test_readme_lists_current_commands_and_artifacts()
    print("PASS: README readiness")
