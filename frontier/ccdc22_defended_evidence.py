"""Build the rank-5 CCDC22 defended-evidence packet from frozen packets."""
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
OUT_JSON = DATA / "ccdc22_defended_evidence.json"
OUT_DOC = ROOT / "docs" / "CCDC22_DEFENDED_EVIDENCE.md"

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


def _disease_summary(cross_row: dict[str, Any]) -> str:
    top = cross_row["open_targets"]["top_context"]
    return (
        f"{top['disease_or_trait']}, genetic association score "
        f"{top['datatype_scores'][0]['score']}"
    )


def _scored_evidence(discovery_row: dict[str, Any], cross_row: dict[str, Any]) -> list[dict[str, Any]]:
    screens = cross_row["external_screen_summary"]
    partners = cross_row["string_network"]["top_partners"]
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
            "summary": "supporting hit: " + ", ".join(screens["supporting_hits"]),
            "supporting_hits": screens["supporting_hits"],
            "missing_rows": screens["missing_rows"],
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
            "summary": "top partners: " + ", ".join(partners[:5]),
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
            "summary": _disease_summary(cross_row),
        },
    ]


def _open_gates() -> list[dict[str, str]]:
    return [
        {
            "gate": "expanded_external_freeze",
            "reason": (
                "the expanded hackathon bar still needs new frozen GWAS Catalog, DepMap, "
                "conservation, or additional primary-T-cell comparator evidence"
            ),
        },
        {
            "gate": "shifrut_replication_depth",
            "reason": "one Shifrut row supports CCDC22, while the second Shifrut row is missing from the frozen packet",
        },
        {
            "gate": "human_acceptance",
            "reason": "no human key has accepted a CCDC22 state transition",
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
            "result": "survives_current_frozen_evidence",
            "basis": "Rest DE is 116 and K562 DE is 13, below the pre-registered artifact ceilings",
        },
        {
            "kill_id": "batch_or_dataset_specificity",
            "result": "survives_current_frozen_evidence",
            "basis": "Shifrut 2018 row 1107 supports the candidate in an independent primary T-cell screen",
        },
        {
            "kill_id": "alternative_mechanism",
            "result": "survives_current_frozen_evidence",
            "basis": "STRING centers CCDC22 in the CCC and COMMD retromer-associated trafficking complex",
        },
    ]


def build_ccdc22_defended_evidence() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    _load(DECISIONS_JSON)
    discovery_row = _row(discovery, "CCDC22")
    cross_row = _row(cross_validation, "CCDC22")
    packet = {
        "phase": "rank_5_ccdc22_defended_evidence",
        "title": "CCDC22 defended evidence",
        "gene": "CCDC22",
        "candidate_rank": discovery_row["rank"],
        "status": "evidence_attached",
        "defended_discovery_status": "needs_external_freeze",
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
        "current_support_count": 5,
        "scored_evidence": _scored_evidence(discovery_row, cross_row),
        "open_gates": _open_gates(),
        "kill_attempts": _kill_attempts(),
        "mechanism": (
            "CCDC22 may connect stimulated CD4+ activation state to CCC and COMMD "
            "retromer-associated endosomal trafficking."
        ),
        "real_world_hook": _disease_summary(cross_row),
        "decision_recommendation": "hold_and_deepen",
        "next_candidate": None,
        "falsifiable_experiment": discovery_row["falsifiable_test"],
        "reproduce_command": "./prospect ccdc22-defended-evidence",
        "next_step": "freeze expanded external datasets before any CCDC22 discovery claim",
    }
    packet["packet_id"] = _hash_obj("ccdc22_defended", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# CCDC22 defended evidence",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        "Plain-language status: needs external freeze.",
        f"Defended-discovery status: `{packet['defended_discovery_status']}`.",
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
        "## Open gates",
        "",
        "| gate | reason |",
        "|---|---|",
    ]
    for row in packet["open_gates"]:
        lines.append(f"| `{row['gate']}` | {row['reason']} |")
    lines += [
        "",
        "## Kill attempts",
        "",
        "| kill | result | basis |",
        "|---|---|---|",
    ]
    for row in packet["kill_attempts"]:
        lines.append(f"| `{row['kill_id']}` | `{row['result']}` | {row['basis']} |")
    lines += [
        "",
        f"Mechanism: {packet['mechanism']}",
        f"Real-world hook: {packet['real_world_hook']}.",
        f"Decision recommendation: `{packet['decision_recommendation']}`.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect ccdc22-defended-evidence",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_ccdc22_defended_evidence(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_ccdc22_defended_evidence()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_ccdc22_defended_evidence()
    print(f"wrote {OUT_JSON} ({packet['defended_discovery_status']})")
    print(f"wrote {OUT_DOC}")
    print(f"packet_id {packet['packet_id']}")


if __name__ == "__main__":
    main()
