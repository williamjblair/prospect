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


def _priority_lane(rank: int, row: dict[str, Any]) -> str:
    if rank == 1:
        return "top wet-lab bet"
    if row["known_regulon_targets"] > 0:
        return "known-regulon anchor"
    if row["rest_de"] <= 25 and (row["k562_de"] is None or row["k562_de"] <= 5):
        return "clean specificity"
    if row["strongest_condition"] == "Stim48hr":
        return "late activation follow-up"
    if row["stim_max_de"] >= 1000:
        return "large-footprint follow-up"
    return "bench follow-up"


def _primary_readout(row: dict[str, Any]) -> str:
    if row["strongest_condition"] == "Stim8hr":
        return "Stim8hr transcriptional program"
    if row["strongest_condition"] == "Stim48hr":
        return "Stim48hr transcriptional program"
    return "stimulated CD4+ transcriptional program"


def _why_interesting(rank: int, row: dict[str, Any]) -> str:
    gene = row["gene"]
    k562 = row["k562_de"]
    transfer = f"K562 DE {k562}" if k562 is not None else "no K562 measurement"
    if rank == 1:
        return (
            f"{gene} has the largest stimulated footprint in the campaign, "
            f"{row['stim_max_de']} DE genes at {row['strongest_condition']}, with {transfer}."
        )
    if row["known_regulon_targets"] > 0:
        return (
            f"{gene} carries a literature regulon anchor while still passing the CD4-specific "
            f"proposal filters, giving the follow-up a known comparison set."
        )
    if row["rest_de"] <= 25:
        return (
            f"{gene} is nearly silent at Rest but crosses the campaign threshold after stimulation, "
            f"with {transfer}."
        )
    return (
        f"{gene} passes the non-canonical, on-target, CD4-specific filter with "
        f"{row['stim_max_de']} DE genes at {row['strongest_condition']}."
    )


def _main_risk(row: dict[str, Any]) -> str:
    if row["k562_de"] is None and row["rpe1_de"] is None:
        return "proposal-only because non-immune transfer is inferred from available rows, not both cell types."
    if row["rest_de"] > 250:
        return "proposal-only because Rest DE is close to the campaign ceiling."
    if row["known_regulon_targets"] > 0:
        return "proposal-only because the known regulon gives context but does not establish this CD4+ claim."
    return "proposal-only until an orthogonal perturbation reproduces the stimulated CD4+ footprint."


def _what_would_weaken(row: dict[str, Any]) -> str:
    if row["k562_de"] is None and row["rpe1_de"] is None:
        return "A broad non-immune effect in a follow-up transfer assay would lower priority."
    if row["rest_de"] > 250:
        return "A larger Rest effect on replicate would make this look less activation-specific."
    return "Loss of the stimulated DE footprint after orthogonal knockdown would lower priority."


def _review_summary(rank: int, row: dict[str, Any]) -> str:
    return (
        f"{_priority_lane(rank, row)}: {_why_interesting(rank, row)} "
        f"Primary readout: {_primary_readout(row)}."
    )


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
        "priority_lane": _priority_lane(rank, row),
        "primary_readout": _primary_readout(row),
        "why_interesting": _why_interesting(rank, row),
        "main_risk": _main_risk(row),
        "what_would_weaken": _what_would_weaken(row),
        "review_summary": _review_summary(rank, row),
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
        "rest_de", "k562_de", "rpe1_de", "known_regulon_targets", "priority_lane",
        "primary_readout", "why_interesting", "main_risk", "what_would_weaken", "rationale", "assay",
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
        "## Review lane",
        "",
        "| rank | gene | lane | why it is interesting | What would weaken it | primary readout |",
        "|---:|---|---|---|---|---|",
    ]
    for row in campaign["candidates"][:12]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['priority_lane']} | "
            f"{row['why_interesting']} | {row['what_would_weaken']} | {row['primary_readout']} |"
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
