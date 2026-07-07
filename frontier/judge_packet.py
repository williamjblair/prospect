"""Build the Prospect judge packet from committed replay artifacts."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
WEB_DATA = ROOT / "web" / "public" / "data"
OUT_JSON = DATA / "judge_packet.json"
OUT_DOC = ROOT / "docs" / "JUDGE_PACKET.md"

LIVE_URL = "https://prospect-sepia-six.vercel.app"
REPO_URL = "https://github.com/williamjblair/prospect"


def _json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing artifact: {path}")
    return json.loads(path.read_text())


def _csv_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as fh:
        return sum(1 for _ in csv.DictReader(fh))


def build_packet() -> dict[str, Any]:
    frontier = _json(WEB_DATA / "frontier.json")
    bridge = frontier["receipt_bridge"]
    finding_index = frontier["finding_index"]
    campaign = frontier["agent_campaign"]
    lab_packet = frontier.get("lab_packet") or {}
    pggt1b = frontier["pggt1b_deep_dive"]
    validation = frontier.get("validation") or []

    return {
        "title": "Prospect judge packet",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "frontier_root": frontier["frontier"]["root"],
        "signer": frontier["frontier"]["signer"],
        "trust_boundary": {
            "model_role": "propose_search_draft",
            "gate": "frozen_code_over_frozen_released_table",
            "acceptance": "human_ed25519_key",
            "model_moves_accepted_state": False,
            "receipt_submission": "proposal_only",
        },
        "typed_statuses": ["computationally_reproduced", "evidence_attached", "contradicted"],
        "gate_commands": [
            "./prospect verify",
            "python benchmark/mutation_pack.py",
            "python tests/test_skill_parity.py",
            "cd web && npm run build",
        ],
        "demo_path": [
            "Overview: AI claim refusal and 48 percent overclaim rate",
            "Findings: five-row index, then evidence tables",
            "Frontier: signed root, contradictions, receipts, MCP bridge",
            "Agent: PGGT1B packet, campaign leaderboard, lab assay packet",
        ],
        "public_data": [
            "/data/frontier.json",
            "/data/finding_index.json",
            "/data/receipt_bridge/receipt_contract.json",
            "/data/receipt_bridge/receipt_bundle.json",
            "/data/pggt1b_deep_dive.json",
            "/data/agent_campaign.json",
            "/data/lab_packet.json",
        ],
        "artifact_counts": {
            "genes": frontier["stats"]["n_genes"],
            "edges": frontier["stats"]["n_edges"],
            "findings": len(frontier["findings"]),
            "finding_index_items": len(finding_index["items"]),
            "receipts": bridge["receipt_count"],
            "agent_campaign_candidates": len(campaign["candidates"]),
            "validation_candidates": len(validation) or _csv_count(DATA / "validation_candidates.csv"),
            "lab_packet_candidates": len(lab_packet.get("candidates", [])),
        },
        "science_packet": {
            "finding_index": {
                "status": finding_index["status"],
                "items": [{"kind": item["kind"], "n_genes": item["n_genes"], "cid": item["cid"]}
                          for item in finding_index["items"]],
            },
            "pggt1b": {
                "status": pggt1b["status"],
                "gene": pggt1b["gene"],
                "stim8hr_de": pggt1b["facts"]["stim8hr_de"],
                "rest_de": pggt1b["facts"]["rest_de"],
                "k562_de": pggt1b["facts"]["k562_de"],
                "collectri_targets": pggt1b["facts"]["collectri_targets"],
            },
            "campaign": {
                "status": campaign["status"],
                "trust_boundary": campaign["trust_boundary"],
                "top_gene": campaign["candidates"][0]["gene"],
                "candidate_count": len(campaign["candidates"]),
            },
            "lab_packet": {
                "status": lab_packet.get("status"),
                "trust_boundary": lab_packet.get("trust_boundary"),
                "candidate_count": len(lab_packet.get("candidates", [])),
            },
        },
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["artifact_counts"]
    lines = [
        "# Judge packet",
        "",
        f"Live: [{packet['live_url']}]({packet['live_url']})",
        "",
        f"Repo: [{packet['repo_url']}]({packet['repo_url']})",
        "",
        f"Signed root: `{packet['frontier_root']}`",
        "",
        "## No model in the trust path",
        "",
        "A model proposes, searches, and drafts. Frozen code over a frozen released table gates the result. A human Ed25519 key accepts. Receipt submission is proposal only.",
        "",
        "## Replay gate",
        "",
        "```bash",
    ]
    lines += packet["gate_commands"]
    lines += [
        "```",
        "",
        "## Artifact counts",
        "",
        f"- Genes mapped: {counts['genes']}",
        f"- Regulatory edges: {counts['edges']}",
        f"- Findings: {counts['findings']}",
        f"- Receipts: {counts['receipts']}",
        f"- Campaign candidates: {counts['agent_campaign_candidates']}",
        f"- Validation candidates: {counts['validation_candidates']}",
        f"- Lab packet candidates: {counts['lab_packet_candidates']}",
        "",
        "## Public data",
        "",
    ]
    lines += [f"- `{path}`" for path in packet["public_data"]]
    lines += [
        "",
        "## Demo path",
        "",
    ]
    lines += [f"- {beat}" for beat in packet["demo_path"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/judge_packet.py",
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


def main() -> None:
    packet = write_packet()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"root {packet['frontier_root']}")


if __name__ == "__main__":
    main()
