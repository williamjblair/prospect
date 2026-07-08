"""Deterministic audit for campaign probe artifacts.

This checks whether a proposal-only Claude campaign probe is safe to promote
into the public review chain. It does not use a model and never moves accepted
state.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.agent_campaign import build_campaign
from frontier.campaign_review import build_review
from loop.campaign_probe import VALID_RECOMMENDATIONS, t_check_regulator, t_cross_cell_type

DATA = ROOT / "examples" / "data"
IN_JSON = DATA / "campaign_agent_probe.json"
OUT_JSON = DATA / "campaign_probe_audit.json"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_PROBE_AUDIT.md"


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _issue(gene: str, issue_type: str, detail: str, frozen_fact: str = "") -> dict[str, str]:
    return {
        "gene": gene,
        "issue_type": issue_type,
        "detail": detail,
        "frozen_fact": frozen_fact,
    }


def _mentions_no_on_target_any_condition(text: str) -> bool:
    lowered = text.lower()
    phrases = [
        "no on-target kd in any condition",
        "no on-target knockdown in any condition",
        "no condition shows on-target kd",
        "no condition shows on-target knockdown",
    ]
    return any(phrase in lowered for phrase in phrases)


def _mentions_k562_inert(text: str) -> bool:
    lowered = text.lower()
    return "k562-inert" in lowered or "k562 inert" in lowered or "fully k562-inert" in lowered


def _rationale_issues(row: dict[str, Any]) -> list[dict[str, str]]:
    gene = row["gene"]
    rationale = row.get("agent_rationale", "")
    issues: list[dict[str, str]] = []
    regulator = t_check_regulator(gene)
    conditions = regulator.get("conditions", {})
    on_target_conditions = [
        condition for condition, values in conditions.items()
        if values.get("kd") == "on-target KD"
    ]
    if _mentions_no_on_target_any_condition(rationale) and on_target_conditions:
        issues.append(_issue(
            gene=gene,
            issue_type="rationale_contradicts_frozen_kd",
            detail="model rationale says no on-target KD in any condition",
            frozen_fact="on-target KD in " + ", ".join(on_target_conditions),
        ))

    transfer = t_cross_cell_type(gene)
    if _mentions_k562_inert(rationale) and transfer.get("k562") not in ("inert", None):
        issues.append(_issue(
            gene=gene,
            issue_type="rationale_contradicts_k562_transfer",
            detail="model rationale says K562 inert",
            frozen_fact=f"K562 verdict is {transfer.get('k562')} with {transfer.get('k562_de')} DE genes",
        ))
    return issues


def _shape_issues(probe: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if probe.get("status") != "evidence_attached":
        issues.append(_issue("probe", "invalid_status", "campaign probe must remain evidence_attached"))
    if probe.get("trust_boundary") != "proposal_only":
        issues.append(_issue("probe", "invalid_trust_boundary", "campaign probe must remain proposal_only"))
    if probe.get("acceptance") is not False:
        issues.append(_issue("probe", "invalid_acceptance", "campaign probe must not accept state"))

    rows = probe.get("rows", [])
    coverage = probe.get("coverage", {})
    if probe.get("candidate_count") != len(rows):
        issues.append(_issue("probe", "candidate_count_mismatch", "candidate_count does not match row count"))
    if coverage.get("coverage_status") != "complete":
        issues.append(_issue("probe", "coverage_incomplete", "probe coverage is not complete"))
    if coverage.get("returned_decisions") != len(rows):
        issues.append(_issue("probe", "coverage_count_mismatch", "returned_decisions does not match row count"))
    if coverage.get("missing_genes"):
        issues.append(_issue("probe", "coverage_missing_genes", "probe has missing requested genes"))
    returned = [row.get("gene") for row in rows]
    if coverage.get("returned_genes") and coverage.get("returned_genes") != returned:
        issues.append(_issue("probe", "coverage_returned_gene_mismatch", "returned_genes does not match rows"))
    return issues


def _row_issues(probe: dict[str, Any]) -> list[dict[str, str]]:
    review_by_gene = {row["gene"]: row for row in build_review()["rows"]}
    campaign_by_gene = {row["gene"]: row for row in build_campaign(limit=20)["candidates"]}
    issues: list[dict[str, str]] = []
    for row in probe.get("rows", []):
        gene = row.get("gene", "")
        review = review_by_gene.get(gene)
        campaign = campaign_by_gene.get(gene)
        if not review or not campaign:
            issues.append(_issue(gene or "unknown", "unknown_campaign_gene", "row gene is not in the campaign review"))
            continue
        if row.get("rank") != campaign["rank"]:
            issues.append(_issue(gene, "rank_mismatch", "probe rank does not match deterministic campaign rank"))
        if row.get("deterministic_decision") != review["decision"]:
            issues.append(_issue(gene, "deterministic_decision_mismatch", "probe decision does not match deterministic review"))
        if row.get("agent_recommendation") not in VALID_RECOMMENDATIONS:
            issues.append(_issue(gene, "invalid_recommendation", "agent recommendation is outside the closed enum"))
        issues.extend(_rationale_issues(row))
    return issues


def audit_probe(probe_path: Path = IN_JSON) -> dict[str, Any]:
    probe = _json(probe_path)
    issues = _shape_issues(probe) + _row_issues(probe)
    return {
        "title": "Campaign probe audit",
        "status": "computationally_reproduced",
        "trust_boundary": "frozen_audit_over_probe_artifact",
        "model_in_trust_path": "no",
        "accepted_state_mutations": 0,
        "source": str(probe_path.relative_to(ROOT) if probe_path.is_relative_to(ROOT) else probe_path),
        "source_probe_id": probe.get("probe_id", ""),
        "campaign_id": probe.get("campaign_id", ""),
        "candidate_count": len(probe.get("rows", [])),
        "coverage": probe.get("coverage", {}),
        "passed": "yes" if not issues else "no",
        "issue_count": len(issues),
        "checks": [
            "proposal_only_status",
            "complete_coverage",
            "deterministic_review_lane_match",
            "closed_recommendation_enum",
            "rationale_contradicts_frozen_kd",
            "rationale_contradicts_k562_transfer",
        ],
        "issues": issues,
        "promotion_rule": (
            "A campaign probe can be promoted only when coverage is complete, recommendations are closed, "
            "deterministic review fields match, and rationale audit reports no frozen-fact contradictions."
        ),
    }


def _markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Campaign probe audit",
        "",
        "Status: `computationally_reproduced`. Trust boundary: frozen audit over proposal-only model pressure.",
        "",
        "No accepted state changes.",
        "",
        f"Source probe: `{audit['source_probe_id']}`.",
        f"Passed: `{audit['passed']}`. Issues: {audit['issue_count']}.",
        "",
        "## Checks",
        "",
    ]
    lines += [f"- `{check}`" for check in audit["checks"]]
    lines += [
        "",
        "## Issues",
        "",
    ]
    if audit["issues"]:
        lines += [
            "| gene | issue | frozen fact |",
            "|---|---|---|",
        ]
        for issue in audit["issues"]:
            lines.append(f"| {issue['gene']} | {issue['issue_type']} | {issue['frozen_fact']} |")
    else:
        lines.append("No audit issues detected in the committed probe artifact.")
    lines += [
        "",
        "## Promotion rule",
        "",
        audit["promotion_rule"],
        "",
        "Run on a temporary expanded probe before promotion:",
        "",
        "```bash",
        "python loop/campaign_probe_audit.py --input /tmp/prospect_campaign_probe.json",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_audit(
    input_json: Path = IN_JSON,
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    audit = audit_probe(input_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, indent=2) + "\n")
    out_doc.write_text(_markdown(audit))
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="campaign_probe_audit")
    parser.add_argument("--input", type=Path, default=IN_JSON)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-doc", type=Path, default=OUT_DOC)
    parser.add_argument("--strict", action="store_true", help="exit nonzero if the audit reports issues")
    args = parser.parse_args(argv)

    audit = write_audit(input_json=args.input, out_json=args.out_json, out_doc=args.out_doc)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_doc}")
    print(f"passed {audit['passed']} with {audit['issue_count']} issues")
    if args.strict and audit["passed"] != "yes":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
