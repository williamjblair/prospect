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
    "./prospect release-manifest",
    "./prospect rendered-qa",
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
        "evidence": ["./prospect campaign-pressure", "./prospect campaign-probe-audit", "/data/campaign_pressure_summary.json", "/data/campaign_probe_audit.json"],
    },
    {
        "workstream": "gladstone_assay_operations",
        "state": "shipped",
        "evidence": ["./prospect assay-ops", "./prospect pilot-design", "/data/assay_operations_bundle.json", "/data/gladstone_pilot_design.json"],
    },
    {
        "workstream": "demo_and_submission_packets",
        "state": "shipped",
        "evidence": ["./prospect demo-pack", "./prospect submit-pack", "docs/FINAL_SUBMISSION_CHECKLIST.md"],
    },
    {
        "workstream": "public_release_manifest",
        "state": "shipped",
        "evidence": ["./prospect release-manifest", "/data/release_manifest.json"],
    },
    {
        "workstream": "rendered_qa_packet",
        "state": "shipped",
        "evidence": ["./prospect rendered-qa", "/data/rendered_qa_packet.json"],
    },
]

HUMAN_ONLY_ACTIONS = [
    "record_demo_video",
    "submit_project_form",
    "wet_lab_execution",
]

RENDERED_QA_CHECKLIST = {
    "production_url": LIVE_URL,
    "local_url": "http://localhost:8124",
    "avoid_port": 3000,
    "tabs": [
        {
            "tab": "Overview",
            "must_show": ["Opening claim checks", "48%", "Judge packet"],
        },
        {
            "tab": "Findings",
            "must_show": ["Scannable findings index", "Substrate replay packet", "MED19"],
        },
        {
            "tab": "Frontier",
            "must_show": ["Executable bridge path", "accepted=false", "human_signature_required"],
        },
        {
            "tab": "Agent",
            "must_show": ["Campaign pressure summary", "Gladstone assay operations bundle", "Gladstone pilot design", "PGGT1B"],
        },
    ],
}

COMPLETION_REQUIREMENTS = [
    {
        "requirement": "p0_floor_green",
        "status": "satisfied",
        "evidence": ["./prospect final-check", "./prospect submit-smoke"],
    },
    {
        "requirement": "protocol_generalization",
        "status": "shipped",
        "evidence": ["./prospect substrate-replay", "/data/substrate_replay_packet.json"],
    },
    {
        "requirement": "claude_campaign_pressure",
        "status": "shipped",
        "evidence": ["./prospect campaign-pressure", "./prospect campaign-probe-audit", "/data/campaign_pressure_summary.json", "/data/campaign_probe_audit.json"],
    },
    {
        "requirement": "gladstone_assay_operations",
        "status": "shipped",
        "evidence": ["./prospect assay-ops", "./prospect pilot-design", "/data/assay_operations_bundle.json", "/data/gladstone_pilot_design.json"],
    },
    {
        "requirement": "demo_submission_packets",
        "status": "shipped",
        "evidence": ["./prospect demo-pack", "./prospect submit-pack", "./prospect judge-handout"],
    },
    {
        "requirement": "public_release_manifest",
        "status": "shipped",
        "evidence": ["./prospect release-manifest", "/data/release_manifest.json", "./prospect submit-smoke"],
    },
    {
        "requirement": "rendered_qa_packet",
        "status": "shipped",
        "evidence": ["./prospect rendered-qa", "/data/rendered_qa_packet.json"],
    },
    {
        "requirement": "public_production_surface",
        "status": "satisfied",
        "evidence": [LIVE_URL, "./prospect submit-smoke", "/data/final_submission_audit.json", "/data/release_manifest.json", "/data/rendered_qa_packet.json"],
    },
    {
        "requirement": "human_upload",
        "status": "human_only_remaining",
        "evidence": ["record_demo_video", "submit_project_form"],
    },
    {
        "requirement": "wet_lab_execution",
        "status": "human_only_remaining",
        "evidence": ["wet_lab_execution"],
    },
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
        "rendered_qa_checklist": RENDERED_QA_CHECKLIST,
        "completion_requirements": COMPLETION_REQUIREMENTS,
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
    qa = audit["rendered_qa_checklist"]
    lines += [
        "",
        "## Rendered QA checklist",
        "",
        f"- Production URL: [{qa['production_url']}]({qa['production_url']})",
        f"- Local fallback: `{qa['local_url']}`",
        f"- Avoid local port: `{qa['avoid_port']}`",
        "",
        "| tab | must show |",
        "|---|---|",
    ]
    for item in qa["tabs"]:
        must_show = ", ".join(f"`{value}`" for value in item["must_show"])
        lines.append(f"| {item['tab']} | {must_show} |")
    lines += [
        "",
        "## Completion requirements",
        "",
        "| requirement | status | evidence |",
        "|---|---|---|",
    ]
    for item in audit["completion_requirements"]:
        evidence = ", ".join(f"`{value}`" for value in item["evidence"])
        lines.append(f"| {item['requirement']} | {item['status']} | {evidence} |")
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
