#!/usr/bin/env python3
"""Re-derive a Prospect proposal's typed verdicts from frozen substrates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from receipt.acceptance_service import SUBSTRATES, _comparability
from receipt.causal_bridge import causal_verdicts
from receipt.schema import receipt_id_for
from receipt.substrate_router import enrich_verdicts, replogle_verdicts

CORE_FIELDS = (
    "gene",
    "typed_status",
    "driver_claim",
    "claim_mode",
    "comparability",
    "condition",
    "n_total_de_genes",
    "ontarget_effect_category",
    "reason",
    "primary_substrate",
    "direction",
    "magnitude",
    "condition_specificity",
    "substrate_evidence",
)


def _load(source: str) -> dict[str, Any]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        with urlopen(source, timeout=15) as response:
            payload = json.loads(response.read())
    else:
        payload = json.loads(Path(source).read_text())
    if not isinstance(payload, dict):
        raise ValueError("proposal JSON must contain an object")
    return payload


def _core(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in CORE_FIELDS}


def replay(payload: dict[str, Any]) -> dict[str, Any]:
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        raise ValueError("proposal JSON lacks a receipt object")
    stored_receipt_id = str(receipt.get("receipt_id") or "")
    recomputed_receipt_id = receipt_id_for(receipt)
    metadata = receipt.get("replay_metadata") or {}
    request = metadata.get("request") or {}
    substrate_id = str(request.get("substrate_id") or "")
    if substrate_id not in SUBSTRATES:
        raise ValueError("proposal receipt has an unsupported substrate_id")
    claim_mode = str(request.get("claim_mode") or "associative_signature")
    context = request.get("claim_context") or {}
    claim_source = str(context.get("source") or context.get("claim") or "").strip()
    comparability = _comparability(substrate_id, context)
    genes = [str(gene) for gene in receipt.get("subject") or []]
    if not genes:
        raise ValueError("proposal receipt has no subject genes")

    if substrate_id == "marson_cd4_activation":
        rederived = causal_verdicts(
            genes,
            claim_mode=claim_mode,
            claim_source=claim_source,
            comparable_readout=comparability["status"] in {"comparable", "not_declared"},
            comparability_status=comparability["status"],
        )
    else:
        rederived = replogle_verdicts(genes, substrate_id)
    rederived = enrich_verdicts(rederived, primary_substrate=substrate_id)

    stored_by_gene = {str(row.get("gene") or ""): row for row in receipt.get("verdicts") or []}
    rederived_by_gene = {str(row.get("gene") or ""): row for row in rederived}
    drift = []
    for gene in sorted(set(stored_by_gene) | set(rederived_by_gene)):
        stored = stored_by_gene.get(gene)
        current = rederived_by_gene.get(gene)
        if stored is None or current is None or _core(stored) != _core(current):
            drift.append({"gene": gene, "stored": _core(stored or {}), "rederived": _core(current or {})})

    return {
        "proposal_id": payload.get("proposal_id"),
        "receipt_id": stored_receipt_id,
        "recomputed_receipt_id": recomputed_receipt_id,
        "receipt_id_matches": stored_receipt_id == recomputed_receipt_id,
        "genes": len(genes),
        "verdict_drift": drift,
        "verdicts_reproduced": not drift,
        "accepted": False,
        "next": "human_signature_required",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="receipt/replay_proposal.py")
    parser.add_argument("proposal", help="proposal JSON path or HTTPS URL")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)
    try:
        result = replay(_load(args.proposal))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"replay failed: {exc}", file=sys.stderr)
        return 1
    passed = result["receipt_id_matches"] and result["verdicts_reproduced"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"{result['proposal_id']} receipt_id_matches={str(result['receipt_id_matches']).lower()} "
            f"verdicts_reproduced={str(result['verdicts_reproduced']).lower()} "
            f"genes={result['genes']} accepted=false"
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
