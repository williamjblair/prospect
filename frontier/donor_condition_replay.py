"""Build a donor-condition replay packet for the proposal-only campaign rows."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.graph_edges import S3PATH, open_matrix, read_col

DATA = ROOT / "examples" / "data"
OUT_SOURCE = DATA / "donor_condition_source_rows.json"
OUT_JSON = DATA / "donor_condition_replay.json"
OUT_DOC = ROOT / "docs" / "DONOR_CONDITION_REPLAY.md"
SIG = ROOT / "frontier" / "frontier.sig.json"
CAMPAIGN = DATA / "agent_campaign.json"

THRESHOLDS = {
    "actionable_de_genes": 50,
    "donor_supported_hits_min": 0.5,
    "donor_supported_hits_mean": 0.6,
    "donor_fragile_hits_min_lt": 0.35,
    "min_guides_for_full_support": 2,
}

CLASS_ORDER = [
    "donor_supported",
    "donor_intermediate",
    "donor_fragile",
    "guide_limited",
    "donor_not_estimated",
    "aggregate_not_actionable",
]


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def _load_campaign() -> list[dict[str, Any]]:
    return json.loads(CAMPAIGN.read_text())["candidates"]


def _clean_number(value: Any, digits: int | None = None) -> Any:
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (float, np.floating)):
        return round(float(value), digits) if digits is not None else float(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


def _yes_no(value: Any) -> str:
    if hasattr(value, "item"):
        value = value.item()
    return "yes" if bool(value) else "no"


def extract_source_rows() -> dict[str, Any]:
    """Extract only campaign strongest-condition rows from the released DE h5ad."""
    campaign = _load_campaign()
    h = open_matrix()
    obs = h["obs"]
    src = read_col(obs, "target_contrast_gene_name")
    condition = read_col(obs, "culture_condition")
    index = {(str(src[i]), str(condition[i])): i for i in range(len(src))}

    text_cols = ["n_total_genes_category", "single_guide_estimate"]
    number_cols = [
        "n_total_de_genes",
        "n_up_genes",
        "n_down_genes",
        "ontarget_effect_size",
        "ontarget_significant",
        "donor_correlation_all_mean",
        "donor_correlation_all_min",
        "donor_correlation_hits_mean",
        "donor_correlation_hits_min",
        "n_guides",
        "guide_n_signif_ontarget",
        "n_cells_target",
    ]
    text = {name: read_col(obs, name) for name in text_cols}
    number = {name: np.asarray(obs[name][:]) for name in number_cols}
    rows = []
    for candidate in campaign:
        gene = candidate["gene"]
        strongest = candidate["strongest_condition"]
        row_index = index.get((gene, strongest))
        if row_index is None:
            raise KeyError(f"missing released DE row for {gene} {strongest}")
        rows.append(
            {
                "rank": int(candidate["rank"]),
                "gene": gene,
                "condition": strongest,
                "campaign_status": candidate["status"],
                "campaign_score": int(candidate["score"]),
                "n_total_de_genes": int(_clean_number(number["n_total_de_genes"][row_index])),
                "n_up_genes": int(_clean_number(number["n_up_genes"][row_index])),
                "n_down_genes": int(_clean_number(number["n_down_genes"][row_index])),
                "n_total_genes_category": str(text["n_total_genes_category"][row_index]),
                "ontarget_effect_size": _clean_number(number["ontarget_effect_size"][row_index], 4),
                "ontarget_significant": _yes_no(number["ontarget_significant"][row_index]),
                "donor_correlation_all_mean": _clean_number(number["donor_correlation_all_mean"][row_index], 4),
                "donor_correlation_all_min": _clean_number(number["donor_correlation_all_min"][row_index], 4),
                "donor_correlation_hits_mean": _clean_number(number["donor_correlation_hits_mean"][row_index], 4),
                "donor_correlation_hits_min": _clean_number(number["donor_correlation_hits_min"][row_index], 4),
                "n_guides": int(_clean_number(number["n_guides"][row_index]) or 0),
                "guide_n_signif_ontarget": _clean_number(number["guide_n_signif_ontarget"][row_index]),
                "single_guide_estimate": _yes_no(text["single_guide_estimate"][row_index]),
                "n_cells_target": int(_clean_number(number["n_cells_target"][row_index]) or 0),
            }
        )
    return {
        "title": "Donor-condition replay source rows",
        "status": "computationally_reproduced",
        "source": f"s3://{S3PATH}",
        "source_object": "GWCD4i.DE_stats.h5ad",
        "source_rows": "campaign strongest-condition perturbation rows",
        "regeneration_command": "./prospect donor-replay --refresh-source",
        "rows": rows,
    }


def _load_source_rows(refresh_source: bool = False) -> dict[str, Any]:
    if refresh_source or not OUT_SOURCE.exists():
        source = extract_source_rows()
        OUT_SOURCE.write_text(json.dumps(source, indent=2) + "\n")
        return source
    return json.loads(OUT_SOURCE.read_text())


def _classify(row: dict[str, Any]) -> str:
    hits_min = row["donor_correlation_hits_min"]
    hits_mean = row["donor_correlation_hits_mean"]
    if hits_min is None or hits_mean is None:
        return "donor_not_estimated"
    if row["n_total_de_genes"] < THRESHOLDS["actionable_de_genes"] or row["ontarget_significant"] != "yes":
        return "aggregate_not_actionable"
    if row["single_guide_estimate"] == "yes" or row["n_guides"] < THRESHOLDS["min_guides_for_full_support"]:
        return "guide_limited"
    if hits_min >= THRESHOLDS["donor_supported_hits_min"] and hits_mean >= THRESHOLDS["donor_supported_hits_mean"]:
        return "donor_supported"
    if hits_min < THRESHOLDS["donor_fragile_hits_min_lt"]:
        return "donor_fragile"
    return "donor_intermediate"


def _with_class(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["donor_replay_class"] = _classify(row)
    return out


def build_packet(refresh_source: bool = False) -> dict[str, Any]:
    source = _load_source_rows(refresh_source=refresh_source)
    rows = [_with_class(row) for row in source["rows"]]
    counts = Counter(row["donor_replay_class"] for row in rows)
    count_block = {
        "campaign_rows": len(rows),
        "strongest_condition_rows": len(rows),
    }
    count_block.update({name: counts.get(name, 0) for name in CLASS_ORDER})
    promotion = [row for row in rows if row["donor_replay_class"] == "donor_supported"]
    warnings = [
        row for row in rows
        if row["donor_replay_class"] in {"donor_fragile", "guide_limited", "donor_intermediate"}
    ]

    return {
        "title": "Donor-condition replay packet",
        "status": "computationally_reproduced",
        "trust_boundary": "frozen_donor_rows_extracted_from_released_h5ad",
        "accepted_state_mutation": "none",
        "signed_frontier_root": _frontier_root(),
        "source": {
            "released_object": source["source"],
            "source_object": source["source_object"],
            "source_rows": source["source_rows"],
            "committed_extract": "examples/data/donor_condition_source_rows.json",
            "source_status": source["status"],
        },
        "method": {
            "model_in_trust_path": "no",
            "accepted_state_mutation": "none",
            "replay_command": "./prospect donor-replay",
            "source_regeneration_command": source["regeneration_command"],
            "classification": "fixed_thresholds_over_released_donor_and_guide_fields",
        },
        "thresholds": THRESHOLDS,
        "classes": [
            {
                "class": "donor_supported",
                "meaning": "Strong aggregate row with two-guide support and donor-hit correlation above threshold.",
            },
            {
                "class": "donor_intermediate",
                "meaning": "Strong aggregate row with donor-hit correlation above fragile threshold but below full support.",
            },
            {
                "class": "donor_fragile",
                "meaning": "Strong aggregate row whose donor-hit correlation falls below the fragile threshold.",
            },
            {
                "class": "guide_limited",
                "meaning": "Strong donor-correlated row that depends on a single-guide estimate.",
            },
            {
                "class": "donor_not_estimated",
                "meaning": "Released donor-correlation fields were not estimated for this strongest condition.",
            },
            {
                "class": "aggregate_not_actionable",
                "meaning": "Strongest campaign condition lacks enough aggregate DE or on-target support.",
            },
        ],
        "counts": count_block,
        "rows": rows,
        "promotion_candidates": promotion,
        "capacity_warnings": warnings,
        "limitations": (
            "This packet replays released donor-correlation and guide fields for campaign prioritization. "
            "It does not prove wet-lab result, clinical result, or accepted biological state."
        ),
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    lines = [
        "# Donor-condition replay packet",
        "",
        "Status: `computationally_reproduced`.",
        "",
        "No accepted state changes. This packet classifies campaign strongest-condition rows by released donor-correlation and guide-support fields.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["method"]["replay_command"],
        "```",
        "",
        "Refresh source extract from the released h5ad:",
        "",
        "```bash",
        packet["method"]["source_regeneration_command"],
        "```",
        "",
        "## Counts",
        "",
        f"- Campaign rows: {counts['campaign_rows']}",
        f"- Donor supported: {counts['donor_supported']}",
        f"- Donor intermediate: {counts['donor_intermediate']}",
        f"- Donor fragile: {counts['donor_fragile']}",
        f"- Guide limited: {counts['guide_limited']}",
        f"- Donor not estimated: {counts['donor_not_estimated']}",
        f"- Aggregate not actionable: {counts['aggregate_not_actionable']}",
        "",
        "## Campaign Rows",
        "",
        "| Rank | Gene | Condition | Class | DE genes | donor hits min | donor hits mean | guides |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in packet["rows"]:
        hits_min = "" if row["donor_correlation_hits_min"] is None else str(row["donor_correlation_hits_min"])
        hits_mean = "" if row["donor_correlation_hits_mean"] is None else str(row["donor_correlation_hits_mean"])
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['condition']} | {row['donor_replay_class']} | "
            f"{row['n_total_de_genes']} | {hits_min} | {hits_mean} | {row['n_guides']} |"
        )
    lines += [
        "",
        packet["limitations"],
    ]
    return "\n".join(lines) + "\n"


def write_packet(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
    refresh_source: bool = False,
) -> dict[str, Any]:
    packet = build_packet(refresh_source=refresh_source)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect donor-replay")
    parser.add_argument("--refresh-source", action="store_true", help="refresh the small source extract from released h5ad")
    parser.add_argument("--json", action="store_true", help="print the packet as JSON")
    args = parser.parse_args(argv)

    packet = write_packet(refresh_source=args.refresh_source)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_SOURCE}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"classified {packet['counts']['campaign_rows']} campaign rows by donor replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
