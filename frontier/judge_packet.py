"""Build the Prospect judge packet from committed replay artifacts."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

from cli.submit_pack import PUBLIC_ARTIFACTS

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
    campaign_probe_audit = frontier.get("campaign_probe_audit") or {}
    campaign_triage = frontier.get("campaign_triage") or {}
    campaign_gate_probe = frontier.get("campaign_gate_probe") or {}
    campaign_pressure = frontier.get("campaign_pressure_summary") or {}
    campaign_challenger = frontier.get("campaign_challenger_ledger") or {}
    lab_packet = frontier.get("lab_packet") or {}
    assay_operations = frontier.get("assay_operations_bundle") or {}
    pilot_design = frontier.get("gladstone_pilot_design") or {}
    final_submission_audit = frontier.get("final_submission_audit") or {}
    transfer_replay = frontier.get("transfer_replay_packet") or {}
    substrate_replay = frontier.get("substrate_replay_packet") or {}
    cross_substrate_discovery = frontier.get("cross_substrate_discovery") or {}
    donor_condition_replay = frontier.get("donor_condition_replay") or {}
    disease_genetics_overlay = frontier.get("disease_genetics_overlay") or {}
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
            "./prospect release-manifest",
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
            "Agent: challenger ledger reconciles shipped packets and challenges one primary assay row",
        ],
        "public_data": PUBLIC_ARTIFACTS,
        "artifact_counts": {
            "genes": frontier["stats"]["n_genes"],
            "edges": frontier["stats"]["n_edges"],
            "findings": len(frontier["findings"]),
            "finding_index_items": len(finding_index["items"]),
            "receipts": bridge["receipt_count"],
            "agent_campaign_candidates": len(campaign["candidates"]),
            "campaign_review_rows": len(campaign_review.get("rows", [])),
            "campaign_probe_rows": len(campaign_probe.get("rows", [])),
            "campaign_probe_audit_issues": campaign_probe_audit.get("issue_count", 0),
            "campaign_triage_rows": len(campaign_triage.get("rows", [])),
            "campaign_gate_probe_rows": len(campaign_gate_probe.get("rows", [])),
            "campaign_pressure_rows": len(campaign_pressure.get("pressure_accounting", [])),
            "campaign_challenger_rows": len(campaign_challenger.get("rows", [])),
            "campaign_challenger_primary_challenges": campaign_challenger.get("counts", {}).get("primary_panel_challenges", 0),
            "campaign_challenger_replacements": len(campaign_challenger.get("panel_delta", {}).get("add", [])),
            "transfer_replay_rows": transfer_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
            "substrate_replay_rows": substrate_replay.get("counts", {}).get("t_cell_regulators_compared", 0),
            "cross_substrate_discovery_rows": cross_substrate_discovery.get("counts", {}).get("marson_genes_considered", 0),
            "cross_substrate_campaign_rows": len(cross_substrate_discovery.get("campaign_intersections", [])),
            "donor_condition_replay_rows": donor_condition_replay.get("counts", {}).get("campaign_rows", 0),
            "donor_supported_campaign_rows": donor_condition_replay.get("counts", {}).get("donor_supported", 0),
            "disease_genetics_overlay_rows": disease_genetics_overlay.get("counts", {}).get("campaign_rows", 0),
            "disease_genetics_context_rows": disease_genetics_overlay.get("counts", {}).get("immune_or_hematologic_context", 0),
            "disease_genetics_genetic_context_rows": disease_genetics_overlay.get("counts", {}).get("immune_or_hematologic_genetic_context", 0),
            "validation_candidates": len(validation) or _csv_count(DATA / "validation_candidates.csv"),
            "lab_packet_candidates": len(lab_packet.get("candidates", [])),
            "assay_operations_candidates": len(assay_operations.get("candidates", [])),
            "pilot_design_candidates": len(pilot_design.get("candidates", [])),
            "pilot_design_culture_arms": pilot_design.get("sample_plan", {}).get("culture_arms", 0),
            "final_submission_public_artifacts": len(PUBLIC_ARTIFACTS),
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
                "coverage": campaign_probe.get("coverage", {}),
                "summary": campaign_probe.get("summary", {}),
            },
            "campaign_probe_audit": {
                "status": campaign_probe_audit.get("status"),
                "trust_boundary": campaign_probe_audit.get("trust_boundary"),
                "passed": campaign_probe_audit.get("passed"),
                "issue_count": campaign_probe_audit.get("issue_count"),
                "promotion_rule": campaign_probe_audit.get("promotion_rule"),
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
                "coverage": campaign_gate_probe.get("coverage", {}),
                "summary": campaign_gate_probe.get("summary", {}),
            },
            "campaign_pressure_summary": {
                "status": campaign_pressure.get("status"),
                "trust_boundary": campaign_pressure.get("trust_boundary"),
                "accepted_state_mutations": campaign_pressure.get("accepted_state_mutations"),
                "claude_probe_rows": campaign_pressure.get("counts", {}).get("claude_probe_rows", 0),
                "triage_rows": campaign_pressure.get("counts", {}).get("triage_rows", 0),
                "gate_recommendations": campaign_pressure.get("gate_recommendations", {}),
                "gate_probe_coverage": campaign_pressure.get("gate_probe_coverage", {}),
            },
            "campaign_challenger_ledger": {
                "status": campaign_challenger.get("status"),
                "trust_boundary": campaign_challenger.get("trust_boundary"),
                "accepted_state_mutation": campaign_challenger.get("accepted_state_mutation"),
                "campaign_rows": campaign_challenger.get("counts", {}).get("campaign_rows", 0),
                "primary_panel_challenges": campaign_challenger.get("counts", {}).get("primary_panel_challenges", 0),
                "recommended_primary_panel": campaign_challenger.get("recommended_primary_panel", []),
                "panel_delta": campaign_challenger.get("panel_delta", {}),
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
            "cross_substrate_discovery": {
                "status": cross_substrate_discovery.get("status"),
                "trust_boundary": cross_substrate_discovery.get("trust_boundary"),
                "accepted_state_mutation": cross_substrate_discovery.get("accepted_state_mutation"),
                "marson_genes_considered": cross_substrate_discovery.get("counts", {}).get("marson_genes_considered", 0),
                "class_counts": cross_substrate_discovery.get("class_counts", {}),
                "top_campaign_gene": (cross_substrate_discovery.get("campaign_intersections") or [{}])[0].get("gene"),
            },
            "donor_condition_replay": {
                "status": donor_condition_replay.get("status"),
                "trust_boundary": donor_condition_replay.get("trust_boundary"),
                "accepted_state_mutation": donor_condition_replay.get("accepted_state_mutation"),
                "campaign_rows": donor_condition_replay.get("counts", {}).get("campaign_rows", 0),
                "donor_supported": donor_condition_replay.get("counts", {}).get("donor_supported", 0),
                "donor_fragile": donor_condition_replay.get("counts", {}).get("donor_fragile", 0),
                "top_gene": (donor_condition_replay.get("rows") or [{}])[0].get("gene"),
            },
            "disease_genetics_overlay": {
                "status": disease_genetics_overlay.get("status"),
                "local_perturbation_status": disease_genetics_overlay.get("local_perturbation_status"),
                "trust_boundary": disease_genetics_overlay.get("trust_boundary"),
                "accepted_state_mutation": disease_genetics_overlay.get("accepted_state_mutation"),
                "campaign_rows": disease_genetics_overlay.get("counts", {}).get("campaign_rows", 0),
                "context_rows": disease_genetics_overlay.get("counts", {}).get("immune_or_hematologic_context", 0),
                "genetic_context_rows": disease_genetics_overlay.get("counts", {}).get("immune_or_hematologic_genetic_context", 0),
                "top_gene": (disease_genetics_overlay.get("rows") or [{}])[0].get("gene"),
                "top_context": (disease_genetics_overlay.get("rows") or [{}])[0].get("top_context"),
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
            "pilot_design": {
                "status": pilot_design.get("status"),
                "trust_boundary": pilot_design.get("trust_boundary"),
                "accepted_state_mutations": pilot_design.get("accepted_state_mutations"),
                "candidate_count": len(pilot_design.get("candidates", [])),
                "culture_arms": pilot_design.get("sample_plan", {}).get("culture_arms"),
                "donor_replicates": pilot_design.get("sample_plan", {}).get("donor_replicates"),
            },
            "final_submission_audit": {
                "readiness": final_submission_audit.get("readiness"),
                "public_artifact_count": len(PUBLIC_ARTIFACTS),
                "human_only_actions": final_submission_audit.get("human_only_actions", []),
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
        f"- Campaign probe audit issues: {counts['campaign_probe_audit_issues']}",
        f"- Campaign triage rows: {counts['campaign_triage_rows']}",
        f"- Campaign gate probe rows: {counts['campaign_gate_probe_rows']}",
        f"- Campaign pressure rows: {counts['campaign_pressure_rows']}",
        f"- Campaign challenger rows: {counts['campaign_challenger_rows']}",
        f"- Campaign challenger primary challenges: {counts['campaign_challenger_primary_challenges']}",
        f"- Campaign challenger replacements: {counts['campaign_challenger_replacements']}",
        f"- Transfer replay rows: {counts['transfer_replay_rows']}",
        f"- Substrate replay rows: {counts['substrate_replay_rows']}",
        f"- Cross-substrate discovery rows: {counts['cross_substrate_discovery_rows']}",
        f"- Cross-substrate campaign rows: {counts['cross_substrate_campaign_rows']}",
        f"- Donor-condition replay rows: {counts['donor_condition_replay_rows']}",
        f"- Donor-supported campaign rows: {counts['donor_supported_campaign_rows']}",
        f"- Disease-genetics overlay rows: {counts['disease_genetics_overlay_rows']}",
        f"- Disease-context rows: {counts['disease_genetics_context_rows']}",
        f"- Disease-genetics context rows: {counts['disease_genetics_genetic_context_rows']}",
        f"- Validation candidates: {counts['validation_candidates']}",
        f"- Lab packet candidates: {counts['lab_packet_candidates']}",
        f"- Assay operations candidates: {counts['assay_operations_candidates']}",
        f"- Pilot design candidates: {counts['pilot_design_candidates']}",
        f"- Pilot design culture arms: {counts['pilot_design_culture_arms']}",
        f"- Final submission public artifacts: {counts['final_submission_public_artifacts']}",
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
        "## Gladstone pilot design",
        "",
        "The pilot design turns those rows into donor, condition, control, and culture-arm accounting for a proposal-only bench plan.",
        "",
        "## Final submission audit",
        "",
        "The final audit names shipped workstreams, required gates, public artifacts, trust boundary, and the human-only upload actions.",
        "",
        "## Campaign gate probe",
        "",
        "The gate probe pressure-tests the disagreement triage rows with closed recommendations: `gate_sufficient`, `add_control`, or `lower_priority`. It stays proposal only.",
        "",
        "## Campaign pressure summary",
        "",
        "The pressure summary accounts for what Claude changed, what Prospect refused to change, and which assay gates remain before any accepted state can move.",
        "",
        "## Campaign challenger ledger",
        "",
        "The challenger ledger joins shipped packets and challenges one current primary assay row. It recommends removing RWDD2B from the primary panel and adding CYB5RL, without changing accepted state.",
        "",
        "## Transfer replay packet",
        "",
        "The transfer packet replays the signed cross-cell-type finding through the Marson and Replogle checkers, without changing accepted state.",
        "",
        "## Substrate replay packet",
        "",
        "The substrate packet makes the protocol-generalization claim explicit: one checker contract, three frozen substrates, typed status, and no accepted-state mutation.",
        "",
        "## Cross-substrate discovery packet",
        "",
        "The discovery packet classifies every frozen Marson row against K562 and RPE1 count tables, then intersects the result with the proposal-only campaign leaderboard.",
        "",
        "## Donor-condition replay packet",
        "",
        "The donor packet replays released donor-correlation and guide-support fields for all 20 campaign strongest-condition rows.",
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
