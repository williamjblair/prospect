"""Print a copy-safe packet for the final hackathon submission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROJECT_TITLE = "Prospect"
LIVE_URL = "https://prospect-sepia-six.vercel.app"
REPO_URL = "https://github.com/williamjblair/prospect"
SIGNED_ROOT = "root_a8b0dcdd4024e12f"

SOURCE_DOCS = [
    "README.md",
    "docs/SUBMISSION.md",
    "docs/DEMO.md",
    "docs/DEMO_RECORDING_RUNBOOK.md",
    "docs/DEPLOY_READINESS.md",
    "docs/RIGOR_AUDIT.md",
    "docs/FINDINGS.md",
    "docs/PROTOCOL.md",
    "docs/JUDGE_TECHNICAL_NOTE.md",
    "docs/RECEIPT_BRIDGE.md",
    "docs/RECEIPT_SCHEMA.md",
    "docs/SUBSTRATE_COVERAGE.md",
    "docs/PGGT1B_DEFENDED_EVIDENCE.md",
    "docs/GSE278572_COMPARATOR.md",
    "docs/JUDGE_HANDOUT.md",
]

VERIFICATION_COMMANDS = [
    "./prospect verify",
    "python benchmark/mutation_pack.py",
    "python tests/test_skill_parity.py",
    "python tests/test_marson.py",
    "python examples/receipt_bridge_client.py --json",
    "python examples/claude_science_connector_client.py --json",
    "python examples/prospect_connector_client.py --case openresearch --json",
    "python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json",
    "python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json",
    "python receipt/replay_proposal.py <proposal.json-or-url>",
    "./prospect demo-mode --reset",
    "./prospect demo-reset",
    "./prospect deploy-checklist",
    "./prospect rigor-audit",
    "./prospect substrate-coverage",
    "./prospect pggt1b-defended-evidence",
    "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
]

PUBLIC_ARTIFACTS = [
    "/data/check.json",
    "/data/frontier.json",
    "/data/finding_index.json",
    "/data/receipt_bridge/receipt_contract.json",
    "/data/receipt_bridge/receipt_manifest.json",
    "/data/receipt_bridge/receipt_bundle.json",
    "/data/claude_science_acceptance_demo.json",
    "/data/gse278572_comparator.json",
    "/data/pggt1b_defended_evidence.json",
    "/data/overclaim_counter.json",
]


def _ensure_source_docs_exist() -> None:
    missing = [path for path in SOURCE_DOCS if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError("missing submission source docs: " + ", ".join(missing))


def build_packet() -> dict[str, object]:
    _ensure_source_docs_exist()
    return {
        "project_title": PROJECT_TITLE,
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "source_docs": SOURCE_DOCS,
        "verification_commands": VERIFICATION_COMMANDS,
        "public_artifacts": PUBLIC_ARTIFACTS,
        "demo_opening": "Start on the real Claude Science export entering Prospect: reproducible is not verified.",
        "demo_close": (
            "Run your own claim, receipt bridge, PGGT1B protocol, and the human-only acceptance step."
        ),
        "limitations": (
            "Prospect proves computation over released data, not wet-lab or clinical truth. "
            "No model is in the trust path."
        ),
        "secret_warning": "Do not paste secrets.",
    }


def _print_text(packet: dict[str, object]) -> None:
    print("Prospect submission packet")
    print("")
    print(f"Project title: {packet['project_title']}")
    print(f"Live URL: {packet['live_url']}")
    print(f"Repo URL: {packet['repo_url']}")
    print(f"Signed root: {packet['signed_root']}")
    print("")
    print("Copy source docs:")
    for path in packet["source_docs"]:
        print(f"- {path}")
    print("")
    print("Run before upload:")
    for command in packet["verification_commands"]:
        print(f"- {command}")
    print("")
    print("Public artifacts:")
    for artifact in packet["public_artifacts"]:
        print(f"- {packet['live_url']}{artifact}")
    print("")
    print(f"Demo opening: {packet['demo_opening']}")
    print(f"Demo close: {packet['demo_close']}")
    print(f"Limitations: {packet['limitations']}")
    print(packet["secret_warning"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect submit-pack")
    parser.add_argument("--json", action="store_true", help="emit the packet as JSON")
    args = parser.parse_args(argv)

    packet = build_packet()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        _print_text(packet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
