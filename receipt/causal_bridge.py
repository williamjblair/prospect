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

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
CLAUDE_EXPORT = DATA / "claude_science_real_export"
MARSON_FULL = DATA / "marson_de_full.csv"

CAUSAL_RULE = {
    "claim_under_test": "Signature genes are causal regulators of the stimulated CD4+ activation program.",
    "condition": "Stim8hr",
    "evidence_attached": "on-target knockdown in Stim8hr and more than 10 DE genes",
    "contradicted": "on-target knockdown in Stim8hr and 10 or fewer DE genes",
    "not_assayed": "absent from the Marson table or no on-target knockdown in Stim8hr",
}


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
) -> list[dict[str, Any]]:
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
        row = rows.get((gene, CAUSAL_RULE["condition"]))
        if row is None:
            typed_status = "not_assayed"
            reason = f"{gene} is absent from the frozen Marson table for Stim8hr."
            n_de = None
            ontarget = "not_found"
        else:
            n_de = int(row["n_total_de_genes"])
            ontarget = row["ontarget_effect_category"]
            if ontarget != "on-target KD":
                typed_status = "not_assayed"
                reason = f"{gene} lacks on-target knockdown in Stim8hr, so Prospect does not call a causal contradiction."
            elif n_de > 10:
                typed_status = "evidence_attached"
                reason = f"{gene} has on-target knockdown and moves {n_de} transcripts in Stim8hr."
            else:
                typed_status = "contradicted"
                reason = f"{gene} has on-target knockdown but moves only {n_de} transcripts in Stim8hr."
        de_row = de.get(gene, {})
        verdicts.append({
            "gene": gene,
            "signature_roles": roles,
            "typed_status": typed_status,
            "condition": CAUSAL_RULE["condition"],
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
            {"evidence_attached": 0, "contradicted": 1, "not_assayed": 2}.get(v["typed_status"], 9),
            -(v["n_total_de_genes"] or 0),
            v["gene"],
        ),
    )


def verdict_counts(verdicts: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(v["typed_status"] for v in verdicts)
    return {
        "genes": len(verdicts),
        "evidence_attached": counts.get("evidence_attached", 0),
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
) -> dict[str, Any]:
    counts = verdict_counts(verdicts)
    status = "evidence_attached" if counts["evidence_attached"] else "contradicted"
    receipt = Receipt(
        frontier="prospect_marson_cd4_perturbseq",
        claim=claim,
        kind="external_causal_review",
        subject=[v["gene"] for v in verdicts],
        producer=producer,
        artifacts=[Artifact(**a) for a in artifacts],
        evidence=[
            EvidenceAtom("genes with causal support", str(counts["evidence_attached"]), "Marson Stim8hr frozen table"),
            EvidenceAtom("genes contradicted for causal-regulator claim", str(counts["contradicted"]), "Marson Stim8hr frozen table"),
            EvidenceAtom("genes not assayed comparably", str(counts["not_assayed"]), "Marson Stim8hr frozen table"),
        ],
        verifier=Verifier(
            name="ProspectCausalReceiptBridge",
            method="frozen lookup over Marson Stim8hr on-target knockdown and DE count",
            replay=replay,
        ),
        status=status,
        replayability="exact",
        conditions=["Stim8hr", "released Marson DE table", "proposal only"],
        verification_requirements=[
            "frozen_replay_passes",
            "reviewer_accepts_state_delta",
            "human_ed25519_signature",
        ],
        state_diff={
            "accepted": False,
            "model_can_apply": False,
            "effect": "proposal_only_no_state_mutation",
            "target": "prospect_marson_cd4_perturbseq",
        },
        replay_metadata={
            "command": replay,
            "rule": CAUSAL_RULE,
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        },
    ).freeze()
    return receipt.to_dict()


def build_claude_science_packet() -> dict[str, Any]:
    signature_path = CLAUDE_EXPORT / "signature_genes.json"
    cd8_path = CLAUDE_EXPORT / "responder_DE_CD8.csv"
    all_path = CLAUDE_EXPORT / "responder_DE_all.csv"
    provenance = _read_json(CLAUDE_EXPORT / "provenance.json")
    signature = _read_json(signature_path)
    genes = signature_genes(signature)
    verdicts = causal_verdicts(genes, de_table_path=cd8_path)
    counts = verdict_counts(verdicts)
    artifacts = [
        {"name": "signature_genes.json", "sha256": sha256_file(signature_path), "locator": "examples/data/claude_science_real_export/signature_genes.json"},
        {"name": "responder_DE_CD8.csv", "sha256": sha256_file(cd8_path), "locator": "examples/data/claude_science_real_export/responder_DE_CD8.csv"},
        {"name": "responder_DE_all.csv", "sha256": sha256_file(all_path), "locator": "examples/data/claude_science_real_export/responder_DE_all.csv"},
        {"name": "marson_de_full.csv", "sha256": sha256_file(MARSON_FULL), "locator": "examples/data/marson_de_full.csv"},
    ]
    claim = CAUSAL_RULE["claim_under_test"]
    receipt = _receipt_from_verdicts(
        producer={
            "kind": "external_workbench",
            "name": "Claude Science",
            "run": "sade_feldman_signature_export",
            "real_export": True,
        },
        claim=claim,
        artifacts=artifacts,
        verdicts=verdicts,
        replay="python examples/claude_science_connector_client.py --json",
    )
    return {
        "demo_id": "claude_science_acceptance_layer",
        "producer": "claude_science",
        "source_dataset": "Sade-Feldman 2018 melanoma ICB scRNA-seq, GSE120575",
        "real_export": True,
        "claim_under_test": claim,
        "causal_rule": CAUSAL_RULE,
        "claude_science": {
            "artifact_status": "reproducible_export",
            "internal_review_status": provenance["claude_science_internal_review"]["status"],
            "internal_review_findings": provenance["claude_science_internal_review"]["findings"],
            "session_caveat": provenance["session_caveat"],
            "auc": signature.get("AUC", {}),
        },
        "prospect": {
            "verifier": "ProspectCausalReceiptBridge",
            "trust_path": "frozen Marson lookup plus human key",
            "accepted": False,
            "next": "human_signature_required",
            "typed_status_counts": counts,
            "receipt_id": receipt["receipt_id"],
            "proposal_id": "proposal_" + hashlib.sha256(receipt["receipt_id"].encode()).hexdigest()[:16],
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        },
        "artifacts": artifacts,
        "verdicts": verdicts,
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
    if case == "claude_science":
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

