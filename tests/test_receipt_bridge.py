"""Receipt bridge contract tests.

The bridge makes Prospect receipts portable to an external workbench without
moving accepted state. It exports a contract, a manifest, and the current
receipts. The validator must reject malformed receipts before any consumer can
treat them as proposals.
"""
import json
import os
import sys
from copy import deepcopy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from receipt.bridge import export_bridge, validate_receipt


def test_export_bridge_writes_contract_manifest_and_bundle(tmp_path):
    bundle = export_bridge(outdir=tmp_path)

    assert (tmp_path / "receipt_contract.json").exists()
    assert (tmp_path / "receipt_manifest.json").exists()
    assert (tmp_path / "receipt_bundle.json").exists()
    assert bundle["contract"]["schema_version"] == "prospect.receipt.v1"
    assert bundle["contract"]["mcp"]["command"] == "./prospect mcp"
    assert bundle["manifest"]["frontier_root"].startswith("root_")
    assert bundle["manifest"]["mcp_command"] == "./prospect mcp"
    assert [s["method"] for s in bundle["manifest"]["protocol_path"]] == [
        "prospect.receipt.schema",
        "prospect.receipt.validate",
        "prospect.receipt.submit",
        "prospect.receipt.submit_artifact",
    ]
    assert bundle["manifest"]["protocol_path"][-1]["result"] == "proposal_only"
    assert bundle["manifest"]["protocol_path"][-1]["accepted"] is False
    assert "prospect.receipt.submit" in bundle["contract"]["methods"]
    assert "prospect.receipt.submit_artifact" in bundle["contract"]["methods"]
    assert len(bundle["receipts"]) >= 6
    assert all(r["receipt_id"].startswith("rcpt_") for r in bundle["receipts"])
    assert all(r["accepted"] is False for r in bundle["receipts"])
    assert all((r.get("acceptance") or {}).get("attestation_type") == "legacy_frontier_root_signature"
               for r in bundle["receipts"])


def test_validate_receipt_accepts_current_receipt_and_rejects_bad_status():
    path = os.path.join(ROOT, "receipts", "receipts.jsonl")
    receipt = json.loads(open(path).readline())

    assert validate_receipt(receipt) == []

    bad = dict(receipt)
    bad["status"] = "verified"
    errors = validate_receipt(bad)
    assert any("status" in e for e in errors)

    bad_acceptance = dict(receipt)
    bad_acceptance["accepted"] = True
    errors = validate_receipt(bad_acceptance)
    assert any("accepted=false" in e for e in errors)


def test_receipt_id_binds_every_trust_field(tmp_path):
    from receipt.emit import emit_all

    receipts = emit_all(outdir=str(tmp_path))
    receipt = receipts[0].to_dict()
    assert validate_receipt(receipt) == []
    mutations = [
        ("claim", "changed claim"),
        ("producer", {"kind": "other"}),
        ("conditions", ["other condition"]),
        ("verifier", {**receipt["verifier"], "replay": "other command"}),
        ("replay_metadata", {**receipt["replay_metadata"], "command": "other command"}),
        ("state_diff", {**receipt["state_diff"], "effect": "other effect"}),
        ("verdicts", [{"gene": "OTHER", "typed_status": "not_assayed"}]),
    ]
    for field, value in mutations:
        changed = deepcopy(receipt)
        changed[field] = value
        assert any("receipt_id" in error for error in validate_receipt(changed)), field


if __name__ == "__main__":
    test_export_bridge_writes_contract_manifest_and_bundle(__import__("pathlib").Path("/tmp/prospect-receipt-bridge-test"))
    test_validate_receipt_accepts_current_receipt_and_rejects_bad_status()
    print("PASS: receipt bridge contract")
