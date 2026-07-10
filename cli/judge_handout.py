"""Build the one-page judge handout from the cut public surface."""
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

HUMAN_ONLY_ACTIONS = [
    "sign the evidence root",
    "accept a submitted receipt",
    "accept a PGGT1B record change",
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
    claude_science = _json(DATA / "claude_science_acceptance_demo.json")
    substrate = _json(DATA / "substrate_coverage_report.json")
    pggt1b = _json(DATA / "pggt1b_defended_evidence.json")
    comparator = _json(DATA / "gse278572_comparator.json")
    calibration = _json(DATA / "gse271788_calibration.json")
    index = _json(DATA / "finding_index.json")
    findings = _jsonl(FRONTIER / "findings.jsonl")
    receipts = _jsonl(RECEIPTS)
    counts = claude_science["prospect"]["typed_status_counts"]

    return {
        "title": "Prospect one-page judge handout",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "thesis": (
            "Prospect tells a biologist which genes in an AI-generated prediction list behave as causal "
            "drivers, which are passengers, and which driver claims the perturbation data contradicts. "
            "The first-screen output is a driver/passenger/contradicted split."
        ),
        "one_line": "Reproducible is not verified.",
        "counts": {
            "public_artifacts": len(PUBLIC_ARTIFACTS),
            "findings": len(findings),
            "receipts": len(receipts),
            "finding_index_rows": len(index.get("items", [])),
            "claude_science_genes": counts["genes"],
            "claude_science_drivers": counts["drivers"],
            "claude_science_passengers": counts["passengers"],
            "claude_science_contradicted": counts["contradicted"],
            "claude_science_not_assayed": counts["not_assayed"],
            "substrate_after_not_assayed": substrate["coverage"]["sade_feldman_signature"]["after"]["not_assayed"],
            "pggt1b_novelty_downgraded": pggt1b["novelty_assessment"]["downgraded_novelty"],
            "pggt1b_wet_lab_minimum_donors": pggt1b["wet_lab_protocol"]["minimum_donors"],
            "pggt1b_orthogonal_public_datasets": pggt1b["orthogonal_public_dataset_count"],
            "gse278572_overlap": comparator["comparison"]["prospect_overlap"],
            "gse278572_qualified_genes": comparator["finding3_review"]["n_needs_qualification"],
            "gse271788_overlap": calibration["primary_result"]["n"],
            "gse271788_rho": calibration["primary_result"]["spearman_rho"],
            "gse271788_permutation_p": calibration["primary_result"]["permutation_p_value_one_sided"],
            "gse271788_kills_passed": sum(
                1 for kill in calibration["adversarial_kills"].values() if kill["passed"]
            ),
        },
        "trust_boundary": {
            "model_role": "propose, search, draft",
            "model_in_trust_path": "no",
            "accepted_record": "human_signed_replayable_root",
            "model_accepted_record_mutations": 0,
        },
        "judge_path": [
            "Check: real Claude Science signature enters Prospect and receives typed causal verdicts.",
            "Check: paste a gene list, DE table, or signature and copy the shareable result link.",
            "Check: inspect the 48 and 64 percent overclaiming benchmark.",
            "Check: inspect the GSE278572 correction that qualifies Prospect's own MED12 interpretation.",
            "Evidence: inspect the 79-target independent primary-CD4 calibration and its three adversarial kills.",
            "Lead: PGGT1B is the caveated mechanism-first hypothesis worth testing.",
            "Evidence: signed CD4+ T-cell findings show the frozen evidence graph.",
            "Receipts: receipts and MCP bridge show accepted=false until a human key signs.",
        ],
        "public_artifacts_to_open": PUBLIC_ARTIFACTS,
        "commands": [
            "./prospect verify",
            "python benchmark/mutation_pack.py",
            "python tests/test_skill_parity.py",
            "python tests/test_marson.py",
            "./prospect demo-mode --reset",
            "./prospect claude-science",
            "./prospect substrate-coverage",
            "./prospect pggt1b-defended-evidence",
            "python frontier/gse271788_calibration.py --check",
            "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
            "python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json",
            "python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json",
            "python receipt/replay_proposal.py <proposal.json-or-url>",
            "python examples/receipt_bridge_client.py --json",
            "python examples/claude_science_connector_client.py --json",
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
        handout["one_line"],
        "",
        handout["limitation"],
        "",
        "## Numbers To Inspect",
        "",
        (
            f"- Real Claude Science signature: {counts['claude_science_genes']} genes, "
            f"{counts['claude_science_drivers']} drivers, {counts['claude_science_passengers']} passengers, "
            f"{counts['claude_science_contradicted']} contradicted driver claims, "
            f"{counts['claude_science_not_assayed']} not assayed"
        ),
        f"- ORCS primary T-cell context reduces uncovered Sade-Feldman genes to {counts['substrate_after_not_assayed']}",
        (
            f"- GSE278572: {counts['gse278572_overlap']} overlapping regulators, "
            f"{counts['gse278572_qualified_genes']} pre-registered interpretation qualification"
        ),
        (
            f"- GSE171737/GSE271788: {counts['gse271788_overlap']} shared primary-CD4 perturbations, "
            f"rho {counts['gse271788_rho']:.6f}, permutation P {counts['gse271788_permutation_p']:.8f}, "
            f"{counts['gse271788_kills_passed']} of 3 adversarial kills passed"
        ),
        f"- PGGT1B carries {counts['pggt1b_orthogonal_public_datasets']} orthogonal public evidence sources",
        (
            f"- PGGT1B novelty downgraded against prior art: {'yes' if counts['pggt1b_novelty_downgraded'] else 'no'}, "
            f"wet-lab protocol minimum donors {counts['pggt1b_wet_lab_minimum_donors']}"
        ),
        f"- {counts['findings']} signed CD4+ findings and {counts['receipts']} receipts",
        f"- {counts['public_artifacts']} public data artifacts",
        "",
        "## Five-minute judge path",
        "",
    ]
    lines += [f"{i}. {step}" for i, step in enumerate(handout["judge_path"], start=1)]
    lines += [
        "",
        "## Trust Boundary",
        "",
        f"- Model role: {handout['trust_boundary']['model_role']}",
        f"- Model in trust path: {handout['trust_boundary']['model_in_trust_path']}",
        f"- Accepted record: {handout['trust_boundary']['accepted_record']}",
        f"- Model accepted record mutations: {handout['trust_boundary']['model_accepted_record_mutations']}",
        "",
        "## Public Artifacts",
        "",
    ]
    lines += [f"- `{path}`" for path in handout["public_artifacts_to_open"]]
    lines += [
        "",
        "## Commands",
        "",
    ]
    lines += [f"- `{command}`" for command in handout["commands"]]
    lines += [
        "",
        "## What remains human-only",
        "",
    ]
    lines += [f"- {action}" for action in handout["human_only_actions"]]
    lines.append("")
    return "\n".join(lines)


def write_handout(out_doc: Path = OUT_DOC) -> dict[str, Any]:
    handout = build_handout()
    out_doc.write_text(_markdown(handout))
    return handout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect judge-handout")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    handout = write_handout()
    if args.json:
        print(json.dumps(handout, indent=2, sort_keys=True))
    else:
        print(f"wrote {OUT_DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
