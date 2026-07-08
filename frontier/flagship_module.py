"""Build the Phase 3 flagship PGGT1B hypothesis packet."""
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

SUPPORTED_ALTERNATIVES = ["CCDC22", "LETM2", "TNNC1"]


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required packet: {path}")
    return json.loads(path.read_text())


def _packet_id(packet: dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"flagship_{digest[:16]}"


def _screen_hit_detail(row: dict[str, Any]) -> str:
    hits = row["external_screen_summary"]["supporting_hits"]
    return ", ".join(hits) if hits else "no independent screen-hit row"


def _schmidt_status(row: dict[str, Any]) -> str:
    if "schmidt_2022_2427" in row["external_screen_summary"].get("orthogonal_phenotypes", []):
        return "orthogonal_phenotype"
    if "schmidt_2022_2427" in row["external_screen_summary"].get("contradictions", []):
        return "contradicted"
    return "evidence_attached"


def _alternative(row: dict[str, Any]) -> dict[str, Any]:
    reasons = {
        "CCDC22": (
            "Independent Shifrut support and genetic disease context remain visible, but PGGT1B is "
            "rank-1 in the novelty funnel and has the strongest direct prenylation hook."
        ),
        "LETM2": (
            "Independent Shifrut support remains visible, but its mechanism is less directly tied to "
            "small-GTPase prenylation and immune-synapse traffic."
        ),
        "TNNC1": (
            "Independent Shifrut support remains visible, but the current packet lacks a stronger "
            "T-cell-specific mechanistic bridge than PGGT1B."
        ),
    }
    return {
        "gene": row["gene"],
        "rank": row["rank"],
        "tier": row["tier"],
        "marson_stim_max_de": row["marson_stim_max_de"],
        "supporting_hits": row["external_screen_summary"]["supporting_hits"],
        "schmidt_status": _schmidt_status(row),
        "string_partners": row["string_network"]["top_partners"][:5],
        "disease_context": row["disease_context"],
        "why_not_flagship": reasons[row["gene"]],
    }


def build_flagship_module() -> dict[str, Any]:
    cross_validation = _load(CROSS_VALIDATION_JSON)
    rows_by_gene = {row["gene"]: row for row in cross_validation["candidates"]}
    pg = rows_by_gene["PGGT1B"]
    schmidt = cross_validation["readout_comparability"]["schmidt_2022_2427"]
    partners = pg["string_network"]["top_partners"]
    hypothesis = {
        "gene": "PGGT1B",
        "rank": pg["rank"],
        "status": "evidence_attached",
        "accepted": False,
        "trust_boundary": "proposal_only",
        "support_level": "rank_1_screen_supported_hypothesis",
        "schmidt_status": _schmidt_status(pg),
        "claim": (
            "Hypothesis: PGGT1B modulates the stimulated primary human CD4+ T-cell activation "
            "transcriptome through geranylgeranylation of small-GTPase signaling that supports "
            "immune-synapse traffic."
        ),
        "candidate_evidence": pg,
        "evidence_ladder": [
            {
                "rung": "novelty_funnel",
                "status": "evidence_attached",
                "detail": "Rank 1 among 18 novelty survivors after scanning 11,526 frontier genes.",
            },
            {
                "rung": "marson_frontier",
                "status": "computationally_reproduced",
                "detail": f"{pg['marson_stim_max_de']} stimulated DE genes in the frozen Marson replay.",
            },
            {
                "rung": "replogle_specificity",
                "status": "evidence_attached",
                "detail": "T-cell activation signal stays inert in the Replogle K562/RPE1 transfer screen.",
            },
            {
                "rung": "shifrut_primary_t_cell_screen",
                "status": "evidence_attached",
                "detail": _screen_hit_detail(pg),
            },
            {
                "rung": "schmidt_cytokine_screen",
                "status": "orthogonal_phenotype",
                "detail": schmidt["interpretation"],
            },
            {
                "rung": "protein_prenylation_context",
                "status": "evidence_attached",
                "detail": (
                    "STRING attaches PGGT1B to prenylation and small-GTPase partners: "
                    f"{', '.join(partners[:10])}."
                ),
            },
            {
                "rung": "immune_expression",
                "status": "evidence_attached",
                "detail": f"DICE activated CD4 mean TPM {pg['dice_expression']['activated_cd4_mean_tpm']}.",
            },
            {
                "rung": "disease_genetics",
                "status": "evidence_attached",
                "detail": pg["open_targets"]["overlay_class"],
            },
        ],
        "caveats": [
            "Single-lab-derived Marson replay, not wet-lab or clinical truth.",
            "Schmidt 2022 is an orthogonal cytokine-production phenotype, not a comparable contradiction.",
            "External context proposes mechanism and assay priority, but does not accept state.",
        ],
        "refutation_experiment": {
            "system": "stimulated primary human CD4+ T cells",
            "perturbations": ["PGGT1B"],
            "readout": "CRISPRi followed by activation-marker flow cytometry and targeted RNA-seq at 8h and 48h",
            "refutes_if": (
                "orthogonal PGGT1B knockdown produces no reproducible activation-program shift, "
                "or the shift is equally strong at Rest and in non-immune controls"
            ),
        },
        "why_not_accepted": (
            "This is not wet-lab or clinical truth. It is a proposal supported by released-data computation "
            "and external context, with a direct refutation experiment."
        ),
    }
    supported_alternatives = [_alternative(rows_by_gene[gene]) for gene in SUPPORTED_ALTERNATIVES]
    packet = {
        "phase": "phase_3_single_gene_hypothesis",
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
        "selection_rationale": (
            "PGGT1B is selected because it is the rank-1 novelty survivor, has the largest Marson "
            "activation-transcriptome signal in the candidate set, has Shifrut support, and has a "
            "direct geranylgeranylation link to small-GTPase traffic. CCDC22, LETM2, and TNNC1 remain "
            "explicit supported alternatives."
        ),
        "flagship_hypothesis": hypothesis,
        "supported_alternatives": supported_alternatives,
        "reproduce_command": "./prospect flagship-module",
        "next_phase": "measure the refusal funnel and overclaim counter around the single PGGT1B hypothesis",
    }
    packet["packet_id"] = _packet_id(packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    hypothesis = packet["flagship_hypothesis"]
    lines = [
        "# Flagship finding",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No hypothesis enters accepted state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        f"Claim: {hypothesis['claim']}",
        "",
        "This is a single PGGT1B hypothesis, not a module claim.",
        "",
        f"Selection rationale: {packet['selection_rationale']}",
        "",
        "## Evidence ladder",
        "",
        "| rung | status | detail |",
        "|---|---|---|",
    ]
    for rung in hypothesis["evidence_ladder"]:
        lines.append(f"| {rung['rung']} | {rung['status']} | {rung['detail']} |")
    lines += [
        "",
        "## Supported alternatives",
        "",
        "| gene | rank | tier | screen support | Schmidt status | why not the flagship |",
        "|---|---:|---|---|---|---|",
    ]
    for row in packet["supported_alternatives"]:
        lines.append(
            f"| {row['gene']} | {row['rank']} | {row['tier']} | "
            f"{', '.join(row['supporting_hits'])} | {row['schmidt_status']} | {row['why_not_flagship']} |"
        )
    exp = hypothesis["refutation_experiment"]
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
        "## Caveats",
        "",
    ]
    lines += [f"- {caveat}" for caveat in hypothesis["caveats"]]
    lines += [
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
    print(f"wrote {OUT_JSON} ({packet['flagship_hypothesis']['gene']} hypothesis)")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
