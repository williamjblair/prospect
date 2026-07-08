"""Build the rank-4 RWDD2B defended-evidence packet from frozen packets."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
DECISIONS_JSON = DATA / "defended_candidate_decisions.json"
PREREG_JSON = DATA / "defended_discovery_preregistration.json"
OUT_JSON = DATA / "rwdd2b_defended_evidence.json"
OUT_DOC = ROOT / "docs" / "RWDD2B_DEFENDED_EVIDENCE.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required frozen source: {path}")
    return json.loads(path.read_text())


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _row(packet: dict[str, Any], gene: str) -> dict[str, Any]:
    return next(row for row in packet["candidates"] if row["gene"] == gene)


def _next_candidate(discovery: dict[str, Any], rank: int) -> dict[str, Any]:
    row = next(candidate for candidate in discovery["candidates"] if candidate["rank"] == rank + 1)
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "required_next_packet": f"rank_{row['rank']}_{row['gene'].lower()}_defended_evidence",
    }


def _scored_evidence(discovery_row: dict[str, Any], cross_row: dict[str, Any]) -> list[dict[str, Any]]:
    screens = cross_row["external_screen_summary"]
    string_partners = cross_row["string_network"]["top_partners"]
    string_summary = (
        "top partners: " + ", ".join(string_partners[:5])
        if string_partners
        else "no STRING partners attached in frozen packet"
    )
    return [
        {
            "source": "marson_frontier",
            "status": "computationally_reproduced",
            "summary": (
                f"{discovery_row['stim_max_de']} stimulated DE genes, "
                f"{discovery_row['rest_de']} Rest DE genes"
            ),
        },
        {
            "source": "replogle_specificity",
            "status": "evidence_attached",
            "summary": f"K562 {discovery_row['k562_de']}; RPE1 {discovery_row['rpe1_de']}",
        },
        {
            "source": "primary_t_cell_screen_support",
            "status": "evidence_attached",
            "summary": (
                "no supporting Shifrut or Schmidt primary T-cell hit in the frozen cross-validation packet"
            ),
            "supporting_hits": screens["supporting_hits"],
            "non_hits": screens["non_hits"],
        },
        {
            "source": "schmidt_2022_orcs_2427",
            "status": "orthogonal_phenotype",
            "summary": "cytokine-production non-hit, not a comparable activation-transcriptome contradiction",
        },
        {
            "source": "string_network",
            "status": "evidence_attached",
            "summary": string_summary,
        },
        {
            "source": "dice_expression",
            "status": "evidence_attached",
            "summary": (
                f"activated CD4 mean TPM {cross_row['dice_expression']['activated_cd4_mean_tpm']}"
            ),
        },
        {
            "source": "open_targets_overlay",
            "status": "evidence_attached",
            "summary": cross_row["open_targets"]["overlay_class"],
        },
    ]


def _clearance_failures() -> list[dict[str, str]]:
    return [
        {
            "rung": "independent_primary_t_cell_support",
            "reason": (
                "RWDD2B has no supporting hit in Shifrut 2018 and Schmidt remains an orthogonal "
                "cytokine-production phenotype"
            ),
        },
        {
            "rung": "real_world_hook",
            "reason": "the bounded Open Targets overlay has no selected immune or hematologic context for RWDD2B",
        },
        {
            "rung": "specific_mechanism",
            "reason": (
                "no STRING partners are attached, so the frozen packet does not state a specific "
                "stimulated CD4+ activation mechanism"
            ),
        },
    ]


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "result": "survives_current_frozen_evidence",
            "basis": "the frozen campaign row has on-target stimulated knockdown",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "result": "not_cleared",
            "basis": "Rest DE is 190, so the non-activation artifact kill remains open",
        },
        {
            "kill_id": "batch_or_dataset_specificity",
            "result": "not_cleared",
            "basis": "no supporting primary T-cell screen hit is attached",
        },
        {
            "kill_id": "alternative_mechanism",
            "result": "not_cleared",
            "basis": "no STRING network or disease hook supplies a specific activation mechanism",
        },
    ]


def build_rwdd2b_defended_evidence() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    _load(DECISIONS_JSON)
    discovery_row = _row(discovery, "RWDD2B")
    cross_row = _row(cross_validation, "RWDD2B")
    packet = {
        "phase": "rank_4_rwdd2b_defended_evidence",
        "title": "RWDD2B defended evidence",
        "gene": "RWDD2B",
        "candidate_rank": discovery_row["rank"],
        "status": "evidence_attached",
        "defended_discovery_status": "not_cleared_full_bar",
        "accepted": False,
        "acceptance": False,
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": prereg["pre_registration_id"],
        "source_packets": {
            "cross_validation": "examples/data/cross_validation.json",
            "decision_ledger": "examples/data/defended_candidate_decisions.json",
            "discovery_campaign": "examples/data/discovery_campaign.json",
        },
        "scored_evidence": _scored_evidence(discovery_row, cross_row),
        "clearance_failures": _clearance_failures(),
        "kill_attempts": _kill_attempts(),
        "decision_recommendation": "demote_and_advance",
        "next_candidate": _next_candidate(discovery, discovery_row["rank"]),
        "falsifiable_experiment": discovery_row["falsifiable_test"],
        "reproduce_command": "./prospect rwdd2b-defended-evidence",
        "next_step": "record RWDD2B decision and build rank-5 CCDC22 defended evidence",
    }
    packet["packet_id"] = _hash_obj("rwdd2b_defended", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# RWDD2B defended evidence",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        f"Defended-discovery status: `{packet['defended_discovery_status']}`.",
        "Plain-language status: not cleared full bar.",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "## Frozen evidence",
        "",
        "| source | status | summary |",
        "|---|---|---|",
    ]
    for row in packet["scored_evidence"]:
        lines.append(f"| `{row['source']}` | `{row['status']}` | {row['summary']} |")
    lines += [
        "",
        "## Clearance failures",
        "",
        "| rung | reason |",
        "|---|---|",
    ]
    for row in packet["clearance_failures"]:
        lines.append(f"| `{row['rung']}` | {row['reason']} |")
    lines += [
        "",
        "## Kill attempts",
        "",
        "| kill | result | basis |",
        "|---|---|---|",
    ]
    for row in packet["kill_attempts"]:
        lines.append(f"| `{row['kill_id']}` | `{row['result']}` | {row['basis']} |")
    next_candidate = packet["next_candidate"]
    lines += [
        "",
        f"Decision recommendation: `{packet['decision_recommendation']}`.",
        f"Next candidate: {next_candidate['gene']} at rank {next_candidate['rank']}.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect rwdd2b-defended-evidence",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_rwdd2b_defended_evidence(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_rwdd2b_defended_evidence()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_rwdd2b_defended_evidence()
    print(f"wrote {OUT_JSON} ({packet['defended_discovery_status']})")
    print(f"wrote {OUT_DOC}")
    print(f"packet_id {packet['packet_id']}")


if __name__ == "__main__":
    main()
