"""Build the defended-discovery candidate decision ledger."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
PREREG_JSON = DATA / "defended_discovery_preregistration.json"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
PGGT1B_JSON = DATA / "pggt1b_defended_evidence.json"
OUT_JSON = DATA / "defended_candidate_decisions.json"
OUT_DOC = ROOT / "docs" / "DEFENDED_CANDIDATE_DECISIONS.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required frozen source: {path}")
    return json.loads(path.read_text())


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _kill_results(packet: dict[str, Any]) -> dict[str, str]:
    return {row["kill_id"]: row["result"] for row in packet["kill_attempts"]}


def _next_candidate(discovery: dict[str, Any], decided_ranks: set[int]) -> dict[str, Any] | None:
    for row in discovery["candidates"]:
        if row["rank"] not in decided_ranks:
            return {
                "rank": row["rank"],
                "gene": row["gene"],
                "status": "pending_deep_dive",
                "required_next_packet": f"rank_{row['rank']}_{row['gene'].lower()}_defended_evidence",
            }
    return None


def build_defended_candidate_decisions() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    discovery = _load(DISCOVERY_JSON)
    pggt1b = _load(PGGT1B_JSON)
    pggt1b_decision = {
        "rank": pggt1b["candidate_rank"],
        "gene": pggt1b["gene"],
        "typed_status": "evidence_attached",
        "decision": "not_cleared_full_bar",
        "disposition": "demote_and_advance",
        "evidence_packet": "examples/data/pggt1b_defended_evidence.json",
        "evidence_packet_id": pggt1b["packet_id"],
        "scored_public_dataset_count": pggt1b["orthogonal_public_dataset_count"],
        "missing_required_rung": (
            "comparable activation-transcriptome or activation-marker primary T-cell screen"
        ),
        "why_not_contradicted": (
            "the frozen comparators do not refute PGGT1B; they fail to supply the required comparable replication rung"
        ),
        "kill_results": _kill_results(pggt1b),
        "decision_rule": (
            "advance when a candidate does not clear every pre-registered rung; do not rewrite the bar"
        ),
    }
    decided_ranks = {pggt1b_decision["rank"]}
    next_candidate = _next_candidate(discovery, decided_ranks)
    packet = {
        "phase": "defended_candidate_decision_ledger",
        "title": "Defended candidate decision ledger",
        "status": "evidence_attached",
        "accepted": False,
        "acceptance": False,
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": prereg["pre_registration_id"],
        "candidate_set_id": discovery["candidate_set_id"],
        "campaign_state": "continue_ranked_list" if next_candidate else "exhausted_ranked_list",
        "completion_status": "not_complete",
        "decided_count": len(decided_ranks),
        "remaining_candidate_count": discovery["candidate_count"] - len(decided_ranks),
        "candidate_decisions": [pggt1b_decision],
        "next_candidate": next_candidate,
        "reproduce_command": "./prospect defended-candidate-decisions",
        "next_step": (
            "build the rank-2 defended evidence packet, starting from the same frozen bar and kill rules"
        ),
    }
    packet["packet_id"] = _hash_obj("defended_decisions", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Defended candidate decisions",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        f"Campaign state: `{packet['campaign_state']}`.",
        f"Completion status: `{packet['completion_status']}`.",
        "",
        "## Decisions",
        "",
        "| rank | gene | decision | disposition | missing required rung |",
        "|---:|---|---|---|---|",
    ]
    for row in packet["candidate_decisions"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | not cleared full bar | demote and advance | "
            f"{row['missing_required_rung']} |"
        )
    lines += [
        "",
        "PGGT1B is not contradicted by this ledger. It is below the full defended-discovery bar because the frozen comparators do not supply the required comparable replication rung.",
        "",
        "## Next candidate",
        "",
    ]
    if packet["next_candidate"]:
        next_candidate = packet["next_candidate"]
        lines.append(
            f"Rank {next_candidate['rank']}: {next_candidate['gene']} "
            f"with required packet `{next_candidate['required_next_packet']}`."
        )
    else:
        lines.append("No ranked candidate remains.")
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect defended-candidate-decisions",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_defended_candidate_decisions(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_defended_candidate_decisions()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_defended_candidate_decisions()
    print(f"wrote {OUT_JSON} ({packet['campaign_state']})")
    print(f"wrote {OUT_DOC}")
    print(f"packet_id {packet['packet_id']}")


if __name__ == "__main__":
    main()
