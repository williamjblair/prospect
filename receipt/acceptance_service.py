"""Canonical submission service for external Prospect acceptance checks."""
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
from receipt.substrate_router import choose_route, coverage_report, enrich_verdicts, replogle_verdicts


def _state_id(frozen: dict[str, Any]) -> str:
    blob = json.dumps(frozen, sort_keys=True, separators=(",", ":"))
    return "state_" + hashlib.sha256(blob.encode()).hexdigest()[:16]


def build_submission_result(
    text: str,
    *,
    filename: str = "",
    source_name: str = "external",
    base_url: str = "",
    claim_context: str = "",
) -> dict[str, Any]:
    parsed = parse_submission_text(text, filename=filename)
    route = choose_route(source_name=source_name, filename=filename, claim_context=claim_context)
    if route["primary_substrate"] in {"replogle_k562", "replogle_rpe1"}:
        verdicts = replogle_verdicts(parsed["genes"], route["primary_substrate"])
    else:
        verdicts = causal_verdicts(parsed["genes"])
    verdicts = enrich_verdicts(verdicts, primary_substrate=route["primary_substrate"])
    counts = verdict_counts(verdicts)
    coverage = coverage_report(verdicts, route)
    input_sha = hashlib.sha256(text.encode()).hexdigest()
    artifacts = [
        {
            "name": filename or "submitted_claim.txt",
            "sha256": input_sha,
            "locator": "submitted_inline",
        },
        {
            "name": "marson_de_full.csv",
            "sha256": sha256_file(Path(MARSON_FULL)),
            "locator": "examples/data/marson_de_full.csv",
        },
    ]
    claim = CAUSAL_RULE["claim_under_test"]
    receipt = _receipt_from_verdicts(
        producer={
            "kind": "external_workbench",
            "name": source_name,
            "input_kind": parsed["input_kind"],
            "real_export": False,
        },
        claim=claim,
        artifacts=artifacts,
        verdicts=verdicts,
        replay="python services/prospect_acceptance_service.py --port 8130",
    )
    frozen = {
        "claim": claim,
        "source_name": source_name,
        "claim_context": claim_context,
        "primary_substrate": route["primary_substrate"],
        "input_sha256": input_sha,
        "genes": [row["gene"] for row in parsed["genes"]],
        "counts": counts,
        "receipt_id": receipt["receipt_id"],
    }
    state_id = _state_id(frozen)
    state_url = f"/state/{state_id}"
    if base_url:
        state_url = base_url.rstrip("/") + state_url
    return {
        "state_id": state_id,
        "state_url": state_url,
        "accepted": False,
        "next": "human_signature_required",
        "claim_under_test": claim,
        "causal_rule": CAUSAL_RULE,
        "normalized_input": parsed,
        "prospect": {
            "verifier": "ProspectCausalReceiptBridge",
            "trust_path": "frozen Marson lookup plus human key",
            "accepted": False,
            "next": "human_signature_required",
            "route": route,
            "coverage_report": coverage,
            "typed_status_counts": counts,
            "receipt_id": receipt["receipt_id"],
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
            "interpretation": "Prospect separates candidate causal drivers from associative passengers. It does not say the submitted signature is wrong.",
        },
        "verdicts": verdicts,
        "receipt": receipt,
        "warnings": parsed["warnings"],
    }


def clear_error(exc: Exception) -> dict[str, Any]:
    return {
        "accepted": False,
        "error": str(exc),
        "next": "fix_submission",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
    }
