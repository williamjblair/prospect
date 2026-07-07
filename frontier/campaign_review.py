"""Build an audit appendix for the proposal-only agent campaign."""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.agent_campaign import build_campaign

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "agent_campaign_review.json"
OUT_CSV = DATA / "agent_campaign_review.csv"
OUT_DOC = ROOT / "docs" / "AGENT_CAMPAIGN_REVIEW.md"


def _fmt_de(value: int | None) -> str:
    return "not measured" if value is None else f"{value} DE"


def _decision(row: dict[str, Any]) -> str:
    if row["rank"] == 1:
        return "advance_to_assay_design"
    if row["known_regulon_targets"] > 0:
        return "use_as_regulon_anchor"
    if row["rest_de"] <= 25 and (row["k562_de"] is None or row["k562_de"] <= 5):
        return "advance_if_capacity_allows"
    return "hold_as_ranked_backup"


def _stop_rules(row: dict[str, Any]) -> list[str]:
    rules = [
        "failed on-target knockdown in the stimulated condition",
        row["what_would_weaken"],
    ]
    if row["rest_de"] > 250:
        rules.append("Rest effect grows on replicate")
    if row["k562_de"] is None and row["rpe1_de"] is None:
        rules.append("broad non-immune effect appears in a transfer assay")
    return rules


def _review_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "review_lane": row["priority_lane"],
        "decision": _decision(row),
        "stimulated_signal": f"{row['stim_max_de']} DE at {row['strongest_condition']}",
        "specificity": (
            f"Rest {row['rest_de']} DE, K562 {_fmt_de(row['k562_de'])}, "
            f"RPE1 {_fmt_de(row['rpe1_de'])}"
        ),
        "regulon_context": (
            "no CollecTRI regulon"
            if row["known_regulon_targets"] == 0
            else f"{row['known_regulon_targets']} CollecTRI targets"
        ),
        "primary_readout": row["primary_readout"],
        "why_interesting": row["why_interesting"],
        "stop_rules": _stop_rules(row),
    }


def build_review() -> dict[str, Any]:
    campaign = build_campaign(limit=20)
    rows = [_review_row(row) for row in campaign["candidates"]]
    lanes = Counter(row["review_lane"] for row in rows)
    return {
        "title": "Campaign review appendix",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "source": "frontier.agent_campaign.build_campaign",
        "campaign_id": campaign["campaign_id"],
        "candidate_count": len(rows),
        "top_gene": rows[0]["gene"],
        "lane_counts": dict(sorted(lanes.items())),
        "audit_questions": [
            {
                "question": "Is there an on-target stimulated footprint?",
                "field": "stimulated_signal",
                "pass_condition": "stimulated DE is above the campaign floor and strongest knockdown is on-target",
            },
            {
                "question": "Is the signal activation-skewed rather than housekeeping?",
                "field": "specificity",
                "pass_condition": "Rest DE remains below the campaign ceiling and non-immune transfer is small where measured",
            },
            {
                "question": "What would make the proposal weaker?",
                "field": "stop_rules",
                "pass_condition": "each row carries explicit reasons to stop or lower priority",
            },
        ],
        "rows": rows,
    }


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "review_lane", "decision",
        "stimulated_signal", "specificity", "regulon_context", "primary_readout",
        "why_interesting", "stop_rules",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "stop_rules": " | ".join(row["stop_rules"])})


def _markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Campaign review appendix",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. The appendix ranks assay follow-up work; it does not move accepted state.",
        "",
        f"Campaign: `{review['campaign_id']}`. Candidates: {review['candidate_count']}. Top gene: `{review['top_gene']}`.",
        "",
        "## Audit questions",
        "",
    ]
    lines += [
        f"- {item['question']} Field: `{item['field']}`. Rule: {item['pass_condition']}."
        for item in review["audit_questions"]
    ]
    lines += [
        "",
        "## Lane counts",
        "",
        "| lane | rows |",
        "|---|---:|",
    ]
    for lane, count in review["lane_counts"].items():
        lines.append(f"| {lane} | {count} |")
    lines += [
        "",
        "## Review rows",
        "",
        "| rank | gene | lane | decision | stimulated signal | specificity | stop rules |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in review["rows"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['review_lane']} | {row['decision']} | "
            f"{row['stimulated_signal']} | {row['specificity']} | {'; '.join(row['stop_rules'])} |"
        )
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/campaign_review.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_review(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    review = build_review()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(review, indent=2) + "\n")
    _write_csv(review["rows"], out_csv)
    out_doc.write_text(_markdown(review))
    return review


def main() -> None:
    review = write_review()
    print(f"wrote {OUT_JSON} ({review['candidate_count']} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
