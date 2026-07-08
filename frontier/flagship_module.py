"""Build the Phase 3 flagship mechanistic module packet."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
OUT_JSON = DATA / "flagship_module.json"
OUT_DOC = ROOT / "docs" / "FLAGSHIP_FINDING.md"

MODULES = [
    {
        "module_id": "prenylation_small_gtpase_trafficking",
        "name": "Prenylation and trafficking control of activation",
        "anchor_gene": "PGGT1B",
        "members": ["PGGT1B", "CCDC22", "SNAP29", "MITD1"],
        "mechanism": (
            "A proposal that stimulated CD4+ activation depends on prenylation-linked small-GTPase "
            "signaling and endosomal trafficking logistics."
        ),
    },
    {
        "module_id": "mitochondrial_metabolic_activation",
        "name": "Mitochondrial metabolic activation",
        "anchor_gene": "MCAT",
        "members": ["RCC1L", "MCAT", "SCO2", "BCKDHA"],
        "mechanism": (
            "A proposal that metabolic and mitochondrial support constrains the stimulated activation program."
        ),
    },
    {
        "module_id": "rna_decay_and_effector_context",
        "name": "RNA decay and effector context",
        "anchor_gene": "ZC3H12A",
        "members": ["DAPK2", "GZMB", "ZC3H12A", "TNNC1"],
        "mechanism": (
            "A proposal that late activation, RNA decay, and effector-state genes mark a second follow-up lane."
        ),
    },
]


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required packet: {path}")
    return json.loads(path.read_text())


def _packet_id(packet: dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"flagship_{digest[:16]}"


def _score(member_rows: list[dict[str, Any]]) -> float:
    screen_bonus = 80 * sum(1 for row in member_rows if row["external_screen_summary"]["supporting_hits"])
    network_bonus = 10 * sum(1 for row in member_rows if row["string_network"]["top_partners"])
    marson_component = sum(row["marson_stim_max_de"] for row in member_rows) / 100
    contradiction_penalty = 5 * sum(1 for row in member_rows if row["external_screen_summary"]["contradictions"])
    return round(screen_bonus + network_bonus + marson_component - contradiction_penalty, 2)


def _module_row(defn: dict[str, Any], rows_by_gene: dict[str, dict[str, Any]]) -> dict[str, Any]:
    member_rows = [rows_by_gene[gene] for gene in defn["members"]]
    screen_supported = [
        row["gene"]
        for row in member_rows
        if row["external_screen_summary"]["supporting_hits"]
    ]
    module = {
        "module_id": defn["module_id"],
        "name": defn["name"],
        "anchor_gene": defn["anchor_gene"],
        "members": defn["members"],
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "mechanism": defn["mechanism"],
        "score": _score(member_rows),
        "screen_supported_members": screen_supported,
        "contradicting_screen": "schmidt_2022_2427",
        "member_evidence": member_rows,
    }
    return module


def build_flagship_module() -> dict[str, Any]:
    cross_validation = _load(CROSS_VALIDATION_JSON)
    rows_by_gene = {row["gene"]: row for row in cross_validation["candidates"]}
    modules = [_module_row(defn, rows_by_gene) for defn in MODULES]
    modules.sort(key=lambda row: (-row["score"], row["module_id"]))
    for rank, module in enumerate(modules, 1):
        module["rank"] = rank
    flagship = modules[0]
    flagship["claim"] = (
        "Hypothesis: a prenylation and small-GTPase-trafficking module anchored on PGGT1B "
        "modulates stimulated human CD4+ T-cell activation."
    )
    flagship["evidence_ladder"] = [
        {
            "rung": "marson_frontier",
            "status": "computationally_reproduced",
            "detail": "PGGT1B has 3,014 stimulated DE genes and CCDC22 has 619 in the frozen frontier.",
        },
        {
            "rung": "independent_primary_t_cell_screen",
            "status": "evidence_attached",
            "detail": "PGGT1B and CCDC22 are hits in Shifrut 2018 screen 1107.",
        },
        {
            "rung": "contradiction",
            "status": "contradicted",
            "detail": "All four members are non-hits in Schmidt 2022 screen 2427.",
        },
        {
            "rung": "network_coherence",
            "status": "evidence_attached",
            "detail": "STRING neighborhoods connect PGGT1B to prenylation and small-GTPase partners and the other members to trafficking complexes.",
        },
        {
            "rung": "immune_expression",
            "status": "evidence_attached",
            "detail": "All four members have DICE activated CD4 expression rows.",
        },
    ]
    flagship["refutation_experiment"] = {
        "system": "stimulated primary human CD4+ T cells",
        "perturbations": flagship["members"],
        "readout": "CRISPRi followed by activation-marker flow cytometry and targeted RNA-seq at 8h and 48h",
        "refutes_if": (
            "orthogonal knockdown produces no reproducible activation-program shift for the module, "
            "or the effect is equally strong at Rest and in non-immune controls"
        ),
    }
    flagship["why_not_accepted"] = (
        "This is not wet-lab or clinical truth. It is a proposal supported by released-data computation "
        "and external context, with a direct refutation experiment."
    )
    packet = {
        "phase": "phase_3_flagship_module",
        "title": "Flagship finding",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted": False,
        "honest_ceiling": "computation over released data, not wet-lab or clinical truth",
        "source_packets": {
            "discovery_campaign": "examples/data/discovery_campaign.json",
            "cross_validation": "examples/data/cross_validation.json",
        },
        "modules": modules,
        "flagship_module": flagship,
        "reproduce_command": "./prospect flagship-module",
        "next_phase": "quantify overclaims and refusals caught by the evidence ladder",
    }
    packet["packet_id"] = _packet_id(packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    flagship = packet["flagship_module"]
    lines = [
        "# Flagship finding",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No module enters accepted state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        f"Claim: {flagship['claim']}",
        "",
        "## Module",
        "",
        f"Anchor: {flagship['anchor_gene']}. Members: {', '.join(flagship['members'])}.",
        "",
        f"Mechanism: {flagship['mechanism']}",
        "",
        "## Evidence ladder",
        "",
        "| rung | status | detail |",
        "|---|---|---|",
    ]
    for rung in flagship["evidence_ladder"]:
        lines.append(f"| {rung['rung']} | {rung['status']} | {rung['detail']} |")
    lines += [
        "",
        "## Competing modules",
        "",
        "| rank | module | members | score | screen-supported members |",
        "|---:|---|---|---:|---|",
    ]
    for module in packet["modules"]:
        lines.append(
            f"| {module['rank']} | {module['module_id']} | {', '.join(module['members'])} | "
            f"{module['score']} | {', '.join(module['screen_supported_members'])} |"
        )
    exp = flagship["refutation_experiment"]
    lines += [
        "",
        "## Refutation experiment",
        "",
        f"System: {exp['system']}.",
        "",
        f"Perturbations: {', '.join(exp['perturbations'])}.",
        "",
        f"Readout: {exp['readout']}.",
        "",
        f"Refutes if: {exp['refutes_if']}.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect flagship-module",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_flagship_module(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_flagship_module()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_flagship_module()
    print(f"wrote {OUT_JSON} ({packet['flagship_module']['module_id']})")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
