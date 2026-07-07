"""Build a wet-lab validation shortlist from frozen Prospect evidence.

The output is a ranked sheet of hypotheses to test. It does not create accepted
state and it does not claim established biology. Every numeric field comes from
the frozen released tables already used by the verifier.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier import predicates as P

DATA = ROOT / "examples" / "data"
OUT_CSV = DATA / "validation_candidates.csv"
OUT_DOC = ROOT / "docs" / "WETLAB_VALIDATION.md"


def _load_backbone() -> dict[str, dict[str, Any]]:
    path = DATA / "atlas_backbone.json"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen backbone: {path}")
    return {n["gene"]: n for n in json.loads(path.read_text())}


def _load_de_csv(path: Path, field: str) -> dict[str, int]:
    if not path.exists():
        return {}
    with path.open() as fh:
        return {r["gene"]: int(r[field]) for r in csv.DictReader(fh)}


def _load_collectri_counts() -> dict[str, int]:
    path = DATA / "collectri_human.csv"
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    with path.open() as fh:
        for r in csv.DictReader(fh):
            counts[r["tf"]] = counts.get(r["tf"], 0) + 1
    return counts


def _cond_de(node: dict[str, Any], cond: str) -> int:
    return int(node["conditions"].get(cond, {}).get("n_de", 0))


def _cond_kd(node: dict[str, Any], cond: str) -> str:
    return str(node["conditions"].get(cond, {}).get("kd", ""))


def _best_on_target_stim(node: dict[str, Any]) -> tuple[str | None, int]:
    candidates = [
        (cond, _cond_de(node, cond))
        for cond in ("Stim8hr", "Stim48hr")
        if _cond_kd(node, cond) == "on-target KD"
    ]
    if not candidates:
        return None, 0
    return max(candidates, key=lambda x: x[1])


def _candidate_row(gene: str, node: dict[str, Any], k562: dict[str, int], rpe1: dict[str, int],
                   collectri: dict[str, int]) -> dict[str, Any]:
    rest = _cond_de(node, "Rest")
    stim8 = _cond_de(node, "Stim8hr")
    stim48 = _cond_de(node, "Stim48hr")
    strongest, stim_max = _best_on_target_stim(node)
    k562_de = k562.get(gene)
    rpe1_de = rpe1.get(gene)
    known = collectri.get(gene, 0)
    specificity = "cell-type-specific"
    if (k562_de is not None and k562_de > 25) or (rpe1_de is not None and rpe1_de > 25):
        specificity = "housekeeping-like"
    no_regulon_bonus = 300 if known == 0 else max(0, 120 - known)
    transfer_bonus = 250 if specificity == "cell-type-specific" else -500
    score = stim_max - rest + no_regulon_bonus + transfer_bonus
    return {
        "gene": gene,
        "status": "evidence_attached",
        "replayability": "attested",
        "class": node["class"],
        "rest_de": rest,
        "stim8hr_de": stim8,
        "stim48hr_de": stim48,
        "stim_max_de": stim_max,
        "strongest_condition": strongest or "",
        "strongest_kd": _cond_kd(node, strongest or ""),
        "k562_de": k562_de,
        "rpe1_de": rpe1_de,
        "cross_cell_type": specificity,
        "known_regulon_targets": known,
        "score": score,
        "rationale": (
            f"hypothesis to test: {gene} has {stim_max} DE genes under {strongest}, "
            f"{rest} DE at Rest, {k562_de if k562_de is not None else 'not tested'} DE in K562, "
            f"and {known} CollecTRI targets"
        ),
        "validation_assay": (
            "repeat CRISPRi or orthogonal knockdown in stimulated primary CD4+ T cells; "
            "measure activation markers and targeted RNA-seq at 8h and 48h"
        ),
    }


def rank_candidates(limit: int = 25, min_stim_de: int = 500, max_rest_de: int = 250) -> list[dict[str, Any]]:
    bb = _load_backbone()
    k562 = _load_de_csv(DATA / "replogle_k562_de.csv", "k562_de")
    rpe1 = _load_de_csv(DATA / "replogle_rpe1_de.csv", "rpe1_de")
    collectri = _load_collectri_counts()
    rows: list[dict[str, Any]] = []

    for gene, node in bb.items():
        _, stim_max = _best_on_target_stim(node)
        if gene in P.CANON:
            continue
        if node["class"] != "condition_specific_regulator":
            continue
        if P.is_essentiality_artifact(node) or P.is_activation_module(node):
            continue
        if stim_max < min_stim_de or P._rest_de(node) > max_rest_de:
            continue
        if k562.get(gene, 0) > 25 or rpe1.get(gene, 0) > 25:
            continue
        rows.append(_candidate_row(gene, node, k562, rpe1, collectri))

    rows.sort(key=lambda r: (-r["score"], -r["stim_max_de"], r["gene"]))
    return rows[:limit]


def write_sheet(limit: int = 25) -> list[dict[str, Any]]:
    rows = rank_candidates(limit=limit)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "gene", "status", "replayability", "class", "rest_de", "stim8hr_de", "stim48hr_de",
        "stim_max_de", "strongest_condition", "strongest_kd", "k562_de", "rpe1_de",
        "cross_cell_type", "known_regulon_targets", "score", "rationale", "validation_assay",
    ]
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    write_markdown(rows)
    return rows


def write_markdown(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Wet-lab validation shortlist",
        "",
        "These are hypotheses to test, derived from frozen Prospect lookups. The status is `evidence_attached`, not an established biological result.",
        "",
        "| rank | gene | stim max DE | Rest DE | K562 DE | CollecTRI targets | assay note |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for i, r in enumerate(rows[:15], 1):
        k562 = "" if r["k562_de"] is None else str(r["k562_de"])
        lines.append(
            f"| {i} | {r['gene']} | {r['stim_max_de']} | {r['rest_de']} | {k562} | "
            f"{r['known_regulon_targets']} | stimulated CD4+ perturbation follow-up |"
        )
    lines += [
        "",
        "Selection filters: non-canonical T-cell gene, condition-specific regulator, not an activation-module gene, not an essentiality artifact, Rest DE at or below 250, stimulated DE at or above 500, and no major effect in non-immune Replogle cells where measured.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/validation_sheet.py",
        "```",
    ]
    OUT_DOC.write_text("\n".join(lines) + "\n")


def main() -> None:
    rows = write_sheet()
    print(f"wrote {OUT_CSV} ({len(rows)} candidates)")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
