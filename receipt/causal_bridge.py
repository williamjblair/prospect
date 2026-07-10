"""Typed causal verdicts for external activity entering Prospect.

The bridge compares an external gene-list claim against the frozen Marson
Perturb-seq table. It never calls a model and never mutates accepted state.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from receipt.schema import Artifact, EvidenceAtom, Receipt, Verifier
from receipt.substrate_router import choose_route, coverage_report, enrich_verdicts

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
CLAUDE_EXPORT = DATA / "claude_science_real_export"
CLAUDE_CONNECTOR_RUN = DATA / "claude_science_connector_run.json"
MARSON_FULL = DATA / "marson_de_full.csv"

CAUSAL_RULE = {
    "claim_under_test": "Which genes in the associative Claude Science response signature behave as causal regulators of the CD4+ activation program?",
    "comparison": "driver_vs_passenger",
    "condition_rule": "strongest on-target effect across Rest, Stim8hr, and Stim48hr",
    "evidence_attached": "on-target knockdown in any Marson condition and more than 10 DE genes in the strongest condition",
    "associative_only": "on-target knockdown in at least one Marson condition but 10 or fewer DE genes in the strongest condition, with no explicit causal driver claim",
    "contradicted": "an explicit causal or driver claim exists, and on-target knockdown moves 10 or fewer genes in the strongest condition",
    "not_assayed": "absent from the Marson table or no on-target knockdown in any Marson condition",
}

CLAIM_MODES = {"associative_signature", "explicit_driver_claim"}

CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _marson_rows(path: Path = MARSON_FULL) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            rows[(row["target_contrast_gene_name"], row["culture_condition"])] = row
    return rows


def _de_lookup(path: Path) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    if not path.exists():
        return lookup
    with path.open(newline="") as f:
        for idx, row in enumerate(csv.DictReader(f), start=1):
            gene = row.get("gene", "")
            if gene and gene not in lookup:
                row = dict(row)
                row["rank"] = str(idx)
                lookup[gene] = row
    return lookup


def _transcripts(n: int) -> str:
    return "1 transcript" if n == 1 else f"{n} transcripts"


def signature_genes(signature: dict[str, Any]) -> list[dict[str, str]]:
    roles: dict[str, list[str]] = defaultdict(list)
    for role, value in signature.items():
        if role == "AUC" or not isinstance(value, list):
            continue
        for gene in value:
            if isinstance(gene, str):
                roles[gene].append(role)
    return [{"gene": gene, "roles": roles[gene]} for gene in sorted(roles)]


def causal_verdicts(
    genes: list[dict[str, Any]] | list[str],
    *,
    marson_path: Path = MARSON_FULL,
    de_table_path: Path | None = None,
    claim_mode: str = "associative_signature",
    claim_source: str = "",
    comparable_readout: bool = True,
    comparability_status: str | None = None,
) -> list[dict[str, Any]]:
    if claim_mode not in CLAIM_MODES:
        raise ValueError(f"claim_mode must be one of {sorted(CLAIM_MODES)}")
    comparability = comparability_status or ("comparable" if comparable_readout else "orthogonal_phenotype")
    if comparability not in {"comparable", "orthogonal_phenotype", "not_declared"}:
        raise ValueError("comparability_status must be comparable, orthogonal_phenotype, or not_declared")
    rows = _marson_rows(marson_path)
    de = _de_lookup(de_table_path) if de_table_path else {}
    verdicts: list[dict[str, Any]] = []
    for item in genes:
        if isinstance(item, str):
            gene = item
            roles: list[str] = []
        else:
            gene = str(item.get("gene", ""))
            roles = [str(role) for role in item.get("roles", [])]
        condition_rows = [rows[(gene, cond)] for cond in CONDITIONS if (gene, cond) in rows]
        on_target_rows = [row for row in condition_rows if row["ontarget_effect_category"] == "on-target KD"]
        row = max(on_target_rows, key=lambda r: int(r["n_total_de_genes"])) if on_target_rows else None
        explicit_driver_claim = claim_source if claim_mode == "explicit_driver_claim" else ""
        if row is None:
            typed_status = "not_assayed"
            if condition_rows:
                reason = f"{gene} lacks on-target knockdown in all Marson conditions, so Prospect does not type it as a driver or passenger."
            else:
                reason = f"{gene} is absent from the frozen Marson table."
            n_de = None
            condition = ""
            ontarget = "not_found" if not condition_rows else "no on-target KD"
        else:
            n_de = int(row["n_total_de_genes"])
            ontarget = row["ontarget_effect_category"]
            condition = row["culture_condition"]
            if n_de > 10:
                typed_status = "evidence_attached"
                reason = f"{gene} has on-target knockdown and moves {_transcripts(n_de)} in {condition}, so Prospect types it as a candidate driver."
            elif explicit_driver_claim and comparable_readout:
                typed_status = "contradicted"
                reason = f"{gene} has an explicit driver claim, but on-target knockdown moves only {_transcripts(n_de)} at strongest effect in {condition}."
            else:
                typed_status = "associative_only"
                if explicit_driver_claim:
                    reason = f"{gene} has an explicit claim with a non-comparable phenotype, so Prospect keeps the result associative_only rather than contradicted."
                else:
                    reason = f"{gene} is in the associative signature, but on-target knockdown moves only {_transcripts(n_de)} at strongest effect in {condition}."
        de_row = de.get(gene, {})
        verdicts.append({
            "gene": gene,
            "signature_roles": roles,
            "typed_status": typed_status,
            "driver_claim": explicit_driver_claim,
            "claim_mode": claim_mode,
            "comparability": comparability,
            "condition": condition,
            "n_total_de_genes": n_de,
            "ontarget_effect_category": ontarget,
            "de_rank": int(de_row["rank"]) if de_row.get("rank") else None,
            "signature_diff_R_minus_NR": float(de_row["diff_R_minus_NR"]) if de_row.get("diff_R_minus_NR") else None,
            "signature_padj": float(de_row["padj"]) if de_row.get("padj") else None,
            "reason": reason,
        })
    return sorted(
        verdicts,
        key=lambda v: (
            {"evidence_attached": 0, "contradicted": 1, "associative_only": 2, "not_assayed": 3}.get(v["typed_status"], 9),
            -(v["n_total_de_genes"] or 0),
            v["gene"],
        ),
    )


def verdict_counts(verdicts: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(v["typed_status"] for v in verdicts)
    return {
        "genes": len(verdicts),
        "drivers": counts.get("evidence_attached", 0),
        "evidence_attached": counts.get("evidence_attached", 0),
        "passengers": counts.get("associative_only", 0),
        "associative_only": counts.get("associative_only", 0),
        "contradicted": counts.get("contradicted", 0),
        "not_assayed": counts.get("not_assayed", 0),
    }


def _receipt_from_verdicts(
    *,
    producer: dict[str, Any],
    claim: str,
    artifacts: list[dict[str, str]],
    verdicts: list[dict[str, Any]],
    replay: str,
    frontier: str = "prospect_marson_cd4_perturbseq",
    source_label: str = "Marson frozen table",
    conditions: list[str] | None = None,
    rule: dict[str, Any] | None = None,
    request_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts = verdict_counts(verdicts)
    if counts["evidence_attached"] or counts["associative_only"]:
        status = "evidence_attached"
    elif counts["contradicted"]:
        status = "contradicted"
    else:
        status = "claimed"
    receipt = Receipt(
        frontier=frontier,
        claim=claim,
        kind="external_causal_review",
        subject=[v["gene"] for v in verdicts],
        producer=producer,
        artifacts=[Artifact(**a) for a in artifacts],
        evidence=[
            EvidenceAtom("signature genes typed as candidate drivers", str(counts["drivers"]), source_label),
            EvidenceAtom("signature genes typed as associative passengers", str(counts["passengers"]), source_label),
            EvidenceAtom("explicit driver claims contradicted", str(counts["contradicted"]), source_label),
            EvidenceAtom("genes not assayed comparably", str(counts["not_assayed"]), source_label),
        ],
        verifier=Verifier(
            name="ProspectCausalReceiptBridge",
            method="frozen lookup over the strongest Marson on-target condition and DE count",
            replay=replay,
        ),
        status=status,
        replayability="exact",
        conditions=conditions or ["Rest", "Stim8hr", "Stim48hr", "released Marson DE table", "proposal only"],
        verification_requirements=[
            "frozen_replay_passes",
            "reviewer_accepts_state_delta",
            "human_ed25519_signature",
        ],
        state_diff={
            "accepted": False,
            "model_can_apply": False,
            "effect": "proposal_only_no_state_mutation",
            "target": frontier,
        },
        replay_metadata={
            "command": replay,
            "verifier": "ProspectCausalReceiptBridge",
            "replayability": "exact",
            "frontier": frontier,
            "rule": rule or CAUSAL_RULE,
            "request": request_metadata or {},
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        },
        verdicts=verdicts,
    ).freeze()
    return receipt.to_dict()


def claude_science_submission_request() -> dict[str, Any]:
    signature_path = CLAUDE_EXPORT / "signature_genes.json"
    provenance = _read_json(CLAUDE_EXPORT / "provenance.json")
    artifacts = [
        {
            "name": row["name"],
            "sha256": row["sha256"],
            "locator": f"examples/data/claude_science_real_export/{row['name']}",
        }
        for row in provenance["artifacts"]
    ]
    artifacts.append({
        "name": "provenance.json",
        "sha256": sha256_file(CLAUDE_EXPORT / "provenance.json"),
        "locator": "examples/data/claude_science_real_export/provenance.json",
    })
    return {
        "input_text": signature_path.read_text(),
        "filename": signature_path.name,
        "producer": {
            "kind": "external_workbench",
            "name": "Claude Science",
            "run": "sade_feldman_signature_export",
            "real_export": True,
        },
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "citations": ["GSE120575", "Sade-Feldman et al. 2018"],
        "artifacts": artifacts,
        "publish_to_ledger": False,
    }


def build_claude_science_packet() -> dict[str, Any]:
    from receipt.acceptance_service import evaluate_submission

    provenance = _read_json(CLAUDE_EXPORT / "provenance.json")
    signature = _read_json(CLAUDE_EXPORT / "signature_genes.json")
    connector_run = _read_json(CLAUDE_CONNECTOR_RUN)
    connector_response = connector_run["response"]
    canonical = evaluate_submission(claude_science_submission_request())
    receipt = canonical["receipt"]
    return {
        "demo_id": "claude_science_acceptance_layer",
        "producer": "claude_science",
        "source_dataset": "Sade-Feldman 2018 melanoma ICB scRNA-seq, GSE120575",
        "real_export": True,
        "accepted": False,
        "next": "human_signature_required",
        "proposal_id": canonical["proposal_id"],
        "claim_under_test": canonical["claim_under_test"],
        "causal_rule": receipt["replay_metadata"]["rule"],
        "claude_science": {
            "artifact_status": "reproducible_export",
            "internal_review_status": provenance["claude_science_internal_review"]["status"],
            "internal_review_findings": provenance["claude_science_internal_review"]["findings"],
            "session_caveat": provenance["session_caveat"],
            "auc": signature.get("AUC", {}),
        },
        "live_connector": {
            "capture_id": connector_run["capture_id"],
            "originating_claude_science_ui_call": connector_run["originating_claude_science_ui_call"],
            "reviewer_result": connector_run["reviewer"]["result"],
            "proposal_id": connector_response["proposal_id"],
            "proposal_url": connector_response["proposal_url"],
            "receipt_id": connector_response["receipt"]["receipt_id"],
            "evidence_mode": connector_response["evidence_mode"],
            "consulted_substrate_count": len(connector_response["consulted_substrates"]),
            "accepted": connector_response["accepted"],
            "next": connector_response["next"],
            "incremental_cost_usd": connector_run["api_budget"]["incremental_cost_usd"],
            "api_cap_usd": connector_run["api_budget"]["cap_usd"],
        },
        "prospect": {
            **canonical["prospect"],
            "proposal_id": canonical["proposal_id"],
            "interpretation": "Prospect separates candidate causal drivers from associative passengers. It does not say the response signature is wrong.",
        },
        "artifacts": receipt["artifacts"],
        "verdicts": canonical["verdicts"],
        "receipt": receipt,
        "commands": {
            "claude_science": "python examples/claude_science_connector_client.py --json",
            "generic": "python examples/prospect_connector_client.py --case openresearch --json",
            "server": "./prospect mcp",
        },
    }


def build_openresearch_packet() -> dict[str, Any]:
    gene = "VAV1"
    verdicts = causal_verdicts([{"gene": gene, "roles": ["external_reproduction_claim"]}])
    artifacts = [
        {
            "name": "marson_de_full.csv",
            "sha256": sha256_file(MARSON_FULL),
            "locator": "examples/data/marson_de_full.csv",
        }
    ]
    claim = "External producer proposes VAV1 as a causal regulator of the stimulated CD4+ activation program."
    receipt = _receipt_from_verdicts(
        producer={
            "kind": "external_workbench",
            "name": "OpenResearch style bundle",
            "run": "generic_external_claim_demo",
            "real_export": False,
        },
        claim=claim,
        artifacts=artifacts,
        verdicts=verdicts,
        replay="python examples/prospect_connector_client.py --case openresearch --json",
    )
    return {
        "demo_id": "generic_external_producer",
        "producer": "openresearch_style_bundle",
        "claim_under_test": claim,
        "prospect": {
            "accepted": False,
            "next": "human_signature_required",
            "typed_status_counts": verdict_counts(verdicts),
            "receipt_id": receipt["receipt_id"],
        },
        "verdicts": verdicts,
        "receipt": receipt,
    }


def submit_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    case = bundle.get("case", "")
    if isinstance(bundle.get("text"), str):
        from receipt.acceptance_service import evaluate_submission

        packet = evaluate_submission({
            "input_text": bundle["text"],
            "filename": str(bundle.get("filename") or "submission.txt"),
            "producer": bundle.get("producer") or bundle.get("source_name") or "generic_external",
            "substrate_id": bundle.get("substrate_id") or "marson_cd4_activation",
            "claim_mode": bundle.get("claim_mode") or "associative_signature",
            "claim_context": bundle.get("claim_context") or {},
            "evidence_mode": bundle.get("evidence_mode") or "primary_only",
            "citations": bundle.get("citations") or [],
            "artifacts": bundle.get("artifacts") or [],
            "publish_to_ledger": bool(bundle.get("publish_to_ledger", False)),
        })
    elif case == "claude_science":
        packet = build_claude_science_packet()
    elif case == "openresearch":
        packet = build_openresearch_packet()
    else:
        genes = bundle.get("genes")
        if not isinstance(genes, list) or not genes:
            raise ValueError("bundle must include case=claude_science, case=openresearch, or a non-empty genes list")
        verdicts = causal_verdicts(genes)
        claim = str(bundle.get("claim") or CAUSAL_RULE["claim_under_test"])
        artifacts = [
            {
                "name": "marson_de_full.csv",
                "sha256": sha256_file(MARSON_FULL),
                "locator": "examples/data/marson_de_full.csv",
            }
        ]
        receipt = _receipt_from_verdicts(
            producer=dict(bundle.get("producer") or {"kind": "external_workbench", "name": "generic"}),
            claim=claim,
            artifacts=artifacts,
            verdicts=verdicts,
            replay=str(bundle.get("replay") or "./prospect mcp"),
        )
        packet = {
            "demo_id": "generic_gene_list",
            "producer": (bundle.get("producer") or {}).get("name", "generic"),
            "claim_under_test": claim,
            "prospect": {
                "accepted": False,
                "next": "human_signature_required",
                "typed_status_counts": verdict_counts(verdicts),
                "receipt_id": receipt["receipt_id"],
            },
            "verdicts": verdicts,
            "receipt": receipt,
        }
    packet["accepted"] = False
    packet["next"] = "human_signature_required"
    return packet


def write_claude_science_packet(path: Path | None = None) -> dict[str, Any]:
    packet = build_claude_science_packet()
    out = path or DATA / "claude_science_acceptance_demo.json"
    out.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    return packet
