"""Build a Gladstone-facing assay operations bundle from lab packet rows."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.lab_packet import build_lab_packet

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "assay_operations_bundle.json"
OUT_CSV = DATA / "assay_operations_bundle.csv"
OUT_DOC = ROOT / "docs" / "ASSAY_OPERATIONS_BUNDLE.md"

REPLAY_LINKS = [
    "/data/frontier.json",
    "/data/judge_packet.json",
    "/data/lab_packet.json",
    "/data/pggt1b_deep_dive.json",
    "/data/pggt1b_matrix_slice.json",
    "/data/campaign_pressure_summary.json",
]


def _queue(rank: int) -> str:
    if rank == 1:
        return "primary_assay_queue"
    if rank == 2:
        return "secondary_assay_queue"
    return "capacity_assay_queue"


def _expected_positive(row: dict[str, Any]) -> str:
    return (
        f"{row['gene']} orthogonal knockdown reproduces a stimulated program shift in "
        f"{row['strongest_condition']} with activation-marker flow cytometry and targeted RNA-seq, "
        "without a matched Rest-only or broad non-immune signal."
    )


def _weakening(row: dict[str, Any]) -> str:
    return (
        "Rest-only shift, weak stimulated marker movement, inconsistent targeted RNA-seq direction, "
        f"or a broad transfer signal stronger than the CD4+ {row['strongest_condition']} footprint."
    )


def _rejection(_row: dict[str, Any]) -> str:
    return (
        "failed on-target knockdown, no stimulated activation-program shift after knockdown, "
        "or a broad non-immune effect that explains the signal better than CD4+ activation gating."
    )


def _assay_steps(row: dict[str, Any]) -> list[str]:
    return [
        "design orthogonal CRISPRi guide and confirm guide mapping before culture work",
        "run matched non-targeting, safe-harbor, VAV1, LAT, and CD3E controls",
        "confirm on-target knockdown before interpreting any transcriptome or flow readout",
        "measure matched Rest, Stim8hr, and Stim48hr cultures from the same donor preparation",
        "read activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h",
        f"compare {row['gene']} against its Prospect replay links before any status change",
    ]


def _decision_gates(_row: dict[str, Any]) -> list[str]:
    return [
        "knockdown gate: on-target knockdown passes before interpretation",
        "specificity gate: stimulated effect is stronger than matched Rest-only signal",
        "transfer gate: broad non-immune effect does not explain the CD4+ signal",
        "acceptance gate: new evidence is replayed and human-signed before accepted state changes",
    ]


def _operations_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "queue": _queue(row["rank"]),
        "intervention": row["intervention"],
        "sample": row["sample"],
        "conditions": row["conditions"],
        "strongest_condition": row["strongest_condition"],
        "stim_max_de": row["stim_max_de"],
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "readouts": {
            "primary": row["primary_readout"],
            "secondary": row["secondary_readout"],
        },
        "controls": {
            "negative": row["negative_controls"],
            "positive": row["positive_controls"],
        },
        "assay_steps": _assay_steps(row),
        "decision_gates": _decision_gates(row),
        "expected_positive_result": _expected_positive(row),
        "weakening_result": _weakening(row),
        "rejection_result": _rejection(row),
        "missing_evidence_before_acceptance": [
            "orthogonal knockdown",
            "matched donor replicate",
            "activation-marker flow cytometry",
            "targeted RNA-seq at 8h and 48h",
            "human signature over replayed follow-up evidence",
        ],
        "replay_links": REPLAY_LINKS,
        "evidence": row["evidence"],
    }


def build_assay_operations_bundle(limit: int = 5) -> dict[str, Any]:
    lab_packet = build_lab_packet(limit=limit)
    candidates = [_operations_row(row) for row in lab_packet["candidates"]]
    return {
        "title": "Gladstone assay operations bundle",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "accepted_state_mutations": 0,
        "scope": "wet-lab planning, not accepted biological state",
        "source_artifact": "examples/data/lab_packet.json",
        "method": {
            "candidate_source": "frontier.lab_packet.build_lab_packet",
            "row_count": len(candidates),
            "operations_rule": (
                "convert proposal-only assay rows into explicit promotion, weakening, and rejection evidence"
            ),
            "replay_links": REPLAY_LINKS,
        },
        "candidates": candidates,
    }


def _join(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "queue", "intervention",
        "strongest_condition", "stim_max_de", "rest_de", "k562_de", "rpe1_de",
        "expected_positive_result", "weakening_result", "rejection_result",
        "missing_evidence_before_acceptance", "decision_gates", "replay_links",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _join(row.get(field)) for field in fields})


def _markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Gladstone assay operations bundle",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. This is wet-lab planning, not accepted biological state.",
        "",
        "## What this adds",
        "",
        "The lab packet names interventions, controls, readouts, and stop rules. This operations bundle adds the bench decision frame for each row: expected positive result, weakening result, rejection result, and missing evidence before acceptance.",
        "",
        "## Candidate operations",
        "",
        "| rank | gene | queue | expected positive result | weakening result | rejection result |",
        "|---:|---|---|---|---|---|",
    ]
    for row in bundle["candidates"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['queue']} | {row['expected_positive_result']} | "
            f"{row['weakening_result']} | {row['rejection_result']} |"
        )
    lines += [
        "",
        "## Required gates before any accepted state change",
        "",
    ]
    for gate in bundle["candidates"][0]["decision_gates"]:
        lines.append(f"- {gate}")
    lines += [
        "",
        "## Missing evidence before acceptance",
        "",
    ]
    for item in bundle["candidates"][0]["missing_evidence_before_acceptance"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Replay links",
        "",
    ]
    lines += [f"- `{link}`" for link in bundle["method"]["replay_links"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect assay-ops",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_assay_operations_bundle(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
    limit: int = 5,
) -> dict[str, Any]:
    bundle = build_assay_operations_bundle(limit=limit)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(bundle, indent=2) + "\n")
    _write_csv(bundle["candidates"], out_csv)
    out_doc.write_text(_markdown(bundle))
    return bundle


def main() -> None:
    bundle = write_assay_operations_bundle()
    print(f"wrote {OUT_JSON} ({len(bundle['candidates'])} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
