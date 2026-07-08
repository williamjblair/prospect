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
    "docs/JUDGE_QUICKSTART.md",
    "docs/SUBMISSION_FORM_PACKET.md",
    "docs/SUBMISSION.md",
    "docs/DEMO_RECORDING_RUNBOOK.md",
    "docs/DEMO_TELEPROMPTER.md",
    "docs/JUDGE_HANDOUT.md",
    "docs/FINAL_SUBMISSION_CHECKLIST.md",
    "docs/FINAL_SUBMISSION_AUDIT.md",
    "docs/CAMPAIGN_PROBE_AUDIT.md",
    "docs/GLADSTONE_PILOT_DESIGN.md",
    "docs/JUDGE_PACKET.md",
    "docs/RELEASE_MANIFEST.md",
    "docs/RENDERED_QA_PACKET.md",
]

VERIFICATION_COMMANDS = [
    "./prospect final-check",
    "./prospect submit-smoke",
    "./prospect submit-pack",
    "./prospect demo-pack",
    "./prospect judge-handout",
    "./prospect release-manifest",
    "./prospect rendered-qa",
    "./prospect verify",
    "python benchmark/mutation_pack.py",
    "python tests/test_skill_parity.py",
    "python examples/receipt_bridge_client.py --json",
]

PUBLIC_ARTIFACTS = [
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
    "/data/lab_packet.json",
    "/data/assay_operations_bundle.json",
    "/data/gladstone_pilot_design.json",
    "/data/final_submission_audit.json",
    "/data/release_manifest.json",
    "/data/rendered_qa_packet.json",
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
        "demo_opening": "Start on the A1BG refusal, not the graph.",
        "demo_close": (
            "Receipt bridge, PGGT1B evidence_attached packet, assay operations bundle, "
            "campaign gates, signed state."
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
