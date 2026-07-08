"""Build a wet-lab assay packet from frozen Prospect candidate rows."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.agent_campaign import MIN_STIM_DE, MAX_REST_DE
from frontier.validation_sheet import rank_candidates

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "lab_packet.json"
OUT_CSV = DATA / "lab_packet.csv"
OUT_DOC = ROOT / "docs" / "LAB_PACKET.md"

REPLAY_LINKS = [
    "/data/frontier.json",
    "/data/agent_campaign.json",
    "/data/pggt1b_deep_dive.json",
    "/data/receipt_bridge/receipt_contract.json",
]

NEGATIVE_CONTROLS = [
    "non-targeting guide",
    "safe-harbor guide",
    "unstimulated matched culture",
]

POSITIVE_CONTROLS = [
    "VAV1",
    "LAT",
    "CD3E",
]

EXCLUSION_CRITERIA = [
    "failed on-target knockdown",
    "broad non-immune effect",
    "Rest-only transcriptional shift",
    "canonical effector readout without upstream program shift",
]


def _evidence(row: dict[str, Any]) -> list[str]:
    k562 = row["k562_de"] if row["k562_de"] is not None else "not measured"
    rpe1 = row["rpe1_de"] if row["rpe1_de"] is not None else "not measured"
    return [
        f"{row['stim_max_de']} DE genes under {row['strongest_condition']} with {row['strongest_kd']}",
        f"{row['rest_de']} DE genes at Rest",
        f"{k562} DE genes in K562 and {rpe1} in RPE1",
        f"{row['known_regulon_targets']} CollecTRI targets",
    ]


def _candidate(rank: int, row: dict[str, Any]) -> dict[str, Any]:
    gene = row["gene"]
    return {
        "rank": rank,
        "gene": gene,
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "intervention": "CRISPRi knockdown",
        "sample": "primary human CD4+ T cells",
        "conditions": ["Rest", "Stim8hr", "Stim48hr"],
        "biological_question": (
            f"Does {gene} gate the stimulated CD4+ activation program without acting as a broad "
            "housekeeping perturbation?"
        ),
        "primary_readout": (
            "stimulated primary CD4+ T cells: activation-marker flow cytometry plus targeted RNA-seq "
            "at 8h and 48h"
        ),
        "secondary_readout": (
            "compare Rest, Stim8hr, and Stim48hr programs against non-targeting and pathway controls"
        ),
        "decision_rule": (
            "advance only if stimulated knockdown shifts the activation program without a Rest-only "
            "or broad non-immune effect"
        ),
        "negative_controls": NEGATIVE_CONTROLS,
        "positive_controls": POSITIVE_CONTROLS,
        "exclusion_criteria": EXCLUSION_CRITERIA,
        "replay_links": REPLAY_LINKS,
        "stim_max_de": row["stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "known_regulon_targets": row["known_regulon_targets"],
        "score": row["score"],
        "evidence": _evidence(row),
    }


def build_lab_packet(limit: int = 5) -> dict[str, Any]:
    rows = rank_candidates(limit=limit, min_stim_de=MIN_STIM_DE, max_rest_de=MAX_REST_DE)
    candidates = [_candidate(i, row) for i, row in enumerate(rows, 1)]
    return {
        "title": "Wet-lab assay packet",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "source": "validation-sheet ranked candidates: stimulated CD4+ effect, cell-type-specific, non-canonical",
        "scope": "assay planning, not accepted biological state",
        "method": {
            "candidate_source": "frontier.validation_sheet.rank_candidates",
            "assay": "stimulated primary CD4+ CRISPRi follow-up",
            "negative_controls": NEGATIVE_CONTROLS,
            "positive_controls": POSITIVE_CONTROLS,
            "exclusion_criteria": EXCLUSION_CRITERIA,
            "replay_links": REPLAY_LINKS,
        },
        "candidates": candidates,
    }


def _join(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if value is None:
        return ""
    return str(value)


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "intervention", "sample",
        "primary_readout", "secondary_readout", "decision_rule", "negative_controls",
        "positive_controls", "exclusion_criteria", "stim_max_de", "strongest_condition",
        "rest_de", "k562_de", "rpe1_de", "known_regulon_targets", "score", "replay_links",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _join(row.get(field)) for field in fields})


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Wet-lab assay packet",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. This packet is assay planning, not accepted biological state.",
        "",
        "## Controls",
        "",
        f"- Negative: {', '.join(packet['method']['negative_controls'])}",
        f"- Positive: {', '.join(packet['method']['positive_controls'])}",
        f"- Exclude: {', '.join(packet['method']['exclusion_criteria'])}",
        "",
        "## Candidate rows",
        "",
        "| rank | gene | primary readout | stim max DE | Rest DE | K562 DE | score |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in packet["candidates"]:
        k562 = row["k562_de"] if row["k562_de"] is not None else ""
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['primary_readout']} | {row['stim_max_de']} | "
            f"{row['rest_de']} | {k562} | {row['score']} |"
        )
    lines += [
        "",
        "## Replay links",
        "",
    ]
    lines += [f"- `{link}`" for link in packet["method"]["replay_links"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/lab_packet.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_lab_packet(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
    limit: int = 5,
) -> dict[str, Any]:
    packet = build_lab_packet(limit=limit)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    _write_csv(packet["candidates"], out_csv)
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_lab_packet()
    print(f"wrote {OUT_JSON} ({len(packet['candidates'])} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
