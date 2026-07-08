"""Build a cross-substrate discovery packet over committed count tables."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "cross_substrate_discovery.json"
OUT_DOC = ROOT / "docs" / "CROSS_SUBSTRATE_DISCOVERY.md"
SIG = ROOT / "frontier" / "frontier.sig.json"

ATLAS = DATA / "atlas_backbone.json"
K562 = DATA / "replogle_k562_de.csv"
RPE1 = DATA / "replogle_rpe1_de.csv"
CAMPAIGN = DATA / "agent_campaign.json"

THRESHOLDS = {
    "rest_high_de": 1000,
    "rest_tolerated_de_for_t_cell_candidate": 250,
    "stim_strong_de": 100,
    "marson_low_de_for_non_immune_only": 10,
    "non_immune_major_de": 25,
    "non_immune_low_de": 25,
}

CLASS_ORDER = {
    "shared_cellular_machinery": 0,
    "t_cell_specific_activation": 1,
    "non_immune_only_effect": 2,
    "ambiguous_or_not_tested": 3,
}

PUBLIC_CLASS = {
    "verified_non_regulator": "reproduced_non_regulator",
}


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def _load_atlas() -> list[dict[str, Any]]:
    return json.loads(ATLAS.read_text())


def _load_counts(path: Path, field: str) -> dict[str, int]:
    rows: dict[str, int] = {}
    with path.open() as fh:
        for row in csv.DictReader(fh):
            rows[row["gene"]] = int(row[field])
    return rows


def _load_campaign() -> dict[str, dict[str, Any]]:
    if not CAMPAIGN.exists():
        return {}
    campaign = json.loads(CAMPAIGN.read_text())
    return {row["gene"]: row for row in campaign.get("candidates", [])}


def _public_class(value: str) -> str:
    return PUBLIC_CLASS.get(value, value)


def _condition_de(record: dict[str, Any], condition: str) -> int:
    return int(record["conditions"].get(condition, {}).get("n_de", 0))


def _has_on_target(record: dict[str, Any], condition: str) -> bool:
    return record["conditions"].get(condition, {}).get("kd") == "on-target KD"


def _stim_values(record: dict[str, Any]) -> list[tuple[str, int]]:
    values = []
    for condition in ("Stim8hr", "Stim48hr"):
        if _has_on_target(record, condition):
            values.append((condition, _condition_de(record, condition)))
    return values


def _classify(
    rest_de: int,
    stim_max_de: int,
    marson_on_target_max_de: int,
    has_marson_on_target: bool,
    k562_de: int | None,
    rpe1_de: int | None,
) -> str:
    non_immune_values = [value for value in (k562_de, rpe1_de) if value is not None]
    non_immune_max = max(non_immune_values or [0])
    non_immune_low = bool(non_immune_values) and all(
        value <= THRESHOLDS["non_immune_low_de"] for value in non_immune_values
    )

    if rest_de > THRESHOLDS["rest_high_de"] and non_immune_max > THRESHOLDS["non_immune_major_de"]:
        return "shared_cellular_machinery"
    if (
        stim_max_de > THRESHOLDS["stim_strong_de"]
        and rest_de <= THRESHOLDS["rest_tolerated_de_for_t_cell_candidate"]
        and non_immune_low
    ):
        return "t_cell_specific_activation"
    if (
        has_marson_on_target
        and marson_on_target_max_de < THRESHOLDS["marson_low_de_for_non_immune_only"]
        and non_immune_max > THRESHOLDS["non_immune_major_de"]
    ):
        return "non_immune_only_effect"
    return "ambiguous_or_not_tested"


def _row(record: dict[str, Any], k562: dict[str, int], rpe1: dict[str, int], campaign: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gene = record["gene"]
    stim_values = _stim_values(record)
    stim_condition, stim_max_de = max(stim_values, key=lambda item: item[1]) if stim_values else ("not_on_target", 0)
    on_target_values = [
        _condition_de(record, condition)
        for condition in ("Rest", "Stim8hr", "Stim48hr")
        if _has_on_target(record, condition)
    ]
    rest_de = _condition_de(record, "Rest")
    k562_de = k562.get(gene)
    rpe1_de = rpe1.get(gene)
    non_immune_values = [value for value in (k562_de, rpe1_de) if value is not None]
    cls = _classify(
        rest_de=rest_de,
        stim_max_de=stim_max_de,
        marson_on_target_max_de=max(on_target_values or [0]),
        has_marson_on_target=bool(on_target_values),
        k562_de=k562_de,
        rpe1_de=rpe1_de,
    )
    campaign_row = campaign.get(gene)
    return {
        "gene": gene,
        "cross_substrate_class": cls,
        "prospect_class": _public_class(record["class"]),
        "rest_de": rest_de,
        "stim8hr_de": _condition_de(record, "Stim8hr"),
        "stim48hr_de": _condition_de(record, "Stim48hr"),
        "stim_max_de": stim_max_de,
        "strongest_stim_condition": stim_condition,
        "marson_on_target_conditions": [
            condition for condition in ("Rest", "Stim8hr", "Stim48hr") if _has_on_target(record, condition)
        ],
        "k562_de": k562_de,
        "rpe1_de": rpe1_de,
        "non_immune_max_de": max(non_immune_values or [0]),
        "campaign_rank": campaign_row.get("rank") if campaign_row else None,
        "campaign_status": campaign_row.get("status") if campaign_row else None,
    }


def _rank_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        CLASS_ORDER[row["cross_substrate_class"]],
        -int(row["non_immune_max_de"]),
        -int(row["stim_max_de"]),
        row["gene"],
    )


def _campaign_key(row: dict[str, Any]) -> tuple[int, str]:
    rank = row["campaign_rank"]
    return (int(rank) if rank is not None else 9999, row["gene"])


def build_packet() -> dict[str, Any]:
    atlas = _load_atlas()
    k562 = _load_counts(K562, "k562_de")
    rpe1 = _load_counts(RPE1, "rpe1_de")
    campaign = _load_campaign()
    rows = [_row(record, k562, rpe1, campaign) for record in atlas]
    by_gene = {row["gene"]: row for row in rows}
    class_counts = Counter(row["cross_substrate_class"] for row in rows)
    campaign_intersections = sorted(
        [row for row in rows if row["campaign_rank"] is not None],
        key=_campaign_key,
    )
    exemplar_genes = ["MED19", "TADA2B", "BCL10", "PGGT1B", "RAC3", "LAT"]

    return {
        "title": "Cross-substrate discovery packet",
        "status": "computationally_reproduced",
        "trust_boundary": "frozen_counts_over_committed_tables",
        "accepted_state_mutation": "none",
        "signed_frontier_root": _frontier_root(),
        "source_tables": [
            {"path": "examples/data/atlas_backbone.json", "role": "primary_human_cd4_t_cell_counts"},
            {"path": "examples/data/replogle_k562_de.csv", "role": "k562_non_immune_counts"},
            {"path": "examples/data/replogle_rpe1_de.csv", "role": "rpe1_non_immune_counts"},
            {"path": "examples/data/agent_campaign.json", "role": "proposal_only_campaign_ranks"},
        ],
        "method": {
            "model_in_trust_path": "no",
            "accepted_state_mutation": "none",
            "replay_command": "./prospect cross-substrate-discovery",
            "classifier": "fixed_threshold_counts",
            "ranking": "class_priority_then_non_immune_de_then_stim_de",
        },
        "thresholds": THRESHOLDS,
        "classes": [
            {
                "class": "shared_cellular_machinery",
                "rule": "Rest Marson DE above 1000 and any non-immune DE above 25.",
                "use": "Flag broad cellular machinery before treating a T-cell effect as specific.",
            },
            {
                "class": "t_cell_specific_activation",
                "rule": "On-target stimulated Marson DE above 100, Rest DE at or below 250, and measured non-immune DE at or below 25.",
                "use": "Prioritize activation-biased CD4+ hypotheses for proposal-only assay follow-up.",
            },
            {
                "class": "non_immune_only_effect",
                "rule": "At least one on-target Marson condition, Marson on-target DE below 10, and any non-immune DE above 25.",
                "use": "Find cross-dataset disagreements that should not be promoted as CD4+ regulators.",
            },
            {
                "class": "ambiguous_or_not_tested",
                "rule": "Rows with missing comparison data, missing effective Marson knockdown, or mixed evidence.",
                "use": "Keep uncertain rows outside stronger classes.",
            },
        ],
        "counts": {
            "marson_genes_considered": len(atlas),
            "overlap_k562": sum(1 for row in rows if row["k562_de"] is not None),
            "overlap_rpe1": sum(1 for row in rows if row["rpe1_de"] is not None),
            "overlap_any_non_immune": sum(1 for row in rows if row["k562_de"] is not None or row["rpe1_de"] is not None),
            "campaign_rows_intersected": len(campaign_intersections),
        },
        "class_counts": {name: class_counts.get(name, 0) for name in CLASS_ORDER},
        "exemplar_rows": [by_gene[gene] for gene in exemplar_genes],
        "top_rows": sorted(rows, key=_rank_key)[:40],
        "campaign_intersections": campaign_intersections,
        "limitations": (
            "This packet proves computation over released frozen tables. It does not prove wet-lab "
            "result, clinical result, or accepted biological state."
        ),
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    class_counts = packet["class_counts"]
    lines = [
        "# Cross-substrate discovery packet",
        "",
        "Status: `computationally_reproduced`.",
        "",
        "No accepted state changes. This packet classifies frozen Marson and Replogle count rows into reproducible cross-substrate discovery lanes.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["method"]["replay_command"],
        "```",
        "",
        "## Counts",
        "",
        f"- Marson genes considered: {counts['marson_genes_considered']}",
        f"- K562 overlap: {counts['overlap_k562']}",
        f"- RPE1 overlap: {counts['overlap_rpe1']}",
        f"- Any non-immune overlap: {counts['overlap_any_non_immune']}",
        f"- Campaign rows intersected: {counts['campaign_rows_intersected']}",
        "",
        "## Class Counts",
        "",
    ]
    lines += [f"- `{name}`: {value}" for name, value in class_counts.items()]
    lines += [
        "",
        "## Exemplars",
        "",
        "| Gene | Class | Rest DE | Stim max DE | K562 DE | RPE1 DE | Campaign rank |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in packet["exemplar_rows"]:
        k562 = "not measured" if row["k562_de"] is None else str(row["k562_de"])
        rpe1 = "not measured" if row["rpe1_de"] is None else str(row["rpe1_de"])
        rank = "" if row["campaign_rank"] is None else str(row["campaign_rank"])
        lines.append(
            f"| {row['gene']} | {row['cross_substrate_class']} | {row['rest_de']} | "
            f"{row['stim_max_de']} | {k562} | {rpe1} | {rank} |"
        )
    lines += [
        "",
        "## Campaign Intersections",
        "",
        "| Rank | Gene | Class | Rest DE | Stim max DE | K562 DE | RPE1 DE |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in packet["campaign_intersections"][:10]:
        k562 = "not measured" if row["k562_de"] is None else str(row["k562_de"])
        rpe1 = "not measured" if row["rpe1_de"] is None else str(row["rpe1_de"])
        lines.append(
            f"| {row['campaign_rank']} | {row['gene']} | {row['cross_substrate_class']} | "
            f"{row['rest_de']} | {row['stim_max_de']} | {k562} | {rpe1} |"
        )
    lines += [
        "",
        packet["limitations"],
    ]
    return "\n".join(lines) + "\n"


def write_packet(out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC) -> dict[str, Any]:
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_packet()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"classified {packet['counts']['marson_genes_considered']} Marson genes across substrates")


if __name__ == "__main__":
    main()
