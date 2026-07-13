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
    pggt1b_audit = _json(DATA / "pggt1b_comparability_audit.json")
    comparator = _json(DATA / "gse278572_comparator.json")
    calibration = _json(DATA / "gse271788_calibration.json")
    activation_specificity = _json(DATA / "gse271788_activation_specificity.json")
    index = _json(DATA / "finding_index.json")
    reliability = _json(DATA / "reliability_benchmark.json")
    findings = _jsonl(FRONTIER / "findings.jsonl")
    receipts = _jsonl(RECEIPTS)
    counts = claude_science["prospect"]["typed_status_counts"]
    rel_core = reliability["metrics"]["contradiction_rate"]["pooled_core"]
    rel_effect = reliability["famous_gene_effect"]

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
        "headline": (
            "About half of confident AI major-regulator claims are contradicted by the frozen data: "
            f"{rel_core['refuted']} of {rel_core['checkable']} "
            f"({round(rel_core['contradiction_rate'] * 100, 1)}%, 95% CI {round(rel_core['ci95'][0] * 100)} "
            f"to {round(rel_core['ci95'][1] * 100)} percent), famous genes overclaimed "
            f"{round(rel_effect['famous_overclaim_rate'] * 100, 1)}% versus "
            f"{round(rel_effect['baseline_overclaim_rate'] * 100, 1)}% baseline. An autonomous Claude Opus "
            "agent generated the claims Prospect measures; a Claude Science connector sends real exports "
            "through the same frozen gate."
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
            "claude_science_reviewer_result": claude_science["live_connector"]["reviewer_result"],
            "claude_science_live_accepted": claude_science["live_connector"]["accepted"],
            "substrate_after_not_assayed": substrate["coverage"]["sade_feldman_signature"]["after"]["not_assayed"],
            "pggt1b_novelty_downgraded": pggt1b["novelty_assessment"]["downgraded_novelty"],
            "pggt1b_wet_lab_minimum_donors": pggt1b["wet_lab_protocol"]["minimum_donors"],
            "pggt1b_orthogonal_public_datasets": pggt1b["orthogonal_public_dataset_count"],
            "pggt1b_registry_accessions": len(
                pggt1b_audit["registry_searches"]["candidate_accession_audit"]
            ),
            "pggt1b_comparable_replication_found": pggt1b_audit["determination"]
            ["comparable_pggt1b_transcriptomic_reproduction_found"],
            "pggt1b_batch_kill": pggt1b_audit["determination"]["batch_or_dataset_specificity_kill"],
            "gse278572_overlap": comparator["comparison"]["prospect_overlap"],
            "gse278572_qualified_genes": comparator["finding3_review"]["n_needs_qualification"],
            "gse271788_overlap": calibration["primary_result"]["n"],
            "gse271788_rho": calibration["primary_result"]["spearman_rho"],
            "gse271788_permutation_p": calibration["primary_result"]["permutation_p_value_one_sided"],
            "gse271788_kills_passed": sum(
                1 for kill in calibration["adversarial_kills"].values() if kill["passed"]
            ),
            "gse271788_partial_rho": activation_specificity["primary_result"]["partial_spearman_rho"],
            "gse271788_partial_p": activation_specificity["primary_result"]["permutation_p_value_one_sided"],
            "gse271788_sensitivity_status": activation_specificity["status"],
            "gse271788_sensitivity_kills_passed": sum(
                1 for kill in activation_specificity["adversarial_kills"].values() if kill["passed"]
            ),
            "reliability_refuted": rel_core["refuted"],
            "reliability_checkable": rel_core["checkable"],
            "reliability_contradiction_rate": rel_core["contradiction_rate"],
            "reliability_ci_low": rel_core["ci95"][0],
            "reliability_ci_high": rel_core["ci95"][1],
            "reliability_famous_rate": rel_effect["famous_overclaim_rate"],
            "reliability_baseline_rate": rel_effect["baseline_overclaim_rate"],
            "reliability_famous_p": rel_effect["permutation_p_one_sided"],
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
            "Check: inspect the reliability benchmark, 46 of 96 confident claims contradicted (47.9%, 95% CI 38 to 58 percent), 63.9% on famous genes at permutation p 0.0001.",
            "Check: inspect the GSE278572 correction that qualifies Prospect's own MED12 interpretation.",
            "Evidence: inspect the broad 79-target calibration, then its activation-specific sensitivity that does not clear the locked bar.",
            "Lead: PGGT1B is the caveated mechanism-first hypothesis worth testing.",
            "Evidence: signed CD4+ T-cell findings show the frozen evidence graph.",
            "Receipts: receipts and MCP bridge show accepted=false until a human key signs.",
        ],
        "public_artifacts_to_open": PUBLIC_ARTIFACTS,
        "command_groups": [
            {
                "label": (
                    "Offline: a bare `git clone` + `pip install -r requirements.txt`. "
                    "No API key, no network, no hosted service."
                ),
                "commands": [
                    "./prospect verify",
                    "./prospect reliability-benchmark",
                    "python benchmark/mutation_pack.py",
                    "python tests/test_skill_parity.py",
                    "python tests/test_marson.py",
                    "./prospect demo-mode --reset",
                    "./prospect claude-science",
                    "./prospect substrate-coverage",
                    "./prospect pggt1b-defended-evidence",
                    "python frontier/gse271788_calibration.py --check",
                    "python frontier/gse271788_activation_specificity.py --check",
                    "python examples/claude_science_connector_client.py --json",
                    "python examples/receipt_bridge_client.py --json",
                    "python receipt/replay_proposal.py <local-proposal.json>",
                ],
            },
            {
                "label": (
                    "Needs a local acceptance service: start it first, then point the "
                    "connectors at it."
                ),
                "commands": [
                    "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
                    "python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json",
                    "python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json",
                ],
            },
            {
                "label": (
                    "Hosted (already live): the paste box and the hosted MCP at "
                    "prospect-acceptance.fly.dev run the same frozen gate."
                ),
                "commands": [
                    "python receipt/replay_proposal.py <hosted-proposal-url>",
                ],
            },
        ],
        "signature_note": (
            "Verify the signature, do not re-sign. The signed root is committed; a fresh clone "
            "auto-generates its own local key, so a signing command would mint a different root. "
            "Re-derive and compare the committed root instead."
        ),
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
        handout["headline"],
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
            f"- Reliability benchmark: {counts['reliability_refuted']} of {counts['reliability_checkable']} confident "
            f"major-regulator claims contradicted ({round(counts['reliability_contradiction_rate']*100, 1)}%, "
            f"95% CI {round(counts['reliability_ci_low']*100)} to {round(counts['reliability_ci_high']*100)} percent); "
            f"famous genes overclaimed {round(counts['reliability_famous_rate']*100, 1)}% versus "
            f"{round(counts['reliability_baseline_rate']*100, 1)}% baseline, permutation p {counts['reliability_famous_p']}; "
            f"stated confidence does not track correctness"
        ),
        (
            f"- Real Claude Science signature: reviewer {counts['claude_science_reviewer_result'].replace('_', ' ')}, "
            f"Prospect returned {counts['claude_science_genes']} genes, "
            f"{counts['claude_science_drivers']} drivers, {counts['claude_science_passengers']} passengers, "
            f"{counts['claude_science_contradicted']} contradicted driver claims, "
            f"{counts['claude_science_not_assayed']} not assayed, and "
            f"accepted={str(counts['claude_science_live_accepted']).lower()}"
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
        (
            f"- Activation-specific sensitivity: partial rho {counts['gse271788_partial_rho']:.6f}, "
            f"permutation P {counts['gse271788_partial_p']:.8f}, "
            f"{counts['gse271788_sensitivity_kills_passed']} of 5 kills passed, status "
            f"{counts['gse271788_sensitivity_status']}"
        ),
        (
            f"- PGGT1B registry audit: {counts['pggt1b_registry_accessions']} candidate accessions inspected, "
            f"direct comparable replication found: "
            f"{'yes' if counts['pggt1b_comparable_replication_found'] else 'no'}"
        ),
        (
            f"- PGGT1B remains proposal-only; independent batch-specificity kill "
            f"{counts['pggt1b_batch_kill'].replace('_', ' ')}, protocol minimum donors "
            f"{counts['pggt1b_wet_lab_minimum_donors']}"
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
    for group in handout["command_groups"]:
        lines.append(f"**{group['label']}**")
        lines.append("")
        lines += [f"- `{command}`" for command in group["commands"]]
        lines.append("")
    lines.append(handout["signature_note"])
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
