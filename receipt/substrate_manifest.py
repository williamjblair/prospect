"""Canonical manifests and per-dataset evidence for frozen Prospect substrates."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from receipt.substrate_router import (
    CONDITIONS,
    K562,
    MARSON,
    ORCS_TCELL,
    RPE1,
    _marson_condition_specificity,
    _orcs_evidence,
    _replogle_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
GSE278572_MANIFEST = DATA / "gse278572" / "source_manifest.json"
GSE278572_RESULT = DATA / "gse278572_comparator.json"
GSE271788_MANIFEST = DATA / "gse271788" / "source_manifest.json"
GSE271788_REACH = DATA / "gse271788" / "target_reach.csv"
EVIDENCE_MODES = {"primary_only", "all_frozen"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class SubstrateManifest:
    substrate_id: str
    label: str
    organism: str
    cell_type: str
    perturbation: str
    phenotype: str
    conditions: tuple[str, ...]
    identifier_namespace: str
    coverage: str
    scoring_rule: str
    comparability: str
    replay: str
    artifacts: tuple[Path, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["conditions"] = list(self.conditions)
        payload["artifacts"] = [
            {
                "name": path.name,
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
            }
            for path in self.artifacts
        ]
        return payload


MANIFESTS = {
    "marson_cd4_activation": SubstrateManifest(
        substrate_id="marson_cd4_activation",
        label="Marson primary human CD4+ CRISPRi Perturb-seq",
        organism="Homo sapiens",
        cell_type="primary human CD4+ T cells",
        perturbation="CRISPR interference",
        phenotype="activation transcriptome",
        conditions=("Rest", "Stim8hr", "Stim48hr"),
        identifier_namespace="HGNC gene symbol",
        coverage="11,526 perturbation targets",
        scoring_rule="strongest on-target condition; candidate driver above 10 DE genes",
        comparability="primary",
        replay="python tests/test_marson.py",
        artifacts=(MARSON,),
    ),
    "replogle_k562": SubstrateManifest(
        substrate_id="replogle_k562",
        label="Replogle K562 Perturb-seq",
        organism="Homo sapiens",
        cell_type="K562",
        perturbation="CRISPR interference",
        phenotype="transcriptome",
        conditions=("K562",),
        identifier_namespace="HGNC gene symbol",
        coverage="genome-scale K562 projection",
        scoring_rule="candidate broad effect above 25 DE genes",
        comparability="cell_type_context",
        replay="python frontier/substrate_coverage.py --check",
        artifacts=(K562,),
    ),
    "replogle_rpe1": SubstrateManifest(
        substrate_id="replogle_rpe1",
        label="Replogle RPE1 Perturb-seq",
        organism="Homo sapiens",
        cell_type="RPE1",
        perturbation="CRISPR interference",
        phenotype="transcriptome",
        conditions=("RPE1",),
        identifier_namespace="HGNC gene symbol",
        coverage="essential-scale RPE1 projection",
        scoring_rule="candidate broad effect above 25 DE genes; non-coverage is not_assayed",
        comparability="cell_type_context",
        replay="python frontier/substrate_coverage.py --check",
        artifacts=(RPE1,),
    ),
    "orcs_primary_tcell": SubstrateManifest(
        substrate_id="orcs_primary_tcell",
        label="BioGRID ORCS primary T-cell perturbation rows",
        organism="Homo sapiens",
        cell_type="primary human T-cell contexts",
        perturbation="curated CRISPR screens",
        phenotype="screen-specific functional readouts",
        conditions=("screen-specific",),
        identifier_namespace="HGNC gene symbol",
        coverage="frozen ORCS rows for submitted signature genes",
        scoring_rule="published screen hit status, retained as orthogonal unless phenotype matches",
        comparability="orthogonal_phenotype",
        replay="python frontier/substrate_coverage.py --check",
        artifacts=(ORCS_TCELL,),
    ),
    "gse278572_cd4_context": SubstrateManifest(
        substrate_id="gse278572_cd4_context",
        label="GSE278572 primary CD4+ Teff and Treg Perturb-CITE-seq",
        organism="Homo sapiens",
        cell_type="primary human CD4+ Teff and Treg",
        perturbation="CRISPR interference",
        phenotype="resting and stimulated context transcriptome",
        conditions=("Resting-Teff", "Stimulated-Teff", "Resting-Treg", "Stimulated-Treg"),
        identifier_namespace="HGNC gene symbol",
        coverage="28 perturbation targets",
        scoring_rule="published activation score and pseudobulk DE projections",
        comparability="orthogonal_context",
        replay="python frontier/gse278572_comparator.py --check",
        artifacts=(GSE278572_MANIFEST, GSE278572_RESULT),
    ),
    "weinstock_freimer_activated_cd4_ko": SubstrateManifest(
        substrate_id="weinstock_freimer_activated_cd4_ko",
        label="GSE171737/GSE271788 activated primary CD4+ CRISPR knockout",
        organism="Homo sapiens",
        cell_type="primary human CD4+ T cells",
        perturbation="arrayed CRISPR knockout",
        phenotype="activated transcriptome",
        conditions=("CD3/CD28/CD2 activation with IL-2, RNA collected day 8",),
        identifier_namespace="HGNC gene symbol",
        coverage="84 perturbation targets, 79 overlapping Marson",
        scoring_rule="published mashr downstream-effect count at LFSR below 0.005",
        comparability="orthogonal_activation_context",
        replay="python frontier/gse271788_calibration.py --check",
        artifacts=(GSE271788_MANIFEST, GSE271788_REACH),
    ),
}


def list_substrates() -> list[dict[str, Any]]:
    return [MANIFESTS[key].to_dict() for key in sorted(MANIFESTS)]


def consulted_substrates(primary_substrate: str, evidence_mode: str) -> list[dict[str, Any]]:
    if evidence_mode not in EVIDENCE_MODES:
        raise ValueError(f"evidence_mode must be one of {sorted(EVIDENCE_MODES)}")
    keys = [primary_substrate]
    if evidence_mode == "all_frozen":
        keys.extend(key for key in sorted(MANIFESTS) if key != primary_substrate)
    return [MANIFESTS[key].to_dict() for key in keys]


def consulted_artifacts(primary_substrate: str, evidence_mode: str) -> list[dict[str, str]]:
    rows: dict[tuple[str, str, str], dict[str, str]] = {}
    for manifest in consulted_substrates(primary_substrate, evidence_mode):
        for artifact in manifest["artifacts"]:
            row = {
                "name": artifact["name"],
                "sha256": artifact["sha256"],
                "locator": artifact["path"],
            }
            rows[(row["name"], row["sha256"], row["locator"])] = row
    return [rows[key] for key in sorted(rows)]


@lru_cache(maxsize=1)
def _gse271788_rows() -> dict[str, dict[str, str]]:
    with GSE271788_REACH.open(newline="") as handle:
        return {row["gene"]: row for row in csv.DictReader(handle)}


@lru_cache(maxsize=1)
def _gse278572_rows() -> dict[str, dict[str, Any]]:
    payload = json.loads(GSE278572_RESULT.read_text())
    return {row["gene"]: row for row in payload["per_gene"]}


def _row(
    gene: str,
    substrate_id: str,
    typed_status: str,
    comparability: str,
    magnitude: int | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "gene": gene,
        "substrate_id": substrate_id,
        "typed_status": typed_status,
        "comparability": comparability,
        "magnitude": magnitude,
        "reason": reason,
    }


def _marson_row(gene: str) -> dict[str, Any]:
    conditions = _marson_condition_specificity(gene)
    covered = [
        (condition, values)
        for condition, values in conditions.items()
        if values.get("assayed") and values.get("ontarget_effect_category") == "on-target KD"
    ]
    if not covered:
        return _row(gene, "marson_cd4_activation", "not_assayed", "orthogonal_phenotype", None, "No on-target Marson condition is available.")
    condition, values = max(covered, key=lambda item: int(item[1].get("n_total_de_genes") or 0))
    magnitude = int(values.get("n_total_de_genes") or 0)
    status = "evidence_attached" if magnitude > 10 else "associative_only"
    return _row(gene, "marson_cd4_activation", status, "orthogonal_phenotype", magnitude, f"Strongest on-target Marson condition is {condition} with {magnitude} DE genes.")


def _replogle_row(gene: str, substrate_id: str) -> dict[str, Any]:
    evidence = _replogle_evidence(gene, substrate_id)
    if evidence["coverage_status"] == "not_assayed":
        return _row(gene, substrate_id, "not_assayed", "orthogonal_phenotype", None, evidence["reason"])
    magnitude = int(evidence["n_total_de_genes"])
    status = "evidence_attached" if magnitude > 25 else "associative_only"
    return _row(gene, substrate_id, status, "orthogonal_phenotype", magnitude, f"{gene} moves {magnitude} transcripts in {substrate_id}.")


def _orcs_row(gene: str) -> dict[str, Any]:
    evidence = _orcs_evidence(gene)
    if evidence["coverage_status"] == "not_assayed":
        return _row(gene, "orcs_primary_tcell", "not_assayed", "orthogonal_phenotype", None, evidence["reason"])
    best = evidence["best_row"]
    status = "evidence_attached" if best.get("hit_status") == "hit" else "associative_only"
    return _row(gene, "orcs_primary_tcell", status, "orthogonal_phenotype", best.get("rank"), evidence["reason"])


def _gse278572_row(gene: str) -> dict[str, Any]:
    source = _gse278572_rows().get(gene)
    if not source:
        return _row(gene, "gse278572_cd4_context", "not_assayed", "orthogonal_context", None, "The gene is absent from the 28-target GSE278572 panel.")
    magnitudes = [
        int(value)
        for lineage in source["lineages"]
        for value in (lineage["rest_pseudobulk_de"], lineage["stimulated_pseudobulk_de"])
    ]
    magnitude = max(magnitudes)
    status = "evidence_attached" if magnitude > 10 else "associative_only"
    return _row(gene, "gse278572_cd4_context", status, "orthogonal_context", magnitude, f"GSE278572 covers {gene}; maximum published pseudobulk reach is {magnitude} DE genes across its four contexts.")


def _gse271788_row(gene: str) -> dict[str, Any]:
    source = _gse271788_rows().get(gene)
    if not source:
        return _row(gene, "weinstock_freimer_activated_cd4_ko", "not_assayed", "orthogonal_activation_context", None, "The gene is absent from the 84-target GSE171737/GSE271788 panel.")
    magnitude = int(source["published_mashr_lfsr_lt_0_005"])
    status = "evidence_attached" if magnitude > 10 else "associative_only"
    return _row(gene, "weinstock_freimer_activated_cd4_ko", status, "orthogonal_activation_context", magnitude, f"The published day-eight activated-CD4 knockout analysis reports {magnitude} downstream effects at LFSR below 0.005.")


def build_dataset_verdicts(
    verdicts: list[dict[str, Any]],
    *,
    primary_substrate: str,
    primary_comparability: str,
    evidence_mode: str,
) -> list[dict[str, Any]]:
    if evidence_mode not in EVIDENCE_MODES:
        raise ValueError(f"evidence_mode must be one of {sorted(EVIDENCE_MODES)}")
    rows = []
    for verdict in verdicts:
        gene = verdict["gene"]
        rows.append(_row(
            gene,
            primary_substrate,
            verdict["typed_status"],
            primary_comparability,
            verdict.get("n_total_de_genes"),
            verdict["reason"],
        ))
        if evidence_mode == "primary_only":
            continue
        for substrate_id in sorted(MANIFESTS):
            if substrate_id == primary_substrate:
                continue
            if substrate_id == "marson_cd4_activation":
                rows.append(_marson_row(gene))
            elif substrate_id in {"replogle_k562", "replogle_rpe1"}:
                rows.append(_replogle_row(gene, substrate_id))
            elif substrate_id == "orcs_primary_tcell":
                rows.append(_orcs_row(gene))
            elif substrate_id == "gse278572_cd4_context":
                rows.append(_gse278572_row(gene))
            elif substrate_id == "weinstock_freimer_activated_cd4_ko":
                rows.append(_gse271788_row(gene))
    return sorted(rows, key=lambda row: (row["gene"], row["substrate_id"]))


def clear_caches() -> None:
    _gse271788_rows.cache_clear()
    _gse278572_rows.cache_clear()
