"""Build a Gladstone-facing pilot design from assay operations rows."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.assay_operations import build_assay_operations_bundle

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "gladstone_pilot_design.json"
OUT_CSV = DATA / "gladstone_pilot_design.csv"
OUT_DOC = ROOT / "docs" / "GLADSTONE_PILOT_DESIGN.md"

CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]
NEGATIVE_CONTROLS = ["non-targeting guide", "safe-harbor guide", "unstimulated matched culture"]
POSITIVE_CONTROLS = ["VAV1", "LAT", "CD3E"]
DONOR_REPLICATES = 3


def _culture_arms(candidate_count: int) -> int:
    perturbation_arms = candidate_count + len(NEGATIVE_CONTROLS) + len(POSITIVE_CONTROLS) - 1
    return perturbation_arms * len(CONDITIONS) * DONOR_REPLICATES


def _candidate_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "queue": row["queue"],
        "strongest_condition": row["strongest_condition"],
        "primary_question": (
            f"Does {row['gene']} reproduce a stimulated CD4+ program shift under "
            f"{row['strongest_condition']} after orthogonal knockdown?"
        ),
        "qc_before_interpretation": [
            "orthogonal knockdown passes before transcriptome or flow interpretation",
            "matched non-targeting and safe-harbor controls pass the same culture handling",
            "matched Rest, Stim8hr, and Stim48hr cultures are retained for specificity review",
        ],
        "promote_if": row["expected_positive_result"],
        "weaken_if": row["weakening_result"],
        "reject_if": row["rejection_result"],
        "missing_evidence_before_acceptance": row["missing_evidence_before_acceptance"],
        "acceptance_gate": "replay follow-up evidence through frozen checks, then require human signature",
        "decision_record": "proposal-only pilot row, not accepted biological state",
        "replay_links": sorted(set(row["replay_links"] + ["/data/assay_operations_bundle.json"])),
    }


def build_pilot_design(limit: int = 5) -> dict[str, Any]:
    ops = build_assay_operations_bundle(limit=limit)
    candidates = [_candidate_row(row) for row in ops["candidates"]]
    return {
        "title": "Gladstone pilot design",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "accepted_state_mutations": 0,
        "model_in_trust_path": "no",
        "scope": "bench planning, not accepted biological state",
        "source_artifact": "examples/data/assay_operations_bundle.json",
        "sample_plan": {
            "sample": "primary human CD4+ T cells",
            "donor_replicates": DONOR_REPLICATES,
            "conditions": CONDITIONS,
            "candidate_count": len(candidates),
            "control_arms": len(NEGATIVE_CONTROLS) + len(POSITIVE_CONTROLS) - 1,
            "culture_arms": _culture_arms(len(candidates)),
            "batching": "one donor preparation per batch, all conditions and controls matched within donor",
            "readouts": [
                "activation-marker flow cytometry",
                "targeted RNA-seq at 8h and 48h",
                "knockdown confirmation before interpreting response",
            ],
        },
        "controls": {
            "negative": NEGATIVE_CONTROLS,
            "positive": POSITIVE_CONTROLS,
            "control_note": (
                "unstimulated matched culture is represented by the Rest condition rather than an extra perturbation arm"
            ),
        },
        "decision_gates": [
            "knockdown gate passes before interpretation",
            "stimulated signal is stronger than matched Rest signal",
            "non-immune transfer context does not explain the CD4+ signal",
            "follow-up evidence is replayed before any status change",
            "human signature is required before accepted state changes",
        ],
        "candidates": candidates,
    }


def _join(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if value is None:
        return ""
    return str(value)


def _write_csv(packet: dict[str, Any], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "queue", "strongest_condition",
        "primary_question", "promote_if", "weaken_if", "reject_if", "acceptance_gate",
        "missing_evidence_before_acceptance", "replay_links",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in packet["candidates"]:
            writer.writerow({field: _join(row.get(field)) for field in fields})


def _markdown(packet: dict[str, Any]) -> str:
    sample = packet["sample_plan"]
    lines = [
        "# Gladstone pilot design",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. This is bench planning, not accepted biological state.",
        "",
        "## Sample plan",
        "",
        f"- Sample: {sample['sample']}",
        f"- Donor replicates: {sample['donor_replicates']}",
        f"- Conditions: {', '.join(sample['conditions'])}",
        f"- Candidate rows: {sample['candidate_count']}",
        f"- Culture arms: {sample['culture_arms']} culture arms",
        f"- Batching: {sample['batching']}",
        "",
        "## Controls",
        "",
        "- Negative: " + ", ".join(packet["controls"]["negative"]),
        "- Positive: " + ", ".join(packet["controls"]["positive"]),
        "",
        "## Candidate decisions",
        "",
        "| rank | gene | queue | primary question | promote if | reject if |",
        "|---:|---|---|---|---|---|",
    ]
    for row in packet["candidates"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['queue']} | {row['primary_question']} | "
            f"{row['promote_if']} | {row['reject_if']} |"
        )
    lines += [
        "",
        "## Gates",
        "",
    ]
    lines += [f"- {gate}" for gate in packet["decision_gates"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect pilot-design",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_pilot_design(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
    limit: int = 5,
) -> dict[str, Any]:
    packet = build_pilot_design(limit=limit)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    _write_csv(packet, out_csv)
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_pilot_design()
    print(f"wrote {OUT_JSON} ({len(packet['candidates'])} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
