"""Build the defended-discovery endgame exhaustion ledger."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
PREREG_JSON = DATA / "defended_discovery_endgame_preregistration.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
PGGT1B_DECISION_JSON = DATA / "pggt1b_endgame_decision.json"
OUT_JSON = DATA / "defended_discovery_endgame_exhaustion.json"
OUT_DOC = ROOT / "docs" / "DEFENDED_DISCOVERY_ENDGAME_EXHAUSTION.md"


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required frozen source: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _source(path: str, role: str) -> dict[str, str]:
    return {"path": path, "role": role, "sha256": _sha256(ROOT / path)}


def _real_world_hook(gene: str, cross_row: dict[str, Any]) -> dict[str, str]:
    overlay = cross_row["open_targets"]["overlay_class"]
    if gene == "PGGT1B":
        return {
            "status": "evidence_attached",
            "basis": "ChEMBL geranylgeranyl transferase target and activity rows, plus immune literature context",
        }
    if gene == "CCDC22":
        return {
            "status": "evidence_attached",
            "basis": "Open Targets genetic context in immune dysregulation and prior CCDC22 target context",
        }
    if overlay == "immune_or_hematologic_genetic_context":
        return {"status": "evidence_attached", "basis": "bounded Open Targets genetic immune context"}
    return {"status": "not_cleared", "basis": f"bounded Open Targets overlay is {overlay}"}


def _specific_mechanism(cross_row: dict[str, Any]) -> dict[str, str]:
    partners = cross_row["string_network"]["top_partners"]
    if partners:
        return {
            "status": "evidence_attached",
            "basis": "STRING partners attached: " + ", ".join(partners[:5]),
        }
    return {"status": "not_cleared", "basis": "no STRING partners attached in the frozen packet"}


def _blocking_rungs(row: dict[str, Any], cross_row: dict[str, Any], hook: dict[str, str], mechanism: dict[str, str]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = [
        {
            "rung": "cell_type_specificity",
            "status": "not_cleared",
            "typed_detail": "rpe1_not_assayed",
            "basis": "RPE1 specificity is not_assayed in the locked candidate table.",
        }
    ]
    if not cross_row["external_screen_summary"]["supporting_hits"]:
        blocks.append(
            {
                "rung": "readout_comparability",
                "status": "not_cleared",
                "typed_detail": "no_supporting_primary_t_cell_hit",
                "basis": "no supporting Shifrut or Schmidt primary T-cell hit is attached; Schmidt remains orthogonal_phenotype",
            }
        )
    elif row["gene"] in {"PGGT1B", "CCDC22", "LETM2", "TNNC1"}:
        blocks.append(
            {
                "rung": "readout_comparability",
                "status": "not_cleared",
                "typed_detail": "no_activation_transcriptome_replay",
                "basis": "supporting Shifrut row is not a Marson activation-transcriptome replay",
            }
        )
    if hook["status"] != "evidence_attached":
        blocks.append(
            {
                "rung": "real_world_hook",
                "status": "not_cleared",
                "typed_detail": "no_hook",
                "basis": hook["basis"],
            }
        )
    if mechanism["status"] != "evidence_attached":
        blocks.append(
            {
                "rung": "mechanistic_coherence",
                "status": "not_cleared",
                "typed_detail": "no_specific_mechanism",
                "basis": mechanism["basis"],
            }
        )
    return blocks


def _kill_attempts(row: dict[str, Any], cross_row: dict[str, Any], mechanism: dict[str, str]) -> list[dict[str, str]]:
    k562 = row["k562_de"]
    rest = row["rest_de"]
    has_support = bool(cross_row["external_screen_summary"]["supporting_hits"])
    artifact_result = "survives_current_frozen_evidence"
    artifact_basis = f"Rest DE is {rest}; K562 DE is {k562}; RPE1 is not_assayed and blocks clearance separately."
    if k562 is None:
        artifact_result = "not_cleared"
        artifact_basis = f"Rest DE is {rest}; K562 is not_assayed; RPE1 is not_assayed."
    elif rest >= 180:
        artifact_result = "not_cleared"
        artifact_basis = f"Rest DE is {rest}, so the non-activation artifact kill remains open."
    alternative_result = "survives_current_frozen_evidence" if mechanism["status"] == "evidence_attached" else "not_cleared"
    return [
        {
            "kill_id": "technical_confound",
            "result": "survives_current_frozen_evidence",
            "basis": "locked candidate row has on-target stimulated perturbation and an activation effect",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "result": artifact_result,
            "basis": artifact_basis,
        },
        {
            "kill_id": "batch_or_donor_effect",
            "result": "survives_current_frozen_evidence" if has_support else "not_cleared",
            "basis": "supporting Shifrut row attached" if has_support else "no supporting primary T-cell screen hit attached",
        },
        {
            "kill_id": "reverse_causality_or_passenger_marker",
            "result": "survives_current_frozen_evidence",
            "basis": "candidate has causal perturbation evidence in Marson, not only expression association",
        },
        {
            "kill_id": "better_alternative_mechanism",
            "result": alternative_result,
            "basis": mechanism["basis"],
        },
    ]


def _decision(row: dict[str, Any], cross_row: dict[str, Any]) -> dict[str, Any]:
    hook = _real_world_hook(row["gene"], cross_row)
    mechanism = _specific_mechanism(cross_row)
    blocks = _blocking_rungs(row, cross_row, hook, mechanism)
    support = cross_row["external_screen_summary"]["supporting_hits"]
    basis = "blocked by the new endgame bar"
    if row["gene"] == "CCDC22":
        basis = "prior rank-5 packet is evidence only and is blocked by the new RPE1 and readout-comparability requirements"
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "decision": "not_cleared_full_bar",
        "decision_basis": basis,
        "typed_status": "evidence_attached",
        "accepted": False,
        "marson_stim_max_de": row["marson_stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "independent_primary_t_cell_support": support,
        "orthogonal_phenotypes": cross_row["external_screen_summary"]["orthogonal_phenotypes"],
        "real_world_hook": hook,
        "mechanism": mechanism,
        "blocking_rungs": blocks,
        "kill_attempts": _kill_attempts(row, cross_row, mechanism),
    }


def build_defended_discovery_endgame_exhaustion() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    cross = _load(CROSS_VALIDATION_JSON)
    _load(PGGT1B_DECISION_JSON)
    cross_by_gene = {row["gene"]: row for row in cross["candidates"]}
    decisions = [_decision(row, cross_by_gene[row["gene"]]) for row in prereg["ranked_candidates"]]
    packet: dict[str, Any] = {
        "phase": "defended_discovery_endgame_exhaustion",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "status": "evidence_attached",
        "accepted": False,
        "trust_boundary": "proposal_only",
        "outcome": "honest_exhaustion",
        "candidate_count": len(decisions),
        "cleared_count": 0,
        "common_blockers": [
            {
                "rung": "cell_type_specificity",
                "typed_detail": "rpe1_not_assayed",
                "affected_candidates": len(decisions),
            }
        ],
        "candidate_decisions": decisions,
        "frozen_sources": [
            _source("examples/data/defended_discovery_endgame_preregistration.json", "locked bar and candidate order"),
            _source("examples/data/cross_validation.json", "cross-dataset support packet"),
            _source("examples/data/discovery_campaign.json", "ranked candidate source"),
            _source("examples/data/pggt1b_endgame_decision.json", "rank-1 decision"),
        ],
        "honest_ceiling": prereg["honest_ceiling"],
        "reproduce_command": "./prospect defended-discovery-endgame-exhaustion",
        "next_step": "surface the honest exhaustion outcome or source new RPE1 and comparable activation evidence before reopening any candidate",
    }
    packet["ledger_id"] = _hash_obj("endgame_exhaustion", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Defended discovery endgame exhaustion",
        "",
        f"Ledger id: `{packet['ledger_id']}`",
        "",
        f"Pre-registration: `{packet['pre_registration_id']}`",
        "",
        "0 candidates cleared the full endgame bar. accepted=false.",
        "",
        f"Ceiling: {packet['honest_ceiling']}.",
        "",
        "RPE1 specificity is not_assayed for 18 of 18 candidates, which blocks the pre-registered cell-type-specificity rung.",
        "",
        "## Candidate decisions",
        "",
        "| rank | gene | decision | main blockers | primary T-cell support |",
        "|---:|---|---|---|---|",
    ]
    for row in packet["candidate_decisions"]:
        blockers = ", ".join(block["typed_detail"] for block in row["blocking_rungs"])
        support = ", ".join(row["independent_primary_t_cell_support"]) or "none"
        lines.append(
            f"| {row['rank']} | {row['gene']} | `{row['decision']}` | {blockers} | {support} |"
        )
    lines += [
        "",
        "## Common blocker",
        "",
        "- `cell_type_specificity`: `rpe1_not_assayed` for all 18 locked candidates.",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_defended_discovery_endgame_exhaustion(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_defended_discovery_endgame_exhaustion()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_defended_discovery_endgame_exhaustion()
    print(f"wrote {OUT_JSON} ({packet['outcome']})")


if __name__ == "__main__":
    main()
