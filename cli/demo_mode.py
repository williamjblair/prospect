"""Deterministic recording mode for the Prospect judge demo."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
from typing import Any

from receipt.acceptance_service import build_submission_result
from services.prospect_acceptance_service import AcceptanceStore, DEFAULT_DATA_DIR

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"

DEMO_SUBMISSION = "IL7R\nCCR7\nPD-1\nENSG00000121410\nNOTGENE"
DEFAULT_BASE_URL = "http://127.0.0.1:8130"


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((DATA / name).read_text())


def reset_demo_state(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Any]:
    path = Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    database = path / "acceptance.sqlite3"
    removed = 0
    if database.exists():
        try:
            with sqlite3.connect(database) as connection:
                removed = int(connection.execute("SELECT COUNT(*) FROM proposals").fetchone()[0])
        except sqlite3.Error:
            removed = 0
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(str(database) + suffix)
        if candidate.exists():
            candidate.unlink()
    return {
        "data_dir": str(path),
        "database": str(database),
        "removed_proposals": removed,
        "accepted": False,
        "next": "human_signature_required",
    }


def build_demo_packet(
    *,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    base_url: str = DEFAULT_BASE_URL,
    reset: bool = False,
) -> dict[str, Any]:
    if reset:
        reset_demo_state(data_dir)

    claude = _load_json("claude_science_acceptance_demo.json")
    pggt = _load_json("pggt1b_defended_evidence.json")
    overclaim = _load_json("overclaim_counter.json")
    correction = _load_json("gse278572_comparator.json")

    submission = build_submission_result(
        DEMO_SUBMISSION,
        filename="demo_genes.txt",
        source_name="demo_recording",
        base_url=base_url,
        publish_to_ledger=True,
    )
    stored = AcceptanceStore(data_dir).store_result(submission)
    ledger = AcceptanceStore(data_dir).ledger()
    claude_counts = claude["prospect"]["typed_status_counts"]
    paste_counts = stored["prospect"]["typed_status_counts"]

    return {
        "demo_id": "prospect_finish_and_win_demo",
        "accepted": False,
        "next": "human_signature_required",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        "data_dir": str(data_dir),
        "beats": [
            {
                "id": "real_claude_science_export",
                "title": "Real Claude Science export enters Prospect",
                "status": "proposal_only",
                "counts": {
                    "genes": claude_counts["genes"],
                    "drivers": claude_counts["drivers"],
                    "passengers": claude_counts["passengers"],
                    "contradicted": claude_counts["contradicted"],
                    "not_assayed": claude_counts["not_assayed"],
                },
                "command": "python examples/claude_science_connector_client.py --json",
                "artifact": "examples/data/claude_science_acceptance_demo.json",
            },
            {
                "id": "overclaim_benchmark",
                "title": "Independent replay catches broad causal overclaims",
                "status": "contradicted",
                "counts": {
                    "comparable_claims": overclaim["counts"]["model_checkable_claims"],
                    "contradicted": overclaim["counts"]["model_contradicted_claims"],
                    "rate": overclaim["counts"]["model_contradicted_rate"],
                    "checkpoint_and_cytokine_rate": overclaim["counts"]["effector_overclaim_rate"],
                },
                "command": "./prospect overclaim-counter",
                "artifact": "examples/data/overclaim_counter.json",
            },
            {
                "id": "med12_correction",
                "title": "Prospect qualifies its own Rest-reach interpretation",
                "status": "evidence_attached",
                "counts": {
                    "overlap_genes": correction["comparison"]["prospect_overlap"],
                    "high_rest_genes": correction["finding3_review"]["n_high_rest_genes_in_overlap"],
                    "qualified": correction["finding3_review"]["n_needs_qualification"],
                },
                "subject": correction["finding3_review"]["needs_qualification"],
                "command": "python frontier/gse278572_comparator.py --check",
                "artifact": "examples/data/gse278572_comparator.json",
            },
            {
                "id": "pggt1b_hypothesis",
                "title": "PGGT1B is the one proposal-only lead worth testing",
                "status": pggt["defended_discovery_status"],
                "mechanism": pggt["mechanism_dossier"]["partners"][:3],
                "command": "./prospect pggt1b-defended-evidence",
                "artifact": "examples/data/pggt1b_defended_evidence.json",
            },
            {
                "id": "run_your_own_claim",
                "title": "Paste path creates a shareable result",
                "status": "proposal_only",
                "proposal_url": stored["proposal_url"],
                "receipt_id": stored["receipt"]["receipt_id"],
                "counts": {
                    "genes": paste_counts["genes"],
                    "drivers": paste_counts["drivers"],
                    "passengers": paste_counts["passengers"],
                    "contradicted": paste_counts["contradicted"],
                    "not_assayed": paste_counts["not_assayed"],
                },
                "command": "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
            },
        ],
        "ledger": {
            "submission_count": ledger["submission_count"],
            "typed_status_counts": ledger["typed_status_counts"],
            "recent": ledger["recent"][-5:],
        },
        "script": [
            "Open Check and start with the acceptance layer, not a standalone analysis.",
            "Show the real Claude Science signature entering as a proposal and getting typed driver, passenger, or not_assayed.",
            "Paste the demo genes and open the returned shareable result page.",
            "Show the 48 percent benchmark, then the MED12 correction that qualifies Prospect's own interpretation.",
            "Open the PGGT1B dossier and state the narrow falsifiable hypothesis.",
            "Open Receipts and close on receipt to proposal to human signature.",
        ],
    }


def _print_text(packet: dict[str, Any]) -> None:
    print("Prospect deterministic demo mode")
    print(f"accepted=false, next={packet['next']}")
    print(packet["ceiling"])
    print("")
    for index, beat in enumerate(packet["beats"], start=1):
        print(f"{index}. {beat['title']}")
        print(f"   status: {beat['status']}")
        if "counts" in beat:
            print(f"   counts: {beat['counts']}")
        if "proposal_url" in beat:
            print(f"   proposal_url: {beat['proposal_url']}")
        print(f"   command: {beat['command']}")
    print("")
    print(f"ledger submissions: {packet['ledger']['submission_count']}")
    print("Recording script:")
    for line in packet["script"]:
        print(f"- {line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect demo-mode")
    parser.add_argument("--json", action="store_true", help="emit the demo packet as JSON")
    parser.add_argument("--reset", action="store_true", help="clear prior demo proposals before writing the demo proposal")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args(argv)

    packet = build_demo_packet(data_dir=Path(args.data_dir), base_url=args.base_url, reset=args.reset)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        _print_text(packet)
    return 0


def reset_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect demo-reset")
    parser.add_argument("--json", action="store_true", help="emit reset result as JSON")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    args = parser.parse_args(argv)
    result = reset_demo_state(Path(args.data_dir))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Prospect demo state reset")
        print(f"removed_proposals={result['removed_proposals']}")
        print(f"database={result['database']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
