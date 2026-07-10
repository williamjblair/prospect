"""Canonical evaluator for external Prospect submissions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from receipt.causal_bridge import (
    CAUSAL_RULE,
    MARSON_FULL,
    _receipt_from_verdicts,
    causal_verdicts,
    sha256_file,
    verdict_counts,
)
from receipt.input_normalizer import parse_submission_text
from receipt.substrate_manifest import (
    EVIDENCE_MODES,
    build_dataset_verdicts,
    consulted_artifacts,
    consulted_substrates,
)
from receipt.substrate_router import (
    K562,
    RPE1,
    SUBSTRATE_LABELS,
    coverage_report,
    enrich_verdicts,
    replogle_verdicts,
)

CLAIM_MODES = {"associative_signature", "explicit_driver_claim"}
HEX_DIGITS = frozenset("0123456789abcdef")
SUBSTRATES = {
    "marson_cd4_activation": {
        "path": Path(MARSON_FULL),
        "frontier": "prospect_marson_cd4_perturbseq",
        "conditions": ["Rest", "Stim8hr", "Stim48hr"],
        "cell_tokens": {"cd4", "primary human cd4", "t cell", "t-cell"},
        "phenotypes": {"activation_transcriptome", "cd4_activation_transcriptome"},
    },
    "replogle_k562": {
        "path": Path(K562),
        "frontier": "prospect_replogle_k562_perturbseq",
        "conditions": ["K562"],
        "cell_tokens": {"k562"},
        "phenotypes": {"transcriptome", "k562_transcriptome"},
    },
    "replogle_rpe1": {
        "path": Path(RPE1),
        "frontier": "prospect_replogle_rpe1_perturbseq",
        "conditions": ["RPE1"],
        "cell_tokens": {"rpe1"},
        "phenotypes": {"transcriptome", "rpe1_transcriptome"},
    },
}


def proposal_id_for(receipt_id: str) -> str:
    return "proposal_" + hashlib.sha256(receipt_id.encode()).hexdigest()[:16]


def _context(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    if not isinstance(value, dict):
        raise ValueError("claim_context must be an object")
    return {str(key): item for key, item in value.items()}


def _citations(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise ValueError("citations must be an array of strings")
    citations: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError("citations must be an array of strings")
        if item.strip():
            citations.add(item.strip())
    return sorted(citations)


def _artifacts(
    value: Any,
    *,
    filename: str,
    input_sha: str,
    substrate_path: Path,
) -> list[dict[str, str]]:
    if value in (None, ""):
        submitted: list[Any] = []
    elif isinstance(value, list):
        submitted = value
    else:
        raise ValueError("artifacts must be an array of objects")
    if len(submitted) > 64:
        raise ValueError("artifacts may contain at most 64 entries")

    normalized: list[dict[str, str]] = []
    for item in submitted:
        if not isinstance(item, dict):
            raise ValueError("artifacts must be an array of objects")
        name = str(item.get("name") or "").strip()
        sha256 = str(item.get("sha256") or "").strip().lower()
        locator = str(item.get("locator") or "").strip()
        if not name or len(name) > 255:
            raise ValueError("each artifact needs a name no longer than 255 characters")
        if len(sha256) != 64 or any(char not in HEX_DIGITS for char in sha256):
            raise ValueError(f"artifact {name} needs a 64-character lowercase sha256")
        if len(locator) > 2048:
            raise ValueError(f"artifact {name} locator exceeds 2048 characters")
        if name == filename and sha256 != input_sha:
            raise ValueError(f"artifact {name} sha256 does not match submitted input bytes")
        normalized.append({"name": name, "sha256": sha256, "locator": locator})

    if not any(row["name"] == filename and row["sha256"] == input_sha for row in normalized):
        normalized.append({"name": filename, "sha256": input_sha, "locator": "submitted_inline"})
    normalized.append({
        "name": substrate_path.name,
        "sha256": sha256_file(substrate_path),
        "locator": str(substrate_path.relative_to(Path(__file__).resolve().parents[1])),
    })
    unique = {(row["name"], row["sha256"], row["locator"]): row for row in normalized}
    return [unique[key] for key in sorted(unique)]


def _comparability(substrate_id: str, context: dict[str, Any]) -> dict[str, str]:
    if not context:
        return {"status": "not_declared", "reason": "associative submissions do not require a causal phenotype comparison"}
    cfg = SUBSTRATES[substrate_id]
    cell_type = str(context.get("cell_type") or "").lower()
    phenotype = str(context.get("phenotype") or "").lower()
    condition = str(context.get("condition") or "")
    cell_match = any(token in cell_type for token in cfg["cell_tokens"])
    phenotype_match = phenotype in cfg["phenotypes"]
    condition_match = condition in cfg["conditions"] or condition in {"strongest", "any"}
    if cell_match and phenotype_match and condition_match:
        return {"status": "comparable", "reason": "cell type, phenotype, and condition match the frozen substrate"}
    return {"status": "orthogonal_phenotype", "reason": "submitted cell type, phenotype, or condition does not match the frozen substrate"}


def _validate_request(request: dict[str, Any]) -> tuple[str, str, dict[str, Any], str, str]:
    claim_mode = str(request.get("claim_mode") or "associative_signature")
    if claim_mode not in CLAIM_MODES:
        raise ValueError(f"claim_mode must be one of {sorted(CLAIM_MODES)}")
    substrate_id = str(request.get("substrate_id") or "marson_cd4_activation")
    if substrate_id not in SUBSTRATES:
        raise ValueError(f"substrate_id must be one of {sorted(SUBSTRATES)}")
    evidence_mode = str(request.get("evidence_mode") or "primary_only")
    if evidence_mode not in EVIDENCE_MODES:
        raise ValueError(f"evidence_mode must be one of {sorted(EVIDENCE_MODES)}")
    context = _context(request.get("claim_context"))
    claim_source = str(context.get("source") or context.get("claim") or "").strip()
    if claim_mode == "explicit_driver_claim":
        missing = [key for key in ("cell_type", "condition", "phenotype") if not context.get(key)]
        if not claim_source:
            missing.append("source")
        if missing:
            raise ValueError("explicit_driver_claim requires claim_context fields: " + ", ".join(missing))
    return claim_mode, substrate_id, context, claim_source, evidence_mode


def evaluate_submission(request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one normalized request through the frozen, model-free rule."""

    text = str(request.get("input_text") or request.get("text") or "")
    filename = str(request.get("filename") or "submission.txt")
    producer_value = request.get("producer") or request.get("source_name") or "external"
    producer = dict(producer_value) if isinstance(producer_value, dict) else {"name": str(producer_value)}
    producer.setdefault("kind", "external_workbench")
    producer["identity_status"] = "self_declared"
    claim_mode, substrate_id, context, claim_source, evidence_mode = _validate_request(request)
    parsed = parse_submission_text(text, filename=filename)
    comparability = _comparability(substrate_id, context)

    if substrate_id == "marson_cd4_activation":
        verdicts = causal_verdicts(
            parsed["genes"],
            claim_mode=claim_mode,
            claim_source=claim_source,
            comparable_readout=comparability["status"] in {"comparable", "not_declared"},
            comparability_status=comparability["status"],
        )
    else:
        verdicts = replogle_verdicts(parsed["genes"], substrate_id)
    verdicts = enrich_verdicts(verdicts, primary_substrate=substrate_id)
    manifests = consulted_substrates(substrate_id, evidence_mode)
    dataset_verdicts = build_dataset_verdicts(
        verdicts,
        primary_substrate=substrate_id,
        primary_comparability=comparability["status"],
        evidence_mode=evidence_mode,
    )
    counts = verdict_counts(verdicts)
    route = {
        "primary_substrate": substrate_id,
        "routing_reason": "the submitter selected this frozen substrate explicitly",
    }
    coverage = coverage_report(verdicts, route)
    cfg = SUBSTRATES[substrate_id]
    input_sha = hashlib.sha256(text.encode()).hexdigest()
    artifacts = _artifacts(
        request.get("artifacts"),
        filename=filename,
        input_sha=input_sha,
        substrate_path=cfg["path"],
    )
    if evidence_mode == "all_frozen":
        combined = [*artifacts, *consulted_artifacts(substrate_id, evidence_mode)]
        unique = {(row["name"], row["sha256"], row["locator"]): row for row in combined}
        artifacts = [unique[key] for key in sorted(unique)]
    if claim_mode == "explicit_driver_claim":
        claim = f"Explicit causal-driver claim from {claim_source}"
    else:
        claim = "Which genes in the submitted associative signature behave as candidate causal drivers in the selected frozen substrate?"
    replay = "python receipt/replay_proposal.py <proposal.json-or-url>"
    rule = {**CAUSAL_RULE, "claim_mode": claim_mode, "comparability": comparability}
    citations = _citations(request.get("citations"))
    request_metadata = {
        "claim_mode": claim_mode,
        "claim_context": context,
        "citations": citations,
        "substrate_id": substrate_id,
    }
    if evidence_mode == "all_frozen":
        request_metadata.update({
            "evidence_mode": evidence_mode,
            "consulted_substrates": manifests,
            "dataset_verdicts": dataset_verdicts,
        })
    receipt = _receipt_from_verdicts(
        producer=producer,
        claim=claim,
        artifacts=artifacts,
        verdicts=verdicts,
        replay=replay,
        frontier=cfg["frontier"],
        source_label=SUBSTRATE_LABELS[substrate_id],
        conditions=[*cfg["conditions"], "proposal only"],
        rule=rule,
        request_metadata=request_metadata,
    )
    proposal_id = proposal_id_for(receipt["receipt_id"])
    return {
        "proposal_id": proposal_id,
        "proposal_url": f"/proposal/{proposal_id}",
        "accepted": False,
        "next": "human_signature_required",
        "claim_under_test": claim,
        "claim_mode": claim_mode,
        "claim_context": context,
        "evidence_mode": evidence_mode,
        "citations": citations,
        "comparability": comparability,
        "consulted_substrates": manifests,
        "dataset_verdicts": dataset_verdicts,
        "normalized_input": parsed,
        "prospect": {
            "verifier": "ProspectCausalReceiptBridge",
            "trust_path": "frozen substrate lookup plus human key",
            "accepted": False,
            "next": "human_signature_required",
            "route": route,
            "coverage_report": coverage,
            "evidence_mode": evidence_mode,
            "consulted_substrate_count": len(manifests),
            "typed_status_counts": counts,
            "receipt_id": receipt["receipt_id"],
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
            "interpretation": "Prospect separates candidate causal drivers from associative passengers for the selected assay.",
        },
        "verdicts": verdicts,
        "receipt": receipt,
        "warnings": parsed["warnings"],
        "replay_command": replay,
        "publish_to_ledger": bool(request.get("publish_to_ledger", False)),
        # Compatibility aliases. They carry proposal identifiers, never accepted state.
        "state_id": proposal_id,
        "state_url": f"/proposal/{proposal_id}",
    }


def build_submission_result(
    text: str,
    *,
    filename: str = "",
    source_name: str = "external",
    base_url: str = "",
    claim_context: dict[str, Any] | str | None = None,
    claim_mode: str = "associative_signature",
    substrate_id: str = "marson_cd4_activation",
    evidence_mode: str = "primary_only",
    publish_to_ledger: bool = False,
) -> dict[str, Any]:
    if isinstance(claim_context, str):
        lowered = claim_context.lower()
        if "k562" in lowered:
            substrate_id = "replogle_k562"
        elif "rpe1" in lowered:
            substrate_id = "replogle_rpe1"
        claim_context = {}
    result = evaluate_submission({
        "input_text": text,
        "filename": filename or "submission.txt",
        "producer": source_name,
        "substrate_id": substrate_id,
        "claim_mode": claim_mode,
        "claim_context": claim_context or {},
        "evidence_mode": evidence_mode,
        "publish_to_ledger": publish_to_ledger,
    })
    if base_url:
        result["proposal_url"] = base_url.rstrip("/") + result["proposal_url"]
        result["state_url"] = result["proposal_url"]
    return result


def clear_error(exc: Exception) -> dict[str, Any]:
    return {
        "accepted": False,
        "error": str(exc),
        "next": "fix_submission",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
    }
