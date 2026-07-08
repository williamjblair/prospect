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
    campaign_review = frontier.get("agent_campaign_review") or {}
    campaign_probe = frontier.get("campaign_agent_probe") or {}
    campaign_triage = frontier.get("campaign_triage") or {}
    campaign_gate_probe = frontier.get("campaign_gate_probe") or {}
    campaign_pressure = frontier.get("campaign_pressure_summary") or {}
    lab_packet = frontier.get("lab_packet") or {}
    assay_operations = frontier.get("assay_operations_bundle") or {}
    transfer_replay = frontier.get("transfer_replay_packet") or {}
    substrate_replay = frontier.get("substrate_replay_packet") or {}
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
            "./prospect final-check",
            "./prospect submit-smoke",
            "./prospect submit-pack",
            "./prospect demo-pack",
            "./prospect verify",
            "python benchmark/mutation_pack.py",
            "python tests/test_skill_parity.py",
            "cd web && npm run build",
        ],
        "receipt_bridge_demo": {
            "command": "python examples/receipt_bridge_client.py",
            "json_command": "python examples/receipt_bridge_client.py --json",
            "transport": "MCP stdio",
            "tools": [
                "prospect.receipt.schema",
                "prospect.receipt.validate",
                "prospect.receipt.submit",
            ],
            "accepted": False,
            "next": "human_signature_required",
        },
        "demo_path": [
            "Overview: AI claim refusal and 48 percent overclaim rate",
            "Findings: five-row index, then evidence tables",
            "Frontier: signed root, contradictions, receipts, MCP bridge",
            "Agent: PGGT1B packet, campaign leaderboard, lab assay packet",
            "Agent: PGGT1B evidence capsule shows exact ratios, matrix slice, and missing acceptance evidence",
            "Agent: Gladstone assay operations bundle names promotion, weakening, and rejection evidence",
            "Agent: Claude probe compared with deterministic review lanes",
            "Agent: disagreement triage turns model pressure into assay gates",
            "Agent: gate probe checks whether gates are sufficient, need controls, or should be lower priority",
        ],
        "public_data": [
            "/data/frontier.json",
            "/data/judge_packet.json",
            "/data/finding_index.json",
            "/data/receipt_bridge/receipt_contract.json",
            "/data/receipt_bridge/receipt_manifest.json",
            "/data/receipt_bridge/receipt_bundle.json",
            "/data/pggt1b_deep_dive.json",
            "/data/pggt1b_matrix_slice.json",
            "/data/agent_campaign.json",
            "/data/agent_campaign_review.json",
            "/data/campaign_agent_probe.json",
            "/data/campaign_triage.json",
            "/data/campaign_gate_probe.json",
            "/data/campaign_pressure_summary.json",
            "/data/transfer_replay_packet.json",
            "/data/substrate_replay_packet.json",
            "/data/lab_packet.json",
            "/data/assay_operations_bundle.json",
        ],
        "artifact_counts": {
            "genes": frontier["stats"]["n_genes"],
            "edges": frontier["stats"]["n_edges"],
            "findings": len(frontier["findings"]),
            "finding_index_items": len(finding_index["items"]),
            "receipts": bridge["receipt_count"],
            "agent_campaign_candidates": len(campaign["candidates"]),
            "campaign_review_rows": len(campaign_review.get("rows", [])),
            "campaign_probe_rows": len(campaign_probe.get("rows", [])),
            "campaign_triage_rows": len(campaign_triage.get("rows", [])),
            "campaign_gate_probe_rows": len(campaign_gate_probe.get("rows", [])),
            "campaign_pressure_rows": len(campaign_pressure.get("pressure_accounting", [])),
            "transfer_replay_rows": transfer_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
            "substrate_replay_rows": substrate_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
            "validation_candidates": len(validation) or _csv_count(DATA / "validation_candidates.csv"),
            "lab_packet_candidates": len(lab_packet.get("candidates", [])),
            "assay_operations_candidates": len(assay_operations.get("candidates", [])),
            "pggt1b_evidence_ladder_steps": len(pggt1b.get("evidence_capsule", {}).get("evidence_ladder", [])),
            "pggt1b_matrix_slice_transcripts": pggt1b.get("matrix_slice", {}).get("n_thresholded_transcripts", 0),
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
                "matrix_slice_transcripts": pggt1b.get("matrix_slice", {}).get("n_thresholded_transcripts", 0),
            },
            "pggt1b_deep_dive": pggt1b,
            "campaign": {
                "status": campaign["status"],
                "trust_boundary": campaign["trust_boundary"],
                "top_gene": campaign["candidates"][0]["gene"],
                "candidate_count": len(campaign["candidates"]),
                "review_rows": len(campaign_review.get("rows", [])),
                "probe_rows": len(campaign_probe.get("rows", [])),
                "triage_rows": len(campaign_triage.get("rows", [])),
            },
            "campaign_probe": {
                "status": campaign_probe.get("status"),
                "trust_boundary": campaign_probe.get("trust_boundary"),
                "candidate_count": len(campaign_probe.get("rows", [])),
                "summary": campaign_probe.get("summary", {}),
            },
            "campaign_triage": {
                "status": campaign_triage.get("status"),
                "trust_boundary": campaign_triage.get("trust_boundary"),
                "candidate_count": len(campaign_triage.get("rows", [])),
                "summary": campaign_triage.get("summary", {}),
            },
            "campaign_gate_probe": {
                "status": campaign_gate_probe.get("status"),
                "trust_boundary": campaign_gate_probe.get("trust_boundary"),
                "candidate_count": len(campaign_gate_probe.get("rows", [])),
                "summary": campaign_gate_probe.get("summary", {}),
            },
            "campaign_pressure_summary": {
                "status": campaign_pressure.get("status"),
                "trust_boundary": campaign_pressure.get("trust_boundary"),
                "accepted_state_mutations": campaign_pressure.get("accepted_state_mutations"),
                "claude_probe_rows": campaign_pressure.get("counts", {}).get("claude_probe_rows", 0),
                "triage_rows": campaign_pressure.get("counts", {}).get("triage_rows", 0),
                "gate_recommendations": campaign_pressure.get("gate_recommendations", {}),
            },
            "transfer_replay": {
                "status": transfer_replay.get("status"),
                "trust_boundary": transfer_replay.get("trust_boundary"),
                "accepted_state_mutation": transfer_replay.get("accepted_state_mutation"),
                "t_cell_regulators_compared": transfer_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
                "activation_specificity_rate": transfer_replay.get("rates", {}).get("activation_specificity", {}).get("rate"),
            },
            "substrate_replay": {
                "status": substrate_replay.get("status"),
                "trust_boundary": substrate_replay.get("trust_boundary"),
                "accepted_state_mutation": substrate_replay.get("accepted_state_mutation"),
                "t_cell_regulators_compared": substrate_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
                "substrate_count": len(substrate_replay.get("datasets", [])),
            },
            "lab_packet": {
                "status": lab_packet.get("status"),
                "trust_boundary": lab_packet.get("trust_boundary"),
                "candidate_count": len(lab_packet.get("candidates", [])),
            },
            "assay_operations_bundle": {
                "status": assay_operations.get("status"),
                "trust_boundary": assay_operations.get("trust_boundary"),
                "accepted_state_mutations": assay_operations.get("accepted_state_mutations"),
                "candidate_count": len(assay_operations.get("candidates", [])),
                "top_gene": (assay_operations.get("candidates") or [{}])[0].get("gene"),
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
        f"- Campaign review rows: {counts['campaign_review_rows']}",
        f"- Campaign probe rows: {counts['campaign_probe_rows']}",
        f"- Campaign triage rows: {counts['campaign_triage_rows']}",
        f"- Campaign gate probe rows: {counts['campaign_gate_probe_rows']}",
        f"- Campaign pressure rows: {counts['campaign_pressure_rows']}",
        f"- Transfer replay rows: {counts['transfer_replay_rows']}",
        f"- Substrate replay rows: {counts['substrate_replay_rows']}",
        f"- Validation candidates: {counts['validation_candidates']}",
        f"- Lab packet candidates: {counts['lab_packet_candidates']}",
        f"- Assay operations candidates: {counts['assay_operations_candidates']}",
        f"- PGGT1B evidence ladder steps: {counts['pggt1b_evidence_ladder_steps']}",
        f"- PGGT1B matrix-slice transcripts: {counts['pggt1b_matrix_slice_transcripts']}",
        "",
        "## PGGT1B evidence capsule",
        "",
        "The top agent hypothesis has an evidence capsule with exact ratios, a released-matrix moved-transcript slice, assay gates, and missing evidence. Status remains `evidence_attached`.",
        "",
        "## Gladstone assay operations bundle",
        "",
        "The operations bundle turns the top five proposal-only assay rows into explicit expected positive, weakening, and rejection evidence before any accepted state can move.",
        "",
        "## Campaign gate probe",
        "",
        "The gate probe pressure-tests the disagreement triage rows with closed recommendations: `gate_sufficient`, `add_control`, or `lower_priority`. It stays proposal only.",
        "",
        "## Campaign pressure summary",
        "",
        "The pressure summary accounts for what Claude changed, what Prospect refused to change, and which assay gates remain before any accepted state can move.",
        "",
        "## Transfer replay packet",
        "",
        "The transfer packet replays the signed cross-cell-type finding through the Marson and Replogle checkers, without changing accepted state.",
        "",
        "## Substrate replay packet",
        "",
        "The substrate packet makes the protocol-generalization claim explicit: one checker contract, three frozen substrates, typed status, and no accepted-state mutation.",
        "",
        "## Receipt bridge demo",
        "",
        "Run the external MCP client:",
        "",
        "```bash",
        packet["receipt_bridge_demo"]["command"],
        "```",
        "",
        "It starts `./prospect mcp`, discovers the receipt tools, validates a receipt, and submits it as a proposal. The expected result includes `accepted=false` and `next=human_signature_required`.",
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
