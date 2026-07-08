"""Build the rendered QA packet for the final judge path."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cli.submit_pack import LIVE_URL

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "examples" / "data" / "rendered_qa_packet.json"
OUT_DOC = ROOT / "docs" / "RENDERED_QA_PACKET.md"

LOCAL_URL = "http://localhost:8124"
PUBLIC_ARTIFACT = "/data/rendered_qa_packet.json"

TABS = [
    {
        "tab": "Overview",
        "must_show": ["Opening claim checks", "48%", "Judge packet"],
        "purpose": "Opening refusal, overclaim rate, and replay entry point.",
    },
    {
        "tab": "Findings",
        "must_show": ["Scannable findings index", "Substrate replay packet", "Cross-substrate discovery packet", "MED19"],
        "purpose": "Scientific evidence path, protocol generalization, and cross-substrate discovery.",
    },
    {
        "tab": "Frontier",
        "must_show": ["Executable bridge path", "accepted=false", "human_signature_required"],
        "purpose": "Receipt boundary and no-model-in-trust-path behavior.",
    },
    {
        "tab": "Agent",
        "must_show": ["Campaign pressure summary", "Donor-condition replay packet", "Disease-genetics overlay packet", "Gladstone assay operations bundle", "Gladstone pilot design", "PGGT1B"],
        "purpose": "Claude pressure, donor replay, disease context, proposal-only assay gates, pilot design, and lab handoff.",
    },
]

VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 1000},
    {"name": "mobile", "width": 390, "height": 844},
]


def build_packet() -> dict[str, Any]:
    return {
        "title": "Prospect rendered QA packet",
        "status": "evidence_attached",
        "automation_claim": "manual_browser_checklist",
        "production_url": LIVE_URL,
        "local_url": LOCAL_URL,
        "avoid_port": 3000,
        "public_artifact": PUBLIC_ARTIFACT,
        "optional_browser_command": "./prospect browser-qa --target both",
        "browser_output_dir": "output/playwright/",
        "viewports": VIEWPORTS,
        "tabs": TABS,
        "evidence_commands": [
            "./prospect final-check",
            "./prospect submit-smoke",
            "./prospect rendered-qa",
        ],
        "trust_boundary": {
            "model_role": "none",
            "model_in_trust_path": "no",
            "accepted_state_mutations": 0,
        },
        "pass_criteria": [
            "No tab hides the signed root, typed status, or proposal-only boundaries.",
            "Overview opens on the refusal and overclaiming number, not decoration.",
            "Findings exposes the substrate replay path, cross-substrate discovery packet, and MED19 contrast.",
            "Frontier shows receipt submission as proposal-only.",
            "Agent shows Claude pressure, donor replay, disease context, assay gates, and pilot design, not accepted state.",
            "Text fits at desktop and mobile viewport sizes.",
        ],
        "limitation": "This packet is a manual browser checklist. It does not prove wet-lab or clinical truth.",
    }


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Prospect rendered QA packet",
        "",
        f"Production: [{packet['production_url']}]({packet['production_url']})",
        "",
        f"Local fallback: `{packet['local_url']}`",
        "",
        f"Avoid local port: `{packet['avoid_port']}`",
        "",
        "## Manual browser checklist",
        "",
        "This packet makes the final browser pass durable. It does not claim automated visual inspection.",
        "",
        "## Viewports",
        "",
        "| name | width | height |",
        "|---|---:|---:|",
    ]
    for viewport in packet["viewports"]:
        lines.append(f"| {viewport['name']} | {viewport['width']} | {viewport['height']} |")
    lines += [
        "",
        "## Tabs",
        "",
        "| tab | must show | purpose |",
        "|---|---|---|",
    ]
    for item in packet["tabs"]:
        must_show = ", ".join(f"`{value}`" for value in item["must_show"])
        lines.append(f"| {item['tab']} | {must_show} | {item['purpose']} |")
    lines += [
        "",
        "## Evidence commands",
        "",
    ]
    lines += [f"- `{command}`" for command in packet["evidence_commands"]]
    lines += [
        "",
        "## Optional browser smoke",
        "",
        "After starting the local web server on `8124`, run:",
        "",
        "```bash",
        packet["optional_browser_command"],
        "```",
        "",
        f"This writes local evidence under ignored `{packet['browser_output_dir']}`.",
    ]
    lines += [
        "",
        "## Pass criteria",
        "",
    ]
    lines += [f"- {criterion}" for criterion in packet["pass_criteria"]]
    lines += [
        "",
        packet["limitation"],
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect rendered-qa",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_packet(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect rendered-qa")
    parser.add_argument("--json", action="store_true", help="print the rendered QA packet as JSON")
    args = parser.parse_args(argv)

    packet = write_packet()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"status {packet['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
