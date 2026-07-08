"""Specify lab writeback receipts without mutating accepted state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "lab_writeback_receipt.json"
OUT_DOC = ROOT / "docs" / "LAB_WRITEBACK_RECEIPT.md"
RECEIPTS = ROOT / "receipts" / "receipts.jsonl"
LAB_PACKET = DATA / "lab_packet.json"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _pggt1b_receipt() -> dict[str, Any]:
    for receipt in _jsonl(RECEIPTS):
        if receipt.get("kind") == "hypothesis" and "PGGT1B" in receipt.get("subject", []):
            return receipt
    raise RuntimeError("PGGT1B hypothesis receipt not found")


def _pggt1b_lab_row() -> dict[str, Any]:
    lab = _json(LAB_PACKET)
    for row in lab.get("candidates", []):
        if row.get("gene") == "PGGT1B":
            return row
    raise RuntimeError("PGGT1B lab packet row not found")


def _return_receipt(outcome: str, typed_status: str, receipt: dict[str, Any], lab_row: dict[str, Any]) -> dict[str, Any]:
    refuting = outcome == "refuting"
    readout = (
        "executed assay shows loss of the stimulated activation-program shift under orthogonal knockdown"
        if refuting else
        "executed assay reproduces a stimulated activation-program shift under orthogonal knockdown"
    )
    return {
        "outcome": outcome,
        "typed_status": typed_status,
        "accepted": False,
        "frontier": "prospect_marson_cd4_perturbseq",
        "kind": "lab_writeback",
        "subject": ["PGGT1B"],
        "claim": (
            "PGGT1B orthogonal follow-up refutes the evidence-attached activation-gate proposal."
            if refuting else
            "PGGT1B orthogonal follow-up supports the evidence-attached activation-gate proposal."
        ),
        "executed_protocol": {
            "source_packet": "examples/data/lab_packet.json",
            "protocol": lab_row["primary_readout"],
            "intervention": lab_row["intervention"],
            "sample": lab_row["sample"],
            "conditions": lab_row["conditions"],
            "controls": {
                "positive": lab_row["positive_controls"],
                "negative": lab_row["negative_controls"],
            },
        },
        "assay_readout": {
            "summary": readout,
            "required_measurements": [
                "knockdown efficiency",
                "activation-marker flow cytometry",
                "targeted RNA-seq at 8h and 48h",
                "Rest matched culture",
            ],
            "result_payload": "required_from_lab_execution",
        },
        "affected_claims": [
            {
                "receipt_id": receipt["receipt_id"],
                "gene": "PGGT1B",
                "prior_status": receipt["status"],
                "prior_claim": receipt["claim"],
            }
        ],
        "reviewer_signature": {
            "required": True,
            "present": False,
            "signer_role": "human_reviewer",
            "signature_field": "ed25519_signature_over_return_receipt",
        },
        "state_diff": {
            "accepted": False,
            "model_can_apply": False,
            "delta_id": "",
            "effect": "proposal_only_no_state_mutation",
            "target": "PGGT1B evidence-attached claim",
        },
        "next": "human_signature_required",
    }


def build_packet() -> dict[str, Any]:
    receipt = _pggt1b_receipt()
    lab_row = _pggt1b_lab_row()
    return {
        "title": "Lab writeback receipt",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "accepted_state_mutation": "none",
        "receipt_kind": "lab_writeback",
        "source": "specified return shape for the wet-lab assay packet",
        "return_shape_required": [
            "executed_protocol",
            "assay_readout",
            "affected_claims",
            "reviewer_signature",
            "state_diff",
        ],
        "return_receipts": [
            _return_receipt("confirming", "independently_reanalyzed", receipt, lab_row),
            _return_receipt("refuting", "contradicted", receipt, lab_row),
        ],
        "contradiction_rule": {
            "title": "Contradiction as proposal",
            "accepted_claim_mutation": "never_overwrite",
            "new_object": "receipt",
            "required_status": "contradicted",
            "accepted": False,
            "next": "human_signature_required",
            "rule": (
                "A later contradiction of an accepted claim is submitted as a new receipt proposal. "
                "It cites the affected accepted receipt and waits for review, replay, and human signing."
            ),
        },
    }


def _markdown(packet: dict[str, Any]) -> str:
    fields = "\n".join(f"- `{field}`" for field in packet["return_shape_required"])
    lines = [
        "# Lab writeback receipt",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        "A wet-lab result returns to Prospect as a receipt with one shape whether it confirms or refutes.",
        "It never overwrites accepted state. It proposes a state transition and waits for a human key.",
        "",
        "## Required return shape",
        "",
        fields,
        "",
        "## Contradiction as proposal",
        "",
        "`never_overwrite`: a later contradiction of an accepted claim is a new `contradicted` receipt.",
        "It cites the affected claim, carries the executed protocol and assay readout, and returns",
        "`accepted=false` with `human_signature_required` until review accepts a new signed state event.",
        "",
        "## Template receipts",
        "",
    ]
    for receipt in packet["return_receipts"]:
        lines += [
            f"### {receipt['outcome']}",
            "",
            f"- Typed status: `{receipt['typed_status']}`",
            f"- Accepted: `{str(receipt['accepted']).lower()}`",
            f"- State effect: `{receipt['state_diff']['effect']}`",
            f"- Affected claim: `{receipt['affected_claims'][0]['receipt_id']}`",
            "",
        ]
    lines += [
        "Rebuild:",
        "",
        "```bash",
        "python -m receipt.writeback",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_packet(out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC) -> dict[str, Any]:
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m receipt.writeback")
    parser.add_argument("--check", action="store_true", help="check the committed packet without rewriting")
    args = parser.parse_args(argv)
    built = build_packet()
    if args.check:
        current = _json(OUT_JSON)
        if current != built:
            raise SystemExit("lab writeback receipt drift")
        print("lab writeback receipt ok: accepted=false")
        return
    write_packet()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
