"""Storage and deployment contracts for the production acceptance service."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import pytest

from receipt.acceptance_service import evaluate_submission
from services.prospect_acceptance_service import AcceptanceStore

ROOT = Path(__file__).resolve().parents[1]


def _result(*, publish: bool = False, producer: str = "external_team") -> dict:
    return evaluate_submission(
        {
            "input_text": "IL7R\nCCR7\nPD-1",
            "filename": "genes.txt",
            "producer": producer,
            "claim_mode": "associative_signature",
            "publish_to_ledger": publish,
        }
    )


def test_store_uses_immutable_proposals_and_append_only_submission_events(tmp_path):
    store = AcceptanceStore(tmp_path)
    first = store.store_result(_result(publish=True))
    second = store.store_result(_result(publish=True))

    assert first["proposal_id"] == second["proposal_id"]
    assert first["submission_event_id"] != second["submission_event_id"]
    assert first["accepted"] is False
    assert first["next"] == "human_signature_required"
    assert first["producer_identity_status"] == "self_declared"
    assert first["proposal_url"].startswith("/proposal/")
    assert "state_url" not in first
    assert store.table_counts() == {
        "proposals": 1,
        "submission_events": 2,
        "acceptance_events": 0,
    }

    reloaded = AcceptanceStore(tmp_path).get(first["proposal_id"])
    assert reloaded is not None
    assert reloaded["receipt"]["receipt_id"] == first["receipt"]["receipt_id"]
    assert reloaded["accepted"] is False


def test_store_rejects_content_change_under_existing_proposal_id(tmp_path):
    store = AcceptanceStore(tmp_path)
    result = _result()
    store.store_result(result)
    tampered = json.loads(json.dumps(result))
    tampered["verdicts"][0]["reason"] = "changed after evaluation"

    with pytest.raises(ValueError, match="different immutable content"):
        store.store_result(tampered)

    assert store.table_counts()["submission_events"] == 1


def test_store_replays_exact_legacy_primary_only_proposal_without_mutation(tmp_path):
    store = AcceptanceStore(tmp_path)
    result = _result()
    current_payload = store._proposal_payload(result)
    legacy_payload = json.loads(json.dumps(current_payload))
    legacy_payload.pop("evidence_mode")
    legacy_payload.pop("consulted_substrates")
    legacy_payload.pop("dataset_verdicts")
    legacy_payload["prospect"].pop("evidence_mode")
    legacy_payload["prospect"].pop("consulted_substrate_count")

    with sqlite3.connect(store.db_path) as connection:
        connection.execute(
            "INSERT INTO proposals(proposal_id, receipt_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (
                result["proposal_id"],
                result["receipt"]["receipt_id"],
                json.dumps(legacy_payload, sort_keys=True, separators=(",", ":")),
                "2026-07-09T00:00:00Z",
            ),
        )

    replayed = store.store_result(result)
    persisted = store.get(result["proposal_id"])

    assert replayed["receipt"] == result["receipt"]
    assert "evidence_mode" not in replayed
    assert persisted is not None
    assert "evidence_mode" not in persisted
    assert store.table_counts() == {
        "proposals": 1,
        "submission_events": 1,
        "acceptance_events": 0,
    }


def test_publish_to_ledger_controls_visibility_not_persistence(tmp_path):
    store = AcceptanceStore(tmp_path)
    private = store.store_result(_result(publish=False, producer="public_team"))
    public = store.store_result(_result(publish=True, producer="public_team"))

    assert private["proposal_id"] == public["proposal_id"]
    assert store.get(private["proposal_id"]) is not None
    ledger = store.ledger()
    assert ledger["submission_count"] == 1
    assert ledger["proposal_count"] == 1
    assert ledger["total_event_count"] == 2
    assert ledger["by_producer"] == {"public_team": 1}
    assert ledger["recent"][0]["producer_identity_status"] == "self_declared"
    assert ledger["recent"][0]["proposal_url"].startswith("/proposal/")
    assert ledger["typed_status_counts"] == {
        "evidence_attached": 1,
        "associative_only": 2,
        "contradicted": 0,
        "not_assayed": 0,
    }
    assert ledger["passenger_or_contradicted"] == {
        "count": 2,
        "denominator": 3,
        "rate": 0.6667,
    }


def test_sqlite_schema_separates_acceptance_events(tmp_path):
    store = AcceptanceStore(tmp_path)
    store.store_result(_result())

    with sqlite3.connect(store.db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        proposal = connection.execute("SELECT proposal_id, receipt_id, payload_json FROM proposals").fetchone()
        acceptance_count = connection.execute("SELECT COUNT(*) FROM acceptance_events").fetchone()[0]

    assert {"proposals", "submission_events", "acceptance_events"} <= tables
    assert proposal[0].startswith("proposal_")
    assert proposal[1].startswith("rcpt_")
    assert json.loads(proposal[2])["accepted"] is False
    assert acceptance_count == 0


def test_invalid_proposal_ids_do_not_reach_sql(tmp_path):
    store = AcceptanceStore(tmp_path)
    with pytest.raises(ValueError, match="invalid proposal id"):
        store.get("../../receipt")


def test_acceptance_container_and_fly_configuration_are_pinned():
    dockerfile = (ROOT / "Dockerfile.acceptance").read_text()
    fly_config = (ROOT / "fly.acceptance.toml").read_text()
    dockerignore = (ROOT / ".dockerignore").read_text()
    acceptance_requirements = (ROOT / "requirements.acceptance.txt").read_text()

    assert "requirements.acceptance.txt" in dockerfile
    assert "PROSPECT_ACCEPTANCE_DATA_DIR" in dockerfile
    assert "PROSPECT_ACCEPTANCE_CORS_ORIGIN" in dockerfile
    assert "/health" in dockerfile
    assert "internal_port = 8130" in fly_config
    assert "PROSPECT_ACCEPTANCE_PUBLIC_URL" in fly_config
    assert "PROSPECT_ACCEPTANCE_MAX_REQUEST_BYTES" in fly_config
    assert "PROSPECT_ACCEPTANCE_MAX_GENES" in fly_config
    assert "web/node_modules" in dockerignore
    assert "output" in dockerignore
    assert "mcp==" in acceptance_requirements
    assert "uvicorn==" in acceptance_requirements


def test_owned_files_follow_copy_discipline():
    paths = [
        ROOT / "services" / "prospect_acceptance_service.py",
        ROOT / "Dockerfile.acceptance",
        ROOT / "fly.acceptance.toml",
        ROOT / ".dockerignore",
        ROOT / "requirements.txt",
        ROOT / "requirements.acceptance.txt",
        ROOT / "docs" / "DEPLOY_READINESS.md",
    ]
    text = "\n".join(path.read_text() for path in paths)
    assert "\N{EM DASH}" not in text
    for forbidden in ("Ve" + "la", "Con" + "stellate", "Car" + "ina"):
        assert forbidden not in text
