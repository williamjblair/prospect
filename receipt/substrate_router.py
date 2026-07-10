"""Context-aware substrate routing for external Prospect claims."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from receipt.frozen_io import sha256_file

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
MARSON = DATA / "marson_de_full.csv"
K562 = DATA / "replogle_k562_de.csv"
RPE1 = DATA / "replogle_rpe1_de.csv"
ORCS_TCELL = DATA / "orcs_tcell_signature_rows.json"
CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]

SUBSTRATE_LABELS = {
    "marson_cd4_activation": "Marson primary human CD4+ CRISPRi Perturb-seq",
    "replogle_k562": "Replogle K562 Perturb-seq",
    "replogle_rpe1": "Replogle RPE1 Perturb-seq",
    "orcs_primary_tcell": "BioGRID ORCS primary T-cell perturbation rows",
}


def choose_route(*, source_name: str = "", filename: str = "", claim_context: str = "", claim: str = "") -> dict[str, str]:
    text = " ".join([source_name, filename, claim_context, claim]).lower()
    if "k562" in text:
        return {
            "primary_substrate": "replogle_k562",
            "routing_reason": "K562 claim routes first to the Replogle K562 perturbation substrate",
        }
    if "rpe1" in text:
        return {
            "primary_substrate": "replogle_rpe1",
            "routing_reason": "RPE1 claim routes first to the Replogle RPE1 perturbation substrate",
        }
    return {
        "primary_substrate": "marson_cd4_activation",
        "routing_reason": "immunotherapy or T-cell claim routes first to the primary CD4+ perturbation substrate",
    }


@lru_cache(maxsize=1)
def _marson_rows() -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with MARSON.open(newline="") as f:
        for row in csv.DictReader(f):
            rows[(row["target_contrast_gene_name"], row["culture_condition"])] = row
    return rows


@lru_cache(maxsize=2)
def _replogle_rows(substrate: str) -> dict[str, dict[str, str]]:
    path = K562 if substrate == "replogle_k562" else RPE1
    rows: dict[str, dict[str, str]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            rows[row["gene"]] = row
    return rows


@lru_cache(maxsize=1)
def _orcs_rows() -> dict[str, dict[str, Any]]:
    if not ORCS_TCELL.exists():
        return {}
    payload = json.loads(ORCS_TCELL.read_text())
    return {row["gene"]: row for row in payload.get("genes", [])}


def _int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _marson_condition_specificity(gene: str) -> dict[str, dict[str, Any]]:
    rows = _marson_rows()
    out: dict[str, dict[str, Any]] = {}
    for condition in CONDITIONS:
        row = rows.get((gene, condition))
        if not row:
            out[condition] = {"assayed": False}
            continue
        out[condition] = {
            "assayed": True,
            "n_total_de_genes": _int(row["n_total_de_genes"]),
            "n_up_genes": _int(row["n_up_genes"]),
            "n_down_genes": _int(row["n_down_genes"]),
            "ontarget_effect_size": _float(row["ontarget_effect_size"]),
            "ontarget_effect_category": row["ontarget_effect_category"],
        }
    return out


def _best_orcs_primary_row(gene: str) -> dict[str, Any] | None:
    payload = _orcs_rows().get(gene)
    if not payload:
        return None
    primary_rows = [
        row
        for row in payload.get("rows", [])
        if "primary" in str(row.get("cell_line", "")).lower() or "primary" in str(row.get("details", "")).lower()
    ]
    if not primary_rows:
        return None
    return sorted(
        primary_rows,
        key=lambda row: (
            0 if row.get("hit_status") == "hit" else 1,
            row.get("rank") if row.get("rank") is not None else 10**9,
        ),
    )[0]


def _orcs_evidence(gene: str) -> dict[str, Any]:
    payload = _orcs_rows().get(gene)
    best = _best_orcs_primary_row(gene)
    if not payload:
        return {"coverage_status": "not_assayed", "reason": "no frozen ORCS T-cell row for this gene"}
    if not best:
        return {
            "coverage_status": "not_assayed",
            "gene_id": payload.get("gene_id"),
            "reason": "frozen ORCS rows exist, but none are primary T-cell rows",
        }
    return {
        "coverage_status": "covered_orthogonal_tcell",
        "gene_id": payload.get("gene_id"),
        "records_filtered": payload.get("records_filtered"),
        "best_row": best,
        "reason": "primary T-cell perturbation coverage exists, but the readout is treated as orthogonal context unless the claim is about that phenotype",
    }


def _replogle_evidence(gene: str, substrate: str) -> dict[str, Any]:
    rows = _replogle_rows(substrate)
    row = rows.get(gene)
    key = "k562_de" if substrate == "replogle_k562" else "rpe1_de"
    if not row:
        return {"coverage_status": "not_assayed", "reason": f"{gene} is absent from {substrate}"}
    n_de = _int(row[key]) or 0
    return {
        "coverage_status": "covered",
        "n_total_de_genes": n_de,
        "magnitude": n_de,
        "is_control": row.get("is_control") == "True",
    }


def replogle_verdicts(genes: list[dict[str, Any]], substrate: str) -> list[dict[str, Any]]:
    rows = _replogle_rows(substrate)
    key = "k562_de" if substrate == "replogle_k562" else "rpe1_de"
    verdicts: list[dict[str, Any]] = []
    for item in genes:
        gene = str(item.get("gene") if isinstance(item, dict) else item)
        row = rows.get(gene)
        if not row:
            typed_status = "not_assayed"
            n_de = None
            reason = f"{gene} is absent from the frozen {substrate} table."
        else:
            n_de = _int(row[key]) or 0
            if n_de > 25:
                typed_status = "evidence_attached"
                reason = f"{gene} moves {n_de} transcripts in {substrate}, so Prospect types it as a candidate driver in that substrate."
            else:
                typed_status = "associative_only"
                reason = f"{gene} is covered in {substrate}, but moves only {n_de} transcripts."
        verdicts.append({
            "gene": gene,
            "signature_roles": list(item.get("roles", [])) if isinstance(item, dict) else [],
            "typed_status": typed_status,
            "driver_claim": "",
            "condition": substrate,
            "n_total_de_genes": n_de,
            "ontarget_effect_category": "covered" if row else "not_found",
            "de_rank": None,
            "signature_diff_R_minus_NR": None,
            "signature_padj": None,
            "reason": reason,
        })
    return sorted(
        verdicts,
        key=lambda v: (
            {"evidence_attached": 0, "contradicted": 1, "associative_only": 2, "not_assayed": 3}.get(v["typed_status"], 9),
            -(v["n_total_de_genes"] or 0),
            v["gene"],
        ),
    )


def enrich_verdicts(verdicts: list[dict[str, Any]], *, primary_substrate: str) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for verdict in verdicts:
        gene = verdict["gene"]
        conditions = _marson_condition_specificity(gene)
        strongest_condition = verdict.get("condition") or ""
        if primary_substrate == "marson_cd4_activation" and strongest_condition in conditions:
            strongest = conditions[strongest_condition]
            n_up = strongest.get("n_up_genes")
            n_down = strongest.get("n_down_genes")
            effect_size = strongest.get("ontarget_effect_size")
        else:
            n_up = None
            n_down = None
            effect_size = None
        magnitude = {
            "n_total_de_genes": verdict.get("n_total_de_genes"),
            "n_up_genes": n_up,
            "n_down_genes": n_down,
            "effect_size": effect_size,
        }
        enriched.append({
            **verdict,
            "primary_substrate": primary_substrate,
            "direction": {
                "strongest_condition": strongest_condition,
                "n_up_genes": n_up,
                "n_down_genes": n_down,
            },
            "magnitude": magnitude,
            "condition_specificity": conditions,
            "substrate_evidence": {
                "marson_cd4_activation": {
                    "coverage_status": "covered" if any(row.get("assayed") for row in conditions.values()) else "not_assayed",
                    "conditions": conditions,
                },
                "replogle_k562": _replogle_evidence(gene, "replogle_k562"),
                "replogle_rpe1": _replogle_evidence(gene, "replogle_rpe1"),
                "orcs_primary_tcell": _orcs_evidence(gene),
            },
        })
    return enriched


def coverage_report(verdicts: list[dict[str, Any]], route: dict[str, str]) -> dict[str, Any]:
    not_assayed = [row["gene"] for row in verdicts if row["typed_status"] == "not_assayed"]
    orcs_covered = [gene for gene in not_assayed if _orcs_evidence(gene)["coverage_status"] == "covered_orthogonal_tcell"]
    k562_covered = [gene for gene in not_assayed if _replogle_evidence(gene, "replogle_k562")["coverage_status"] == "covered"]
    rpe1_covered = [gene for gene in not_assayed if _replogle_evidence(gene, "replogle_rpe1")["coverage_status"] == "covered"]
    after_not_assayed = sorted(set(not_assayed) - set(orcs_covered))
    counts = Counter(row["typed_status"] for row in verdicts)
    return {
        "primary_substrate": route["primary_substrate"],
        "routing_reason": route["routing_reason"],
        "before": {
            "genes": len(verdicts),
            "not_assayed": len(not_assayed),
            "not_assayed_fraction": round(len(not_assayed) / len(verdicts), 4) if verdicts else 0,
            "typed_status_counts": dict(counts),
        },
        "after": {
            "genes": len(verdicts),
            "not_assayed": len(after_not_assayed),
            "not_assayed_fraction": round(len(after_not_assayed) / len(verdicts), 4) if verdicts else 0,
            "basis": "primary T-cell ORCS rows shrink uncovered genes, but remain orthogonal context unless readouts are comparable",
            "remaining_genes": after_not_assayed,
        },
        "substrates": {
            "marson_cd4_activation": {
                "source_sha256": sha256_file(MARSON),
                "covered_genes": len(verdicts) - len(not_assayed),
                "not_assayed_genes": len(not_assayed),
            },
            "orcs_primary_tcell": {
                "source_sha256": sha256_file(ORCS_TCELL) if ORCS_TCELL.exists() else "",
                "covered_genes": len(orcs_covered),
                "covered_not_assayed_genes": sorted(orcs_covered),
            },
            "replogle_k562": {
                "source_sha256": sha256_file(K562),
                "covered_not_assayed_genes": sorted(k562_covered),
                "covered_genes": len([row for row in verdicts if _replogle_evidence(row["gene"], "replogle_k562")["coverage_status"] == "covered"]),
            },
            "replogle_rpe1": {
                "source_sha256": sha256_file(RPE1),
                "covered_not_assayed_genes": sorted(rpe1_covered),
                "covered_genes": len([row for row in verdicts if _replogle_evidence(row["gene"], "replogle_rpe1")["coverage_status"] == "covered"]),
            },
        },
    }


def artifact_hashes() -> dict[str, dict[str, str]]:
    artifacts = {
        "marson_cd4_activation": MARSON,
        "replogle_k562": K562,
        "replogle_rpe1": RPE1,
        "orcs_primary_tcell": ORCS_TCELL,
    }
    return {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path) if path.exists() else ""}
        for name, path in artifacts.items()
    }


def clear_caches() -> None:
    _marson_rows.cache_clear()
    _replogle_rows.cache_clear()
    _orcs_rows.cache_clear()
