"""Build a compact summary of the Claude campaign pressure loop."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "campaign_pressure_summary.json"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_PRESSURE_SUMMARY.md"

CLOSED_RECOMMENDATIONS = ["add_control", "gate_sufficient", "lower_priority"]


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _pressure_result(row: dict[str, Any]) -> str:
    if row["alignment"] == "aligned":
        return "aligned_with_deterministic_review"
    if row["alignment"] == "more_aggressive":
        return "converted_to_assay_gate"
    if row["alignment"] == "more_cautious":
        return "model_more_cautious"
    return "needs_human_review"


def _pressure_accounting(
    probe_rows: list[dict[str, Any]],
    triage_rows: list[dict[str, Any]],
    gate_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    triage_by_gene = {row["gene"]: row for row in triage_rows}
    gate_by_gene = {row["gene"]: row for row in gate_rows}
    rows = []
    for row in probe_rows:
        triage = triage_by_gene.get(row["gene"], {})
        gate = gate_by_gene.get(row["gene"], {})
        rows.append({
            "rank": row["rank"],
            "gene": row["gene"],
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "deterministic_decision": row["deterministic_decision"],
            "claude_recommendation": row["agent_recommendation"],
            "alignment": row["alignment"],
            "pressure_result": _pressure_result(row),
            "triage_decision": triage.get("triage_decision", "none"),
            "gate_recommendation": gate.get("gate_recommendation", "none"),
            "assay_gate": triage.get("assay_gate", "none"),
            "reason": triage.get("reason_to_hold") or row["agent_rationale"],
        })
    return sorted(rows, key=lambda item: item["rank"])


def build_summary() -> dict[str, Any]:
    campaign = _json(DATA / "agent_campaign.json")
    review = _json(DATA / "agent_campaign_review.json")
    probe = _json(DATA / "campaign_agent_probe.json")
    triage = _json(DATA / "campaign_triage.json")
    gate_probe = _json(DATA / "campaign_gate_probe.json")

    probe_rows = probe["rows"]
    triage_rows = triage["rows"]
    gate_rows = gate_probe["rows"]
    alignment_counts = Counter(row["alignment"] for row in probe_rows)
    gate_counts = Counter(row["gate_recommendation"] for row in gate_rows)
    pressure_rows = _pressure_accounting(probe_rows, triage_rows, gate_rows)
    gate_coverage = gate_probe.get("coverage", {})

    return {
        "title": "Campaign pressure summary",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted_state_mutations": 0,
        "model_in_trust_path": "no",
        "source_artifacts": [
            "examples/data/agent_campaign.json",
            "examples/data/agent_campaign_review.json",
            "examples/data/campaign_agent_probe.json",
            "examples/data/campaign_triage.json",
            "examples/data/campaign_gate_probe.json",
        ],
        "campaign_id": campaign["campaign_id"],
        "probe_id": probe["probe_id"],
        "gate_probe_id": gate_probe["probe_id"],
        "counts": {
            "campaign_candidates": len(campaign["candidates"]),
            "deterministic_review_rows": len(review["rows"]),
            "claude_probe_rows": len(probe_rows),
            "aligned_rows": alignment_counts.get("aligned", 0),
            "more_aggressive_rows": alignment_counts.get("more_aggressive", 0),
            "more_cautious_rows": alignment_counts.get("more_cautious", 0),
            "triage_rows": len(triage_rows),
            "gate_probe_rows": len(gate_rows),
        },
        "gate_recommendations": {key: gate_counts.get(key, 0) for key in CLOSED_RECOMMENDATIONS},
        "gate_probe_coverage": gate_coverage,
        "closed_recommendations": CLOSED_RECOMMENDATIONS,
        "pressure_accounting": pressure_rows,
        "boundary_statement": (
            "Claude pressure became review work: aligned rows stayed aligned, more-aggressive rows "
            "became assay gates, gate probes added controls or lowered priority, gate coverage stayed explicit, "
            "and no accepted state changed."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    counts = summary["counts"]
    lines = [
        "# Campaign pressure summary",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        summary["boundary_statement"],
        "",
        "## Replay",
        "",
        "```bash",
        "./prospect campaign-pressure",
        "```",
        "",
        "## Counts",
        "",
        f"- Campaign candidates: {counts['campaign_candidates']}",
        f"- Deterministic review rows: {counts['deterministic_review_rows']}",
        f"- Claude probe rows: {counts['claude_probe_rows']}",
        f"- Aligned rows: {counts['aligned_rows']}",
        f"- More-aggressive rows converted to assay gates: {counts['more_aggressive_rows']}",
        f"- More-cautious rows: {counts['more_cautious_rows']}",
        f"- Gate probe rows: {counts['gate_probe_rows']}",
        "",
        "## Gate coverage",
        "",
        f"- Requested gates: {summary['gate_probe_coverage'].get('requested_limit', 0)}",
        f"- Returned gate decisions: {summary['gate_probe_coverage'].get('returned_decisions', 0)}",
        f"- Coverage status: `{summary['gate_probe_coverage'].get('coverage_status', 'unknown')}`",
        f"- Missing decisions: {summary['gate_probe_coverage'].get('missing_decisions', 0)}",
        "",
        "## Gate recommendations",
        "",
    ]
    for key, value in summary["gate_recommendations"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Pressure accounting",
        "",
        "| rank | gene | Claude pressure | Prospect result | gate recommendation |",
        "|---:|---|---|---|---|",
    ]
    for row in summary["pressure_accounting"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['claude_recommendation']} | "
            f"{row['pressure_result']} | {row['gate_recommendation']} |"
        )
    lines += [
        "",
        "No model output in this packet changes accepted state.",
    ]
    return "\n".join(lines) + "\n"


def write_summary(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    summary = build_summary()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2) + "\n")
    out_doc.write_text(_markdown(summary))
    return summary


def main() -> None:
    summary = write_summary()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"accounted for {summary['counts']['claude_probe_rows']} Claude probe rows")


if __name__ == "__main__":
    main()
