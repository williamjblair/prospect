"""Build the final submission audit packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cli.submit_pack import LIVE_URL, PUBLIC_ARTIFACTS, REPO_URL, SIGNED_ROOT, SOURCE_DOCS

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "examples" / "data" / "final_submission_audit.json"
OUT_DOC = ROOT / "docs" / "FINAL_SUBMISSION_AUDIT.md"

REQUIRED_GATES = [
    "./prospect final-check",
    "./prospect submit-smoke",
    "./prospect submit-pack",
    "./prospect demo-pack",
    "./prospect judge-handout",
    "./prospect verify",
    "python benchmark/mutation_pack.py",
    "python tests/test_skill_parity.py",
    "python examples/receipt_bridge_client.py --json",
]

SHIPPED_WORKSTREAMS = [
    {
        "workstream": "submission_floor",
        "state": "shipped",
        "evidence": ["./prospect final-check", "./prospect submit-smoke", "root_a8b0dcdd4024e12f"],
    },
    {
        "workstream": "second_substrate_replay",
        "state": "shipped",
        "evidence": ["./prospect substrate-replay", "/data/substrate_replay_packet.json"],
    },
    {
        "workstream": "claude_campaign_pressure",
        "state": "shipped",
        "evidence": ["./prospect campaign-pressure", "/data/campaign_pressure_summary.json"],
    },
    {
        "workstream": "gladstone_assay_operations",
        "state": "shipped",
        "evidence": ["./prospect assay-ops", "/data/assay_operations_bundle.json"],
    },
    {
        "workstream": "demo_and_submission_packets",
        "state": "shipped",
        "evidence": ["./prospect demo-pack", "./prospect submit-pack", "docs/FINAL_SUBMISSION_CHECKLIST.md"],
    },
]

HUMAN_ONLY_ACTIONS = [
    "record_demo_video",
    "submit_project_form",
    "wet_lab_execution",
]


def build_audit() -> dict[str, Any]:
    return {
        "title": "Prospect final submission audit",
        "readiness": "submission_ready_for_human_upload",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "public_artifact_count": len(PUBLIC_ARTIFACTS),
        "public_artifacts": PUBLIC_ARTIFACTS,
        "source_docs": SOURCE_DOCS,
        "required_gates": REQUIRED_GATES,
        "shipped_workstreams": SHIPPED_WORKSTREAMS,
        "trust_boundary": {
            "model_role": "propose_search_pressure_test",
            "model_in_trust_path": "no",
            "accepted_state_gate": "frozen_replay_plus_human_ed25519_signature",
            "model_accepted_state_mutations": 0,
        },
        "human_only_actions": HUMAN_ONLY_ACTIONS,
        "limitation": "Prospect proves computation over released data, not wet-lab or clinical truth.",
    }


def _markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Prospect final submission audit",
        "",
        f"Readiness: `{audit['readiness']}`.",
        "",
        f"Live: [{audit['live_url']}]({audit['live_url']})",
        "",
        f"Repo: [{audit['repo_url']}]({audit['repo_url']})",
        "",
        f"Signed root: `{audit['signed_root']}`",
        "",
        f"Public artifacts: {audit['public_artifact_count']}",
        "",
        "## Trust boundary",
        "",
        f"- Model role: `{audit['trust_boundary']['model_role']}`",
        f"- Model in trust path: `{audit['trust_boundary']['model_in_trust_path']}`",
        f"- Accepted-state gate: `{audit['trust_boundary']['accepted_state_gate']}`",
        f"- Model accepted-state mutations: {audit['trust_boundary']['model_accepted_state_mutations']}",
        "",
        "## Required gates before upload",
        "",
    ]
    lines += [f"- `{command}`" for command in audit["required_gates"]]
    lines += [
        "",
        "## Source docs",
        "",
    ]
    lines += [f"- `{path}`" for path in audit["source_docs"]]
    lines += [
        "",
        "## Shipped workstreams",
        "",
        "| workstream | state | evidence |",
        "|---|---|---|",
    ]
    for item in audit["shipped_workstreams"]:
        evidence = ", ".join(f"`{value}`" for value in item["evidence"])
        lines.append(f"| {item['workstream']} | {item['state']} | {evidence} |")
    lines += [
        "",
        "## Public artifacts",
        "",
    ]
    lines += [f"- `{path}`" for path in audit["public_artifacts"]]
    lines += [
        "",
        "## Human-only actions",
        "",
    ]
    lines += [f"- `{action}`" for action in audit["human_only_actions"]]
    lines += [
        "",
        audit["limitation"],
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect submission-audit",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_audit(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    audit = build_audit()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, indent=2) + "\n")
    out_doc.write_text(_markdown(audit))
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect submission-audit")
    parser.add_argument("--json", action="store_true", help="print the audit as JSON")
    args = parser.parse_args(argv)

    audit = write_audit()
    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"readiness {audit['readiness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
