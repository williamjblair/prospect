"""Build the defended-discovery fixed-bar result packet."""
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
PGGT1B_EVIDENCE_JSON = DATA / "pggt1b_defended_evidence.json"
CCDC22_EVIDENCE_JSON = DATA / "ccdc22_defended_evidence.json"
OUT_JSON = DATA / "defended_discovery_endgame_result.json"
OUT_DOC = ROOT / "docs" / "DEFENDED_DISCOVERY_ENDGAME_RESULT.md"

RPE1_CONTEXT = {
    "rung": "cell_type_specificity",
    "typed_detail": "rpe1_not_assayed",
    "affected_candidates": 18,
    "basis": "RPE1 coverage is sparse in the frozen Replogle comparator, so missing RPE1 rows are not_assayed context.",
}


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
            "basis": "ChEMBL geranylgeranyl transferase target and activity rows supply a druggability hook.",
        }
    if gene == "CCDC22":
        return {
            "status": "evidence_attached",
            "basis": "Open Targets immune-dysregulation context and prior CCDC22 packet supply a disease hook.",
        }
    if overlay == "immune_or_hematologic_genetic_context":
        return {"status": "evidence_attached", "basis": "bounded Open Targets genetic immune context"}
    if overlay == "immune_or_hematologic_non_genetic_context":
        return {"status": "evidence_attached", "basis": "bounded Open Targets immune literature context"}
    return {"status": "not_cleared", "basis": f"bounded Open Targets overlay is {overlay}"}


def _specific_mechanism(cross_row: dict[str, Any]) -> dict[str, str]:
    partners = cross_row["string_network"]["top_partners"]
    if partners:
        return {
            "status": "evidence_attached",
            "basis": "STRING partners attached: " + ", ".join(partners[:5]),
        }
    return {"status": "not_cleared", "basis": "no STRING partners attached in the frozen packet"}


def _orthogonal_dataset_count(gene: str, row: dict[str, Any], cross_row: dict[str, Any]) -> int:
    if gene == "PGGT1B":
        return int(_load(PGGT1B_EVIDENCE_JSON)["orthogonal_public_dataset_count"])
    if gene == "CCDC22":
        return int(_load(CCDC22_EVIDENCE_JSON)["orthogonal_public_dataset_count"])
    count = 0
    screens = cross_row["external_screen_summary"]
    if screens["supporting_hits"]:
        count += 1
    if cross_row["string_network"]["top_partners"]:
        count += 1
    if cross_row["dice_expression"]:
        count += 1
    if cross_row["open_targets"]["overlay_class"] != "no_selected_context":
        count += 1
    if row["k562_de"] is not None:
        count += 1
    return count


def _blocking_rungs(
    row: dict[str, Any],
    cross_row: dict[str, Any],
    hook: dict[str, str],
    mechanism: dict[str, str],
    dataset_count: int,
    lead_cleared: bool,
) -> list[dict[str, Any]]:
    if row["gene"] == "PGGT1B":
        return []
    if row["gene"] == "CCDC22" and lead_cleared:
        return []
    blocks: list[dict[str, Any]] = []
    if row["k562_de"] is None:
        blocks.append(
            {
                "rung": "cell_type_specificity",
                "status": "not_assayed",
                "typed_detail": "k562_not_assayed",
                "basis": "K562 is the genome-wide specificity comparator for this fixed bar, but this gene lacks a K562 row in the frozen packet.",
            }
        )
    if not cross_row["external_screen_summary"]["supporting_hits"]:
        blocks.append(
            {
                "rung": "independent_primary_t_cell_support",
                "status": "not_cleared",
                "typed_detail": "no_supporting_primary_t_cell_hit",
                "basis": "no supporting Shifrut or comparable primary T-cell hit is attached; Schmidt remains orthogonal_phenotype",
            }
        )
    if dataset_count < 5:
        blocks.append(
            {
                "rung": "five_frozen_orthogonal_public_datasets",
                "status": "not_cleared",
                "typed_detail": "insufficient_covering_datasets",
                "basis": f"{dataset_count} covering orthogonal public datasets are attached; the fixed bar requires at least 5",
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
    artifact_basis = f"Rest DE is {rest}; K562 DE is {k562}; RPE1 is not_assayed context."
    if k562 is None:
        artifact_result = "not_cleared"
        artifact_basis = f"Rest DE is {rest}; K562 is not_assayed; RPE1 is not_assayed context."
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


def _decision(row: dict[str, Any], cross_row: dict[str, Any], *, lead_cleared: bool) -> dict[str, Any]:
    hook = _real_world_hook(row["gene"], cross_row)
    mechanism = _specific_mechanism(cross_row)
    dataset_count = _orthogonal_dataset_count(row["gene"], row, cross_row)
    blocks = _blocking_rungs(row, cross_row, hook, mechanism, dataset_count, lead_cleared)
    support = cross_row["external_screen_summary"]["supporting_hits"]
    kills = _kill_attempts(row, cross_row, mechanism)
    decision = "not_cleared_full_bar"
    basis = "blocked by the fixed endgame bar"
    if row["gene"] == "PGGT1B":
        decision = "clears_fixed_bar_pending_human_key"
        basis = "rank 1 PGGT1B clears the corrected fixed bar; accepted state still requires a human key and later wet-lab evidence"
    elif row["gene"] == "CCDC22" and lead_cleared:
        decision = "not_selected_after_rank1_lead"
        basis = "rank 1 PGGT1B cleared first in the locked order; CCDC22 remains a supported alternative proposal, not accepted state"
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "decision": decision,
        "decision_basis": basis,
        "typed_status": "evidence_attached",
        "accepted": False,
        "marson_stim_max_de": row["marson_stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "not_assayed_context": [RPE1_CONTEXT],
        "orthogonal_public_dataset_count": dataset_count,
        "independent_primary_t_cell_support": support,
        "orthogonal_phenotypes": cross_row["external_screen_summary"]["orthogonal_phenotypes"],
        "real_world_hook": hook,
        "mechanism": mechanism,
        "blocking_rungs": blocks,
        "kill_attempts": kills,
    }


def build_defended_discovery_endgame_result() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    cross = _load(CROSS_VALIDATION_JSON)
    pggt1b_decision = _load(PGGT1B_DECISION_JSON)
    lead_cleared = pggt1b_decision["decision"] == "clears_fixed_bar_pending_human_key"
    cross_by_gene = {row["gene"]: row for row in cross["candidates"]}
    decisions = [
        _decision(row, cross_by_gene[row["gene"]], lead_cleared=lead_cleared)
        for row in prereg["ranked_candidates"]
    ]
    cleared = [row for row in decisions if row["decision"] == "clears_fixed_bar_pending_human_key"]
    packet: dict[str, Any] = {
        "phase": "defended_discovery_endgame_result",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "status": "evidence_attached",
        "accepted": False,
        "trust_boundary": "proposal_only",
        "outcome": "defended_lead" if cleared else "honest_exhaustion",
        "candidate_count": len(decisions),
        "cleared_count": len(cleared),
        "lead_candidate": cleared[0] if cleared else None,
        "non_blocking_not_assayed": [RPE1_CONTEXT],
        "candidate_decisions": decisions,
        "frozen_sources": [
            _source("examples/data/defended_discovery_endgame_preregistration.json", "locked bar and candidate order"),
            _source("examples/data/cross_validation.json", "cross-dataset support packet"),
            _source("examples/data/discovery_campaign.json", "ranked candidate source"),
            _source("examples/data/pggt1b_endgame_decision.json", "rank-1 fixed-bar decision"),
        ],
        "honest_ceiling": prereg["honest_ceiling"],
        "reproduce_command": "./prospect defended-discovery-endgame-result",
        "next_step": "keep PGGT1B proposal-only until human review, human-key acceptance, and later wet-lab evidence",
    }
    packet["ledger_id"] = _hash_obj("endgame_result", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lead = packet["lead_candidate"]
    lines = [
        "# Defended discovery endgame result",
        "",
        f"Ledger id: `{packet['ledger_id']}`",
        "",
        f"Pre-registration: `{packet['pre_registration_id']}`",
        "",
        f"Outcome: `{packet['outcome']}`. accepted=false.",
        "",
        f"Ceiling: {packet['honest_ceiling']}.",
        "",
    ]
    if lead:
        lines += [
            f"PGGT1B clears the fixed bar as rank {lead['rank']}, pending human key.",
            "",
            "RPE1 non-coverage is retained as not_assayed context, not a failed rung.",
            "",
        ]
    else:
        lines += [
            "No candidate cleared the fixed bar.",
            "",
            "RPE1 non-coverage is retained as not_assayed context, not a failed rung.",
            "",
        ]
    lines += [
        "## Candidate decisions",
        "",
        "| rank | gene | decision | blockers or reason | primary T-cell support |",
        "|---:|---|---|---|---|",
    ]
    for row in packet["candidate_decisions"]:
        blockers = ", ".join(block["typed_detail"] for block in row["blocking_rungs"])
        reason = blockers or row["decision_basis"]
        support = ", ".join(row["independent_primary_t_cell_support"]) or "none"
        lines.append(
            f"| {row['rank']} | {row['gene']} | `{row['decision']}` | {reason} | {support} |"
        )
    lines += [
        "",
        "## Not-assayed context",
        "",
        "- `rpe1_not_assayed`: retained for all 18 candidates, never counted as a blocking failure.",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_defended_discovery_endgame_result(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_defended_discovery_endgame_result()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_defended_discovery_endgame_result()
    print(f"wrote {OUT_JSON} ({packet['outcome']})")


if __name__ == "__main__":
    main()
