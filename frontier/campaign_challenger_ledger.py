"""Build a deterministic challenger ledger over shipped campaign packets."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "campaign_challenger_ledger.json"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_CHALLENGER_LEDGER.md"
SIG = ROOT / "frontier" / "frontier.sig.json"

SOURCE_ARTIFACTS = [
    "examples/data/agent_campaign.json",
    "examples/data/agent_campaign_review.json",
    "examples/data/campaign_pressure_summary.json",
    "examples/data/donor_condition_replay.json",
    "examples/data/cross_substrate_discovery.json",
    "examples/data/disease_genetics_overlay.json",
]

ACTION_ORDER = [
    "retain_primary_panel",
    "promote_if_capacity",
    "contextual_priority",
    "hold_for_review",
    "demote_or_control",
    "challenge_primary_panel",
]


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def _by_gene(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["gene"]: row for row in rows}


def _source_rows() -> dict[str, Any]:
    campaign = _json(DATA / "agent_campaign.json")
    review = _json(DATA / "agent_campaign_review.json")
    pressure = _json(DATA / "campaign_pressure_summary.json")
    donor = _json(DATA / "donor_condition_replay.json")
    cross = _json(DATA / "cross_substrate_discovery.json")
    disease = _json(DATA / "disease_genetics_overlay.json")
    return {
        "campaign": campaign,
        "review": _by_gene(review["rows"]),
        "pressure": _by_gene(pressure["pressure_accounting"]),
        "donor": _by_gene(donor["rows"]),
        "cross": _by_gene(cross["campaign_intersections"]),
        "disease": _by_gene(disease["rows"]),
    }


def _action(
    current_primary: str,
    donor_class: str,
    cross_class: str,
    gate_recommendation: str,
    disease_class: str,
) -> str:
    if current_primary == "yes" and (
        donor_class in {"donor_fragile", "guide_limited"}
        or gate_recommendation == "lower_priority"
        or cross_class != "t_cell_specific_activation"
    ):
        return "challenge_primary_panel"
    if current_primary == "yes" and donor_class == "donor_supported" and cross_class == "t_cell_specific_activation":
        return "retain_primary_panel"
    if donor_class == "donor_supported" and cross_class == "t_cell_specific_activation" and gate_recommendation == "gate_sufficient":
        return "promote_if_capacity"
    if donor_class in {"donor_fragile", "guide_limited"} or cross_class != "t_cell_specific_activation":
        return "demote_or_control"
    if disease_class == "immune_or_hematologic_genetic_context":
        return "contextual_priority"
    return "hold_for_review"


def _evidence_score(row: dict[str, Any]) -> int:
    score = int(row["campaign_score"])
    if row["donor_replay_class"] == "donor_supported":
        score += 200
    if row["donor_replay_class"] in {"donor_fragile", "guide_limited"}:
        score -= 600
    if row["cross_substrate_class"] == "t_cell_specific_activation":
        score += 200
    else:
        score -= 300
    if row["gate_recommendation"] == "gate_sufficient":
        score += 100
    if row["gate_recommendation"] == "lower_priority":
        score -= 500
    if row["disease_overlay_class"] == "immune_or_hematologic_genetic_context":
        score += 50
    return score


def _recommended_change(action: str, current_primary: str) -> str:
    if action == "challenge_primary_panel":
        return "remove_from_primary_panel"
    if action == "promote_if_capacity":
        return "add_to_primary_panel"
    if current_primary == "yes":
        return "keep_in_primary_panel"
    return "none"


def _reason(row: dict[str, Any]) -> str:
    if row["challenger_action"] == "challenge_primary_panel":
        return (
            f"{row['gene']} is in the current primary panel, but donor replay is "
            f"{row['donor_replay_class']} and the gate recommendation is {row['gate_recommendation']}."
        )
    if row["challenger_action"] == "promote_if_capacity":
        return (
            f"{row['gene']} is donor-supported, T-cell-specific across substrates, and its disagreement gate "
            "was sufficient."
        )
    if row["challenger_action"] == "contextual_priority":
        return f"{row['gene']} has selected immune or hematologic genetic context outside accepted state."
    if row["challenger_action"] == "retain_primary_panel":
        return f"{row['gene']} remains supported by donor replay and the cross-substrate packet."
    if row["challenger_action"] == "demote_or_control":
        return f"{row['gene']} needs control-heavy review before scarce primary assay capacity."
    return f"{row['gene']} remains a proposal-only review row."


def _ledger_row(
    campaign_row: dict[str, Any],
    review: dict[str, dict[str, Any]],
    pressure: dict[str, dict[str, Any]],
    donor: dict[str, dict[str, Any]],
    cross: dict[str, dict[str, Any]],
    disease: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gene = campaign_row["gene"]
    pressure_row = pressure[gene]
    current_primary = "yes" if int(campaign_row["rank"]) <= 5 else "no"
    donor_class = donor[gene]["donor_replay_class"]
    cross_class = cross[gene]["cross_substrate_class"]
    disease_class = disease[gene]["overlay_class"]
    gate_recommendation = pressure_row["gate_recommendation"]
    action = _action(current_primary, donor_class, cross_class, gate_recommendation, disease_class)
    row = {
        "rank": campaign_row["rank"],
        "gene": gene,
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "current_primary_panel": current_primary,
        "campaign_score": campaign_row["score"],
        "review_decision": review[gene]["decision"],
        "claude_pressure_alignment": pressure_row["alignment"],
        "gate_recommendation": gate_recommendation,
        "donor_replay_class": donor_class,
        "cross_substrate_class": cross_class,
        "disease_overlay_class": disease_class,
        "challenger_action": action,
        "recommended_change": _recommended_change(action, current_primary),
        "stim_max_de": campaign_row["stim_max_de"],
        "rest_de": campaign_row["rest_de"],
        "k562_de": campaign_row["k562_de"],
        "rpe1_de": campaign_row["rpe1_de"],
    }
    row["challenger_score"] = _evidence_score(row)
    row["reason"] = _reason(row)
    return row


def _recommended_panel(rows: list[dict[str, Any]]) -> list[str]:
    retained = [
        row for row in rows
        if row["current_primary_panel"] == "yes" and row["challenger_action"] != "challenge_primary_panel"
    ]
    promoted = sorted(
        [row for row in rows if row["challenger_action"] == "promote_if_capacity"],
        key=lambda row: (-int(row["challenger_score"]), int(row["rank"]), row["gene"]),
    )
    panel = sorted(retained, key=lambda row: int(row["rank"])) + promoted
    return [row["gene"] for row in panel[:5]]


def build_ledger() -> dict[str, Any]:
    src = _source_rows()
    rows = [
        _ledger_row(row, src["review"], src["pressure"], src["donor"], src["cross"], src["disease"])
        for row in src["campaign"]["candidates"]
    ]
    action_counts = Counter(row["challenger_action"] for row in rows)
    current_panel = [row["gene"] for row in rows if row["current_primary_panel"] == "yes"]
    recommended_panel = _recommended_panel(rows)
    remove = [gene for gene in current_panel if gene not in recommended_panel]
    add = [gene for gene in recommended_panel if gene not in current_panel]
    replacement_candidates = [
        row for row in rows
        if row["challenger_action"] == "promote_if_capacity"
    ]

    counts = {
        "campaign_rows": len(rows),
        "current_primary_panel_rows": len(current_panel),
        "recommended_primary_panel_rows": len(recommended_panel),
        "primary_panel_challenges": len(remove),
        "replacement_candidates": len(replacement_candidates),
    }
    counts.update({action: action_counts.get(action, 0) for action in ACTION_ORDER})

    return {
        "title": "Campaign challenger ledger",
        "status": "evidence_attached",
        "trust_boundary": "frozen_join_over_committed_packets",
        "accepted_state_mutation": "none",
        "model_in_trust_path": "no",
        "signed_frontier_root": _frontier_root(),
        "public_artifact": "/data/campaign_challenger_ledger.json",
        "source_artifacts": SOURCE_ARTIFACTS,
        "method": {
            "model_role": "prior_campaign_pressure_only",
            "model_in_trust_path": "no",
            "accepted_state_mutation": "none",
            "replay_command": "./prospect campaign-challenger",
            "join_key": "campaign gene symbol",
            "panel_rule": "retain current primary rows unless donor, substrate, or gate evidence challenges them; fill open slots with donor-supported T-cell-specific gate-sufficient rows",
        },
        "counts": counts,
        "current_primary_panel": current_panel,
        "recommended_primary_panel": recommended_panel,
        "panel_delta": {
            "remove": remove,
            "add": add,
            "changed": "yes" if remove or add else "no",
        },
        "primary_panel_challenges": [
            row for row in rows if row["recommended_change"] == "remove_from_primary_panel"
        ],
        "replacement_candidates": replacement_candidates,
        "rows": rows,
        "limitations": (
            "This ledger reconciles shipped proposal and replay packets for assay prioritization. "
            "It does not move accepted state or prove a wet-lab result."
        ),
    }


def _markdown(ledger: dict[str, Any]) -> str:
    counts = ledger["counts"]
    lines = [
        "# Campaign challenger ledger",
        "",
        "Status: `evidence_attached`. Trust boundary: frozen join over committed packets.",
        "",
        "No accepted state changes. The ledger challenges assay priority only.",
        "",
        "## Replay",
        "",
        "```bash",
        ledger["method"]["replay_command"],
        "```",
        "",
        "## Panel delta",
        "",
        f"- Current primary panel: {', '.join(ledger['current_primary_panel'])}",
        f"- Recommended primary panel: {', '.join(ledger['recommended_primary_panel'])}",
        f"- Remove: {', '.join(ledger['panel_delta']['remove']) or 'none'}",
        f"- Add: {', '.join(ledger['panel_delta']['add']) or 'none'}",
        "",
        "## Counts",
        "",
        f"- Campaign rows: {counts['campaign_rows']}",
        f"- Primary-panel challenges: {counts['primary_panel_challenges']}",
        f"- Replacement candidates: {counts['replacement_candidates']}",
        f"- Retain primary panel: {counts['retain_primary_panel']}",
        f"- Promote if capacity: {counts['promote_if_capacity']}",
        f"- Demote or control: {counts['demote_or_control']}",
        "",
        "## Challenger rows",
        "",
        "| rank | gene | current panel | donor | substrate | gate | action | change |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in ledger["rows"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['current_primary_panel']} | "
            f"{row['donor_replay_class']} | {row['cross_substrate_class']} | "
            f"{row['gate_recommendation']} | {row['challenger_action']} | {row['recommended_change']} |"
        )
    lines += [
        "",
        ledger["limitations"],
    ]
    return "\n".join(lines) + "\n"


def write_ledger(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    ledger = build_ledger()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(ledger, indent=2) + "\n")
    out_doc.write_text(_markdown(ledger))
    return ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect campaign-challenger")
    parser.add_argument("--json", action="store_true", help="print the challenger ledger as JSON")
    args = parser.parse_args(argv)

    ledger = write_ledger()
    if args.json:
        print(json.dumps(ledger, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(
        "challenged "
        f"{ledger['counts']['primary_panel_challenges']} primary-panel rows; "
        f"recommended {len(ledger['recommended_primary_panel'])} assay rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
