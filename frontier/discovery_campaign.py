"""Build the Phase 1 whole-frontier discovery campaign packet."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier import predicates as P
from frontier.validation_sheet import (
    DATA,
    _best_on_target_stim,
    _candidate_row,
    _load_backbone,
    _load_collectri_counts,
    _load_de_csv,
)

OUT_JSON = DATA / "discovery_campaign.json"
OUT_CSV = DATA / "discovery_candidates.csv"
OUT_DOC = ROOT / "docs" / "DISCOVERY_CAMPAIGN.md"

MIN_STIM_DE = 250
MAX_REST_DE = 350
MAX_REPLOGLE_DE = 25

SOURCE_ARTIFACTS = {
    "frontier_backbone": "examples/data/atlas_backbone.json",
    "replogle_k562": "examples/data/replogle_k562_de.csv",
    "replogle_rpe1": "examples/data/replogle_rpe1_de.csv",
    "collectri": "examples/data/collectri_human.csv",
    "standard_t_cell_annotations": "loop.find_surprises.CANON",
}

FILTER_KEYS = [
    "frontier_genes",
    "condition_specific_regulator",
    "noncanonical_condition_specific",
    "non_artifact_non_activation",
    "on_target_stimulated",
    "strong_stimulated_effect",
    "rest_ceiling",
    "collectri_absent",
    "cell_type_specific_replogle",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for key, rel in SOURCE_ARTIFACTS.items():
        if rel == "loop.find_surprises.CANON":
            basis = "\n".join(sorted(P.CANON)) + "\n"
            hashes[key] = hashlib.sha256(basis.encode()).hexdigest()
        else:
            hashes[key] = _sha256(ROOT / rel)
    return hashes


def _candidate_set_id(rows: list[dict[str, Any]], counts: dict[str, int]) -> str:
    basis = {
        "counts": counts,
        "rows": [
            {
                "rank": row["rank"],
                "gene": row["gene"],
                "score": row["score"],
                "stim_max_de": row["stim_max_de"],
                "rest_de": row["rest_de"],
                "k562_de": row["k562_de"],
                "rpe1_de": row["rpe1_de"],
            }
            for row in rows
        ],
        "source_hashes": _source_hashes(),
    }
    digest = hashlib.sha256(json.dumps(basis, sort_keys=True).encode()).hexdigest()[:16]
    return f"discovery_{digest}"


def _as_candidate(rank: int, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": rank,
        "gene": row["gene"],
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "class": row["class"],
        "score": row["score"],
        "rest_de": row["rest_de"],
        "stim8hr_de": row["stim8hr_de"],
        "stim48hr_de": row["stim48hr_de"],
        "stim_max_de": row["stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "strongest_kd": row["strongest_kd"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "cross_cell_type": row["cross_cell_type"],
        "known_regulon_targets": row["known_regulon_targets"],
        "standard_t_cell_annotation": False,
        "hypothesis": (
            f"{row['gene']} may act as a non-standard regulator of stimulated human CD4+ "
            f"T-cell activation."
        ),
        "evidence_ladder": [
            {
                "rung": "marson_stimulated_effect",
                "status": "computationally_reproduced",
                "detail": f"{row['stim_max_de']} DE genes under {row['strongest_condition']}",
            },
            {
                "rung": "rest_specificity",
                "status": "computationally_reproduced",
                "detail": f"{row['rest_de']} DE genes at Rest",
            },
            {
                "rung": "non_immune_transfer",
                "status": "evidence_attached",
                "detail": f"K562 {row['k562_de']}; RPE1 {row['rpe1_de']}",
            },
            {
                "rung": "novelty_filter",
                "status": "evidence_attached",
                "detail": "absent from CollecTRI and the standard T-cell annotation set",
            },
        ],
        "falsifiable_test": row["validation_assay"],
        "rationale": row["rationale"],
    }


def _refusal_counts(counts: dict[str, int]) -> dict[str, int]:
    return {
        "not_condition_specific": counts["frontier_genes"] - counts["condition_specific_regulator"],
        "standard_t_cell_annotation": (
            counts["condition_specific_regulator"] - counts["noncanonical_condition_specific"]
        ),
        "artifact_or_activation_module": (
            counts["noncanonical_condition_specific"] - counts["non_artifact_non_activation"]
        ),
        "not_on_target_stimulated": counts["non_artifact_non_activation"] - counts["on_target_stimulated"],
        "weak_stimulated_effect": counts["on_target_stimulated"] - counts["strong_stimulated_effect"],
        "rest_above_ceiling": counts["strong_stimulated_effect"] - counts["rest_ceiling"],
        "collectri_present": counts["rest_ceiling"] - counts["collectri_absent"],
        "non_immune_transfer_effect": counts["collectri_absent"] - counts["cell_type_specific_replogle"],
    }


def build_discovery_campaign(limit: int = 50) -> dict[str, Any]:
    backbone = _load_backbone()
    k562 = _load_de_csv(DATA / "replogle_k562_de.csv", "k562_de")
    rpe1 = _load_de_csv(DATA / "replogle_rpe1_de.csv", "rpe1_de")
    collectri = _load_collectri_counts()
    counts = {key: 0 for key in FILTER_KEYS}
    counts["frontier_genes"] = len(backbone)
    candidate_basis: list[dict[str, Any]] = []

    for gene, node in backbone.items():
        if node["class"] != "condition_specific_regulator":
            continue
        counts["condition_specific_regulator"] += 1
        if gene in P.CANON:
            continue
        counts["noncanonical_condition_specific"] += 1
        if P.is_essentiality_artifact(node) or P.is_activation_module(node):
            continue
        counts["non_artifact_non_activation"] += 1
        _, stim_max = _best_on_target_stim(node)
        if stim_max == 0:
            continue
        counts["on_target_stimulated"] += 1
        if stim_max < MIN_STIM_DE:
            continue
        counts["strong_stimulated_effect"] += 1
        if P._rest_de(node) > MAX_REST_DE:
            continue
        counts["rest_ceiling"] += 1
        if collectri.get(gene, 0) != 0:
            continue
        counts["collectri_absent"] += 1
        if k562.get(gene, 0) > MAX_REPLOGLE_DE or rpe1.get(gene, 0) > MAX_REPLOGLE_DE:
            continue
        counts["cell_type_specific_replogle"] += 1
        candidate_basis.append(_candidate_row(gene, node, k562, rpe1, collectri))

    candidate_basis.sort(key=lambda r: (-r["score"], -r["stim_max_de"], r["gene"]))
    candidates = [_as_candidate(i, row) for i, row in enumerate(candidate_basis[:limit], 1)]
    packet = {
        "phase": "phase_1_novelty_at_scale",
        "title": "Phase 1 discovery campaign",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted": False,
        "claim": (
            "Hypothesis set: non-standard genes may regulate human CD4+ T-cell activation "
            "when they show a strong stimulated Marson effect, little non-immune transfer, "
            "and no CollecTRI or standard T-cell regulator annotation."
        ),
        "honest_ceiling": "computation over released data, not wet-lab or clinical truth",
        "method": {
            "min_stim_de": MIN_STIM_DE,
            "max_rest_de": MAX_REST_DE,
            "max_replogle_de": MAX_REPLOGLE_DE,
            "ranking": "score = stimulated DE minus Rest DE plus novelty and transfer bonuses",
            "filters": [
                "condition-specific regulator in the frozen Marson frontier",
                "absent from the standard T-cell annotation set",
                "not an essentiality artifact or activation-module gene",
                "on-target knockdown under stimulation",
                "stimulated DE at or above threshold",
                "Rest DE at or below ceiling",
                "zero CollecTRI targets",
                "no broad K562 or RPE1 transfer effect where measured",
            ],
        },
        "source_artifacts": SOURCE_ARTIFACTS,
        "source_artifact_hashes": _source_hashes(),
        "filter_counts": counts,
        "refusal_counts": _refusal_counts(counts),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "reproduce_command": "./prospect discovery-campaign",
        "next_phase": "freeze and attach independent public T-cell, protein-interaction, expression, and disease-genetics evidence",
    }
    packet["candidate_set_id"] = _candidate_set_id(candidates, counts)
    return packet


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "trust_boundary", "score", "stim_max_de", "strongest_condition",
        "rest_de", "k562_de", "rpe1_de", "known_regulon_targets", "standard_t_cell_annotation",
        "hypothesis", "falsifiable_test",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["filter_counts"]
    refusals = packet["refusal_counts"]
    lines = [
        "# Phase 1 discovery campaign",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No model output enters accepted state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "Prospect scored 11,526 frozen frontier genes for a novel activation-regulator hypothesis set. The filter keeps genes with a strong stimulated CD4+ effect, low Rest effect, no broad K562 or RPE1 transfer where measured, zero CollecTRI targets, and no standard T-cell regulator annotation.",
        "",
        "## Filter counts",
        "",
        "| rung | survivors | refused at rung |",
        "|---|---:|---:|",
        f"| frontier genes | {counts['frontier_genes']:,} |  |",
        f"| condition-specific regulator | {counts['condition_specific_regulator']:,} | {refusals['not_condition_specific']:,} |",
        f"| non-standard T-cell annotation | {counts['noncanonical_condition_specific']:,} | {refusals['standard_t_cell_annotation']:,} |",
        f"| not artifact or activation module | {counts['non_artifact_non_activation']:,} | {refusals['artifact_or_activation_module']:,} |",
        f"| on-target stimulated knockdown | {counts['on_target_stimulated']:,} | {refusals['not_on_target_stimulated']:,} |",
        f"| strong stimulated effect | {counts['strong_stimulated_effect']:,} | {refusals['weak_stimulated_effect']:,} |",
        f"| Rest ceiling | {counts['rest_ceiling']:,} | {refusals['rest_above_ceiling']:,} |",
        f"| CollecTRI absent | {counts['collectri_absent']:,} | {refusals['collectri_present']:,} |",
        f"| Replogle specificity | {counts['cell_type_specific_replogle']:,} | {refusals['non_immune_transfer_effect']:,} |",
        "",
        "## Ranked survivors",
        "",
        "| rank | gene | stim max DE | Rest DE | K562 DE | RPE1 DE | score |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in packet["candidates"]:
        k562 = "" if row["k562_de"] is None else str(row["k562_de"])
        rpe1 = "" if row["rpe1_de"] is None else str(row["rpe1_de"])
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['stim_max_de']} | {row['rest_de']} | "
            f"{k562} | {rpe1} | {row['score']} |"
        )
    lines += [
        "",
        "## Current lead",
        "",
        "PGGT1B is the Phase 1 lead because it has the largest stimulated footprint among the survivor set and remains proposal-only until independent evidence is attached.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect discovery-campaign",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_discovery_campaign(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
    limit: int = 50,
) -> dict[str, Any]:
    packet = build_discovery_campaign(limit=limit)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    _write_csv(packet["candidates"], out_csv)
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_discovery_campaign()
    print(f"wrote {OUT_JSON} ({packet['candidate_count']} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
