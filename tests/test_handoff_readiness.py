"""Root handoff docs must match the current submission command surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
HANDOFF = ROOT / "docs" / "HANDOFF.md"


def test_agents_lists_current_cli_surface():
    text = AGENTS.read_text()

    for command in [
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect verify",
        "./prospect campaign-probe",
        "./prospect campaign-triage",
        "./prospect campaign-gate-probe",
        "./prospect transfer-replay",
        "./prospect pggt1b",
        "./prospect lab-pack",
        "./prospect assay-ops",
        "./prospect judge-pack",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect submission-audit",
        "./prospect release-manifest",
        "python examples/receipt_bridge_client.py --json",
    ]:
        assert command in text

    for verb in [
        "campaign-gate-probe",
        "transfer-replay",
        "lab-pack",
        "assay-ops",
        "final-check",
        "submit-smoke",
        "submit-pack",
        "submission-audit",
        "release-manifest",
        "mcp",
    ]:
        assert verb in text


def test_handoff_describes_current_production_smoke_gate():
    text = HANDOFF.read_text()

    for phrase in [
        "`./prospect submit-smoke`",
        "judge packet command",
        "exact public-data parity",
        "shared `submit-pack` manifest",
        "all public artifact",
        "campaign gate probe",
        "transfer replay packet",
        "lab packet",
        "receipt bridge manifest",
        "release manifest hashes",
    ]:
        assert phrase in text


def test_handoff_points_to_judge_quickstart():
    text = HANDOFF.read_text()

    for phrase in [
        "[JUDGE_QUICKSTART.md](JUDGE_QUICKSTART.md)",
        "five-minute judge path",
        "`./prospect submit-pack`",
        "release-manifest",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_agents_lists_current_cli_surface()
    test_handoff_describes_current_production_smoke_gate()
    test_handoff_points_to_judge_quickstart()
    print("PASS: handoff readiness")
