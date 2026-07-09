"""Frozen replay tests for canonical proposal results."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from receipt.acceptance_service import evaluate_submission
from receipt.replay_proposal import replay

ROOT = Path(__file__).resolve().parents[1]


def _proposal() -> dict:
    return evaluate_submission({
        "input_text": "IL7R\nCCR7\nPD-1\nNOTGENE",
        "filename": "genes.txt",
        "producer": "replay_test",
        "claim_mode": "associative_signature",
    })


def test_replay_recomputes_receipt_identity_and_typed_verdicts():
    result = replay(_proposal())

    assert result["receipt_id_matches"] is True
    assert result["verdicts_reproduced"] is True
    assert result["verdict_drift"] == []
    assert result["genes"] == 4
    assert result["accepted"] is False
    assert result["next"] == "human_signature_required"


def test_replay_detects_receipt_and_verdict_tampering():
    proposal = deepcopy(_proposal())
    proposal["receipt"]["verdicts"][0]["typed_status"] = "associative_only"

    result = replay(proposal)

    assert result["receipt_id_matches"] is False
    assert result["verdicts_reproduced"] is False
    assert result["verdict_drift"][0]["gene"]


def test_replay_cli_accepts_a_saved_proposal(tmp_path):
    path = tmp_path / "proposal.json"
    path.write_text(json.dumps(_proposal()))
    proc = subprocess.run(
        [sys.executable, str(ROOT / "receipt" / "replay_proposal.py"), str(path), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["receipt_id_matches"] is True
    assert result["verdicts_reproduced"] is True
