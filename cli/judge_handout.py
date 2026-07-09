"""Build the one-page judge handout from the kept, signed surfaces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cli.submit_pack import LIVE_URL, PUBLIC_ARTIFACTS, REPO_URL, SIGNED_ROOT

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
FRONTIER = ROOT / "frontier"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"
OUT_DOC = ROOT / "docs" / "JUDGE_HANDOUT.md"

# The trust boundary: these stay a human key-custody decision, never a model's.
HUMAN_ONLY_ACTIONS = [
    "sign the frontier root",
    "accept a submitted receipt",
    "sign an agent or campaign hypothesis",
    "wet-lab execution",
]


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _jsonl(path: Path) -> list[Any]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def build_handout() -> dict[str, Any]:
    campaign = _json(DATA / "agent_campaign.json")
    disease = _json(DATA / "disease_genetics_overlay.json")
    lab = _json(DATA / "lab_packet.json")
    claude_science = _json(DATA / "claude_science_acceptance_demo.json")
    substrate = _json(DATA / "substrate_coverage_report.json")
    pggt1b = _json(DATA / "pggt1b_defended_evidence.json")
    endgame = _json(DATA / "defended_discovery_endgame_result.json")
    index = _json(DATA / "finding_index.json")
    findings = _jsonl(FRONTIER / "findings.jsonl")
    receipts = _jsonl(RECEIPTS)

    return {
        "title": "Prospect one-page judge handout",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "thesis": (
            "Claude makes scientific activity cheap; Prospect decides what becomes replayable, "
            "human-accepted state."
        ),
        "counts": {
            "public_artifacts": len(PUBLIC_ARTIFACTS),
            "findings": len(findings),
            "receipts": len(receipts),
            "finding_index_rows": len(index.get("items", [])),
            "campaign_rows": len(campaign.get("candidates", [])),
            "disease_overlay_rows": disease["counts"]["campaign_rows"],
            "disease_overlay_context_rows": disease["counts"]["immune_or_hematologic_context"],
            "lab_packet_rows": len(lab.get("candidates", [])),
            "claude_science_genes": claude_science["prospect"]["typed_status_counts"]["genes"],
            "claude_science_drivers": claude_science["prospect"]["typed_status_counts"]["drivers"],
            "claude_science_passengers": claude_science["prospect"]["typed_status_counts"]["passengers"],
            "claude_science_contradicted": claude_science["prospect"]["typed_status_counts"]["contradicted"],
            "claude_science_not_assayed": claude_science["prospect"]["typed_status_counts"]["not_assayed"],
            "substrate_after_not_assayed": substrate["coverage"]["sade_feldman_signature"]["after"]["not_assayed"],
            "pggt1b_novelty_downgraded": pggt1b["novelty_assessment"]["downgraded_novelty"],
            "pggt1b_wet_lab_minimum_donors": pggt1b["wet_lab_protocol"]["minimum_donors"],
            "endgame_candidates": endgame["candidate_count"],
            "endgame_cleared": endgame["cleared_count"],
            "endgame_lead": (endgame.get("lead_candidate") or {}).get("gene", "none"),
            "endgame_with_t_cell_support": sum(
                1 for row in endgame["candidate_decisions"]
                if row["independent_primary_t_cell_support"]
            ),
            "endgame_rpe1_not_assayed": endgame["non_blocking_not_assayed"][0]["affected_candidates"],
        },
        "trust_boundary": {
            "model_role": "propose, search, pressure-test",
            "model_in_trust_path": "no",
            "accepted_state": "human_signed_replayable_root",
            "model_accepted_state_mutations": 0,
        },
        "five_minute_path": [
            "Overview: acceptance layer first, the real Claude Science export enters Prospect and receives typed causal verdicts.",
            "Overview: substrate coverage, frozen ORCS primary T-cell context shrinks uncovered genes while staying proposal-only.",
            "Overview: PGGT1B is the caveated hypothesis worth testing, with prior-art novelty downgraded.",
            "Overview: paste any signature, DE table, ranked marker list, or gene list into the submitter and share the state page.",
            "Overview: the overclaiming counter, 48% overall and 64% on canonical effectors.",
            "Findings: signed CD4+ T-cell findings that recover known biology and catch overclaims.",
            "Agent: the campaign leaderboard, every row a proposal, none accepted state.",
            "Agent: the PGGT1B evidence packet, ChEMBL hook, disease context, and wet-lab protocol.",
            "Agent: the wet-lab assay packet, proposal-only, ready for a lab.",
            "Frontier: the receipt boundary and the MCP bridge, which returns a proposal, never accepted state.",
        ],
        "public_artifacts_to_open": PUBLIC_ARTIFACTS,
        "commands": [
            "./prospect verify",
            "./prospect submit-pack",
            "./prospect demo-mode --reset",
            "./prospect claude-science",
            "./prospect defended-discovery-endgame-preregister",
            "./prospect pggt1b-endgame-decision",
            "./prospect defended-discovery-endgame-result",
            "./prospect substrate-coverage",
            "./prospect pggt1b-defended-evidence",
            "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
            "python benchmark/mutation_pack.py",
            "python examples/receipt_bridge_client.py --json",
            "python examples/claude_science_connector_client.py --json",
            "python examples/prospect_connector_client.py --case openresearch --json",
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
        f"- {counts['finding_index_rows']} rows in the scannable finding index",
        f"- {counts['campaign_rows']} proposal-only campaign rows",
        f"- {counts['disease_overlay_rows']} campaign rows overlaid with external disease context",
        f"- {counts['disease_overlay_context_rows']} rows with selected immune or hematologic context",
        f"- {counts['lab_packet_rows']} proposal-only wet-lab assay rows",
        f"- {counts['public_artifacts']} public data artifacts",
        (
            f"- {counts['claude_science_genes']} real Claude Science signature genes typed by Prospect: "
            f"{counts['claude_science_drivers']} drivers, {counts['claude_science_passengers']} passengers, "
            f"{counts['claude_science_contradicted']} contradicted driver claims, "
            f"{counts['claude_science_not_assayed']} not assayed"
        ),
        f"- Frozen ORCS primary T-cell context reduces uncovered Sade-Feldman genes to {counts['substrate_after_not_assayed']}",
        (
            f"- PGGT1B novelty downgraded against prior art: {'yes' if counts['pggt1b_novelty_downgraded'] else 'no'}, "
            f"wet-lab protocol minimum donors {counts['pggt1b_wet_lab_minimum_donors']}"
        ),
        (
            f"- Defended-discovery fixed bar: {counts['endgame_candidates']} locked candidates, "
            f"{counts['endgame_cleared']} proposal-only lead worth testing ({counts['endgame_lead']}), "
            f"{counts['endgame_with_t_cell_support']} retained independent primary T-cell support, "
            f"{counts['endgame_rpe1_not_assayed']} retain RPE1 as not_assayed context"
        ),
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
    lines += ["", "## Public artifacts to open", ""]
    lines += [f"- `{path}`" for path in handout["public_artifacts_to_open"]]
    lines += ["", "## Replay commands", ""]
    lines += [f"- `{command}`" for command in handout["commands"]]
    lines += ["", "## What remains human-only", ""]
    lines += [f"- {action}" for action in handout["human_only_actions"]]
    lines += ["", "Rebuild:", "", "```bash", "./prospect judge-handout", "```"]
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
