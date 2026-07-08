"""Build assay triage rows from campaign probe disagreements."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "campaign_triage.json"
OUT_CSV = DATA / "campaign_triage.csv"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_TRIAGE.md"


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _triage_decision(row: dict[str, Any]) -> str:
    if row["agent_recommendation"] == "advance_to_assay_design":
        return "secondary_assay_queue"
    if row["agent_recommendation"] == "advance_if_capacity_allows":
        return "capacity_assay_queue"
    return "hold_as_ranked_backup"


def _assay_gate(row: dict[str, Any]) -> str:
    if row["agent_recommendation"] == "advance_to_assay_design":
        return "orthogonal knockdown plus matched Rest, Stim8hr, and Stim48hr targeted RNA-seq before assay-design promotion"
    return "orthogonal knockdown and non-immune transfer check before spending primary assay capacity"


def _reason_to_hold(row: dict[str, Any]) -> str:
    return (
        "model disagreement is evidence for review priority, not acceptance; deterministic review "
        f"keeps {row['gene']} at {row['deterministic_decision'].replace('_', ' ')} until the assay gate passes"
    )


def _triage_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "alignment": row["alignment"],
        "deterministic_decision": row["deterministic_decision"],
        "agent_recommendation": row["agent_recommendation"],
        "triage_decision": _triage_decision(row),
        "stimulated_signal": row["stimulated_signal"],
        "specificity": row["specificity"],
        "assay_gate": _assay_gate(row),
        "reason_to_hold": _reason_to_hold(row),
        "stop_rules": row["stop_rules"],
        "agent_rationale": row["agent_rationale"],
    }


def build_triage() -> dict[str, Any]:
    probe = _json(DATA / "campaign_agent_probe.json")
    rows = [_triage_row(row) for row in probe["rows"] if row["alignment"] == "more_aggressive"]
    return {
        "title": "Campaign disagreement triage",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "source": "examples/data/campaign_agent_probe.json",
        "source_probe_id": probe["probe_id"],
        "campaign_id": probe["campaign_id"],
        "summary": {
            "more_aggressive": len(rows),
            "secondary_assay_queue": sum(1 for row in rows if row["triage_decision"] == "secondary_assay_queue"),
            "capacity_assay_queue": sum(1 for row in rows if row["triage_decision"] == "capacity_assay_queue"),
        },
        "rows": rows,
    }


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "alignment", "deterministic_decision",
        "agent_recommendation", "triage_decision", "stimulated_signal", "specificity",
        "assay_gate", "reason_to_hold", "stop_rules", "agent_rationale",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "stop_rules": " | ".join(row["stop_rules"])})


def _markdown(triage: dict[str, Any]) -> str:
    lines = [
        "# Campaign disagreement triage",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. Model disagreement can prioritize review; it cannot accept state.",
        "",
        f"Probe: `{triage['source_probe_id']}`. Campaign: `{triage['campaign_id']}`.",
        "",
        "## Summary",
        "",
    ]
    for key, value in triage["summary"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Triage rows",
        "",
        "| rank | gene | deterministic decision | Claude probe | triage decision | assay gate |",
        "|---:|---|---|---|---|---|",
    ]
    for row in triage["rows"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['deterministic_decision']} | "
            f"{row['agent_recommendation']} | {row['triage_decision']} | {row['assay_gate']} |"
        )
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/campaign_triage.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_triage(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    triage = build_triage()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(triage, indent=2) + "\n")
    _write_csv(triage["rows"], out_csv)
    out_doc.write_text(_markdown(triage))
    return triage


def main() -> None:
    triage = write_triage()
    print(f"wrote {OUT_JSON} ({len(triage['rows'])} rows)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
