"""Export and validate the Prospect receipt bridge.

This is the small external-workbench contract: activity producers emit a
Prospect-shaped receipt, the frozen gate validates structure and replay fields,
and accepted state still requires the existing human signature path.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"
FRONTIER_SIG = ROOT / "frontier" / "frontier.sig.json"
DEFAULT_OUT = ROOT / "receipts" / "bridge"

STATUSES = {
    "claimed",
    "evidence_attached",
    "computationally_reproduced",
    "independently_reanalyzed",
    "contradicted",
    "refuted",
}
REPLAYABILITY = {"exact", "reanalysis", "attested", "none"}
REQUIRED = {
    "receipt_id",
    "frontier",
    "claim",
    "kind",
    "subject",
    "producer",
    "artifacts",
    "evidence",
    "verifier",
    "status",
    "replayability",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _frontier_sig() -> dict[str, Any]:
    if not FRONTIER_SIG.exists():
        return {}
    return json.loads(FRONTIER_SIG.read_text())


def contract() -> dict[str, Any]:
    """Return the portable receipt contract for external producers."""
    return {
        "schema_version": "prospect.receipt.v1",
        "frontier": "prospect_marson_cd4_perturbseq",
        "mcp": {
            "transport": "stdio",
            "protocol_version": "2025-11-25",
            "command": "./prospect mcp",
        },
        "boundary": ["Activity", "Receipt", "Proposal", "Review", "Verification", "Accepted", "State"],
        "required_fields": sorted(REQUIRED),
        "statuses": sorted(STATUSES),
        "replayability": sorted(REPLAYABILITY),
        "methods": {
            "prospect.receipt.schema": {
                "description": "Return this contract so an external workbench can shape a receipt.",
                "input": {},
                "output": "prospect.receipt.v1",
            },
            "prospect.receipt.validate": {
                "description": "Check receipt shape, typed status, replay fields, and acceptance fields.",
                "input": {"receipt": "prospect.receipt.v1"},
                "output": {"errors": "list[str]"},
            },
            "prospect.receipt.submit": {
                "description": "Submit a receipt as a proposal. This never moves accepted state by itself.",
                "input": {"receipt": "prospect.receipt.v1"},
                "output": {"accepted": False, "next": "human signature over an accepted delta"},
            },
        },
        "trust_path": [
            "producer activity is untrusted",
            "receipt binds claim, artifacts, evidence atoms, verifier, replay, and typed status",
            "frozen verifier decides what re-derives",
            "human Ed25519 key accepts state",
        ],
    }


def manifest(receipts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    sig = _frontier_sig()
    receipts = receipts if receipts is not None else _read_jsonl(RECEIPTS)
    return {
        "frontier": "prospect_marson_cd4_perturbseq",
        "frontier_root": sig.get("root", ""),
        "signer": sig.get("signer", ""),
        "receipt_count": len(receipts),
        "receipt_ids": [r.get("receipt_id", "") for r in receipts],
        "replay": "./prospect verify",
        "mcp_command": "./prospect mcp",
        "exported_files": [
            "receipt_contract.json",
            "receipt_manifest.json",
            "receipt_bundle.json",
        ],
    }


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    """Return a list of contract errors. Empty means structurally admissible."""
    errors: list[str] = []
    missing = sorted(k for k in REQUIRED if k not in receipt)
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
    if receipt.get("status") not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    if receipt.get("replayability") not in REPLAYABILITY:
        errors.append(f"replayability must be one of {sorted(REPLAYABILITY)}")
    if not isinstance(receipt.get("subject"), list) or not receipt.get("subject"):
        errors.append("subject must be a non-empty list")
    if not isinstance(receipt.get("artifacts"), list) or not receipt.get("artifacts"):
        errors.append("artifacts must be a non-empty list")
    if not isinstance(receipt.get("evidence"), list):
        errors.append("evidence must be a list")
    verifier = receipt.get("verifier")
    if not isinstance(verifier, dict):
        errors.append("verifier must be an object")
    else:
        for key in ("name", "method", "replay"):
            if not verifier.get(key):
                errors.append(f"verifier.{key} is required")
    accepted = receipt.get("accepted", False)
    if accepted and not receipt.get("acceptance"):
        errors.append("accepted receipt requires acceptance")
    if receipt.get("receipt_id") and not str(receipt["receipt_id"]).startswith("rcpt_"):
        errors.append("receipt_id must start with rcpt_")
    return errors


def export_bridge(outdir: str | os.PathLike[str] = DEFAULT_OUT) -> dict[str, Any]:
    """Write the bridge contract, manifest, and receipt bundle."""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    receipts = _read_jsonl(RECEIPTS)
    c = contract()
    m = manifest(receipts)
    bundle = {"contract": c, "manifest": m, "receipts": receipts}

    (out / "receipt_contract.json").write_text(json.dumps(c, indent=2) + "\n")
    (out / "receipt_manifest.json").write_text(json.dumps(m, indent=2) + "\n")
    (out / "receipt_bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")
    return bundle


def main(argv: list[str] | None = None) -> None:
    import argparse

    ap = argparse.ArgumentParser(prog="python -m receipt.bridge")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="directory for bridge artifacts")
    args = ap.parse_args(argv)
    bundle = export_bridge(args.out)
    errors = [e for r in bundle["receipts"] for e in validate_receipt(r)]
    if errors:
        raise SystemExit("receipt bridge validation failed: " + "; ".join(errors))
    print(f"exported receipt bridge -> {args.out} ({len(bundle['receipts'])} receipts)")


if __name__ == "__main__":
    main()
