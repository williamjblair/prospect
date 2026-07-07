"""Build a proposal-only campaign leaderboard from frozen Prospect evidence."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.validation_sheet import rank_candidates

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "agent_campaign.json"
OUT_CSV = DATA / "agent_campaign.csv"
OUT_DOC = ROOT / "docs" / "AGENT_CAMPAIGN.md"

MIN_STIM_DE = 250
MAX_REST_DE = 350


def _campaign_id(rows: list[dict[str, Any]]) -> str:
    basis = "|".join(f"{r['rank']}:{r['gene']}:{r['score']}" for r in rows)
    return "campaign_" + hashlib.sha256(basis.encode()).hexdigest()[:16]


def _evidence(row: dict[str, Any]) -> list[str]:
    k562 = row["k562_de"] if row["k562_de"] is not None else "not measured"
    rpe1 = row["rpe1_de"] if row["rpe1_de"] is not None else "not measured"
    return [
        f"{row['stim_max_de']} DE genes under {row['strongest_condition']} with {row['strongest_kd']}",
        f"{row['rest_de']} DE genes at Rest",
        f"{k562} DE genes in K562 and {rpe1} in RPE1",
        f"{row['known_regulon_targets']} CollecTRI targets",
    ]


def _campaign_row(rank: int, row: dict[str, Any]) -> dict[str, Any]:
    gene = row["gene"]
    return {
        "rank": rank,
        "gene": gene,
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "class": row["class"],
        "score": row["score"],
        "stim_max_de": row["stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "strongest_kd": row["strongest_kd"],
        "rest_de": row["rest_de"],
        "stim8hr_de": row["stim8hr_de"],
        "stim48hr_de": row["stim48hr_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "cross_cell_type": row["cross_cell_type"],
        "known_regulon_targets": row["known_regulon_targets"],
        "rationale": (
            f"hypothesis to test: {gene} has a stimulated CD4+ footprint, little non-immune transfer, "
            f"and {row['known_regulon_targets']} CollecTRI targets"
        ),
        "evidence": _evidence(row),
        "assay": row["validation_assay"],
    }


def build_campaign(limit: int = 20) -> dict[str, Any]:
    ranked = rank_candidates(limit=limit, min_stim_de=MIN_STIM_DE, max_rest_de=MAX_REST_DE)
    candidates = [_campaign_row(i, r) for i, r in enumerate(ranked, 1)]
    return {
        "campaign_id": _campaign_id(candidates),
        "title": "Agent campaign leaderboard",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "method": {
            "source": "frozen Prospect candidate ranking",
            "min_stim_de": MIN_STIM_DE,
            "max_rest_de": MAX_REST_DE,
            "filters": [
                "non-canonical T-cell gene",
                "condition-specific regulator",
                "not activation-module gene",
                "not essentiality artifact",
                "on-target stimulated knockdown",
                "no broad non-immune effect where measured",
            ],
        },
        "candidates": candidates,
    }


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "score", "stim_max_de", "strongest_condition",
        "rest_de", "k562_de", "rpe1_de", "known_regulon_targets", "rationale", "assay",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def _markdown(campaign: dict[str, Any]) -> str:
    lines = [
        "# Agent campaign leaderboard",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from this campaign.",
        "",
        "The campaign widens the single-agent result into a ranked bench of follow-up hypotheses. Every row is a frozen Prospect lookup: non-canonical, condition-specific, not housekeeping, on-target under stimulation, and inert in non-immune cells where measured.",
        "",
        "| rank | gene | stim max DE | Rest DE | K562 DE | CollecTRI targets | score |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in campaign["candidates"][:20]:
        k562 = row["k562_de"] if row["k562_de"] is not None else ""
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['stim_max_de']} | {row['rest_de']} | "
            f"{k562} | {row['known_regulon_targets']} | {row['score']} |"
        )
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/agent_campaign.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_campaign(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
    limit: int = 20,
) -> dict[str, Any]:
    campaign = build_campaign(limit=limit)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(campaign, indent=2) + "\n")
    _write_csv(campaign["candidates"], out_csv)
    out_doc.write_text(_markdown(campaign))
    return campaign


def main() -> None:
    campaign = write_campaign()
    print(f"wrote {OUT_JSON} ({len(campaign['candidates'])} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
