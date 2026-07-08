"""Build the one-page judge handout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cli.final_submission_audit import HUMAN_ONLY_ACTIONS
from cli.submit_pack import LIVE_URL, PUBLIC_ARTIFACTS, REPO_URL, SIGNED_ROOT

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT_DOC = ROOT / "docs" / "JUDGE_HANDOUT.md"


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def build_handout() -> dict[str, Any]:
    judge = _json(DATA / "judge_packet.json")
    campaign = _json(DATA / "campaign_pressure_summary.json")
    assay = _json(DATA / "assay_operations_bundle.json")
    pilot = _json(DATA / "gladstone_pilot_design.json")
    substrate = _json(DATA / "substrate_replay_packet.json")
    discovery = _json(DATA / "cross_substrate_discovery.json")

    return {
        "title": "Prospect one-page judge handout",
        "readiness": "submission_ready_for_human_upload",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "thesis": (
            "Claude makes scientific activity cheap; Prospect decides what becomes replayable, "
            "human-accepted state."
        ),
        "counts": {
            "public_artifacts": len(PUBLIC_ARTIFACTS),
            "findings": judge["artifact_counts"]["findings"],
            "receipts": judge["artifact_counts"]["receipts"],
            "claude_probe_rows": campaign["counts"]["claude_probe_rows"],
            "gate_probe_returned": campaign["gate_probe_coverage"]["returned_decisions"],
            "gate_probe_requested": campaign["gate_probe_coverage"]["requested_limit"],
            "gate_probe_coverage_status": campaign["gate_probe_coverage"]["coverage_status"],
            "assay_operations_candidates": len(assay["candidates"]),
            "pilot_design_culture_arms": pilot["sample_plan"]["culture_arms"],
            "substrate_replay_rows": substrate["counts"]["t_cell_regulators_compared"],
            "cross_substrate_discovery_rows": discovery["counts"]["marson_genes_considered"],
            "cross_substrate_t_cell_candidates": discovery["class_counts"]["t_cell_specific_activation"],
        },
        "trust_boundary": {
            "model_role": "propose_search_pressure_test",
            "model_in_trust_path": "no",
            "accepted_state": "human_signed_replayable_root",
            "model_accepted_state_mutations": 0,
        },
        "five_minute_path": [
            "Overview: A1BG refusal and 48 percent overclaiming number.",
            "Findings: signed CD4+ T-cell findings that recover known biology and catch overclaims.",
            "Findings: substrate replay across Marson CD4+ T cells, Replogle K562, and Replogle RPE1.",
            "Findings: cross-substrate discovery classifies shared machinery and T-cell-specific candidates.",
            "Frontier: receipt bridge returns proposal-only submission, not accepted state.",
            "Agent: Claude pressure becomes assay gates, then PGGT1B, assay operations, and pilot design show the lab handoff.",
        ],
        "public_artifacts_to_open": [
            "/data/judge_packet.json",
            "/data/campaign_pressure_summary.json",
            "/data/substrate_replay_packet.json",
            "/data/cross_substrate_discovery.json",
            "/data/assay_operations_bundle.json",
            "/data/gladstone_pilot_design.json",
            "/data/final_submission_audit.json",
            "/data/release_manifest.json",
            "/data/rendered_qa_packet.json",
        ],
        "commands": [
            "./prospect final-check",
            "./prospect submit-smoke",
            "./prospect submit-pack",
            "./prospect demo-pack",
            "python examples/receipt_bridge_client.py --json",
        ],
        "human_only_actions": HUMAN_ONLY_ACTIONS,
        "limitation": "Prospect proves computation over released data, not wet-lab or clinical truth.",
    }


def _markdown(handout: dict[str, Any]) -> str:
    counts = handout["counts"]
    lines = [
        "# Prospect one-page judge handout",
        "",
        f"Live: [{handout['live_url']}]({handout['live_url']})",
        "",
        f"Repo: [{handout['repo_url']}]({handout['repo_url']})",
        "",
        f"Signed root: `{handout['signed_root']}`",
        "",
        "## What Prospect proves",
        "",
        handout["thesis"],
        "",
        handout["limitation"],
        "",
        "## Numbers to inspect",
        "",
        f"- {counts['findings']} signed findings",
        f"- {counts['receipts']} portable receipts",
        f"- {counts['public_artifacts']} public data artifacts",
        f"- {counts['substrate_replay_rows']} replayed T-cell regulators across three frozen substrates",
        f"- {counts['cross_substrate_discovery_rows']} Marson rows classified against non-immune substrates",
        f"- {counts['cross_substrate_t_cell_candidates']} T-cell-specific activation candidates",
        f"- {counts['claude_probe_rows']} Claude probe rows in the pressure loop",
        (
            f"- {counts['gate_probe_returned']} of {counts['gate_probe_requested']} gate-probe decisions returned, "
            f"coverage `{counts['gate_probe_coverage_status']}`"
        ),
        f"- {counts['assay_operations_candidates']} proposal-only assay operations rows",
        f"- {counts['pilot_design_culture_arms']} proposal-only pilot culture arms",
        "",
        "## Trust boundary",
        "",
        f"- Model role: `{handout['trust_boundary']['model_role']}`",
        f"- Model in trust path: `{handout['trust_boundary']['model_in_trust_path']}`",
        f"- Accepted state: `{handout['trust_boundary']['accepted_state']}`",
        f"- Model accepted-state mutations: {handout['trust_boundary']['model_accepted_state_mutations']}",
        "",
        "## Five-minute judge path",
        "",
    ]
    lines += [f"{idx}. {step}" for idx, step in enumerate(handout["five_minute_path"], start=1)]
    lines += [
        "",
        "## Public artifacts to open",
        "",
    ]
    lines += [f"- `{path}`" for path in handout["public_artifacts_to_open"]]
    lines += [
        "",
        "## Replay commands",
        "",
    ]
    lines += [f"- `{command}`" for command in handout["commands"]]
    lines += [
        "",
        "## What remains human-only",
        "",
    ]
    lines += [f"- `{action}`" for action in handout["human_only_actions"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect judge-handout",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_handout(out_doc: Path = OUT_DOC) -> dict[str, Any]:
    handout = build_handout()
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_doc.write_text(_markdown(handout))
    return handout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect judge-handout")
    parser.add_argument("--json", action="store_true", help="print the handout packet as JSON")
    args = parser.parse_args(argv)

    handout = write_handout()
    if args.json:
        print(json.dumps(handout, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_DOC}")
    print(f"readiness {handout['readiness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
