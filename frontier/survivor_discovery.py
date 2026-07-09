"""Build the judge-facing survivor discovery packet from overnight outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"

LEADERBOARD_JSON = DATA / "overnight_defended_leaderboard.json"
ATLAS_JSON = DATA / "overnight_genome_wide_atlas.json"
LITERATURE_AUDIT_JSON = DATA / "overnight_literature_audit.json"
CROSS_SOURCES_JSON = DATA / "cross_validation_sources.json"
DISEASE_JSON = DATA / "disease_genetics_overlay.json"
OUT_JSON = DATA / "survivor_discovery.json"
OUT_CSV = DATA / "survivor_discovery.csv"
OUT_DOC = ROOT / "docs" / "SURVIVOR_DISCOVERY.md"

HONEST_CEILING = "Computation over released data, not wet-lab or clinical truth."

MECHANISMS = {
    "PGGT1B": {
        "axis": "prenylation and small-GTPase traffic",
        "mechanism": (
            "PGGT1B may tune the stimulated CD4+ activation transcriptome through geranylgeranylation "
            "of small-GTPase traffic nodes that support immune-synapse and receptor-localization programs."
        ),
        "why_it_matters": (
            "This connects a large Stim8hr perturbation effect to a concrete biochemical axis, with K562 specificity "
            "and Shifrut primary T-cell support."
        ),
        "refuting_readout": "prenylation or small-GTPase localization plus activation-transcriptome shift",
    },
    "CCDC22": {
        "axis": "CCC, COMMD, and retromer-associated endosomal traffic",
        "mechanism": (
            "CCDC22 may connect stimulated CD4+ activation state to CCC and COMMD retromer-associated trafficking, "
            "a route for receptor recycling and endosomal control rather than a canonical transcription factor route."
        ),
        "why_it_matters": (
            "This is the cleanest genetic hook among the survivors, with immune-dysregulation context and a strong "
            "CCDC93, VPS35L, and COMMD protein-network neighborhood."
        ),
        "refuting_readout": "endosomal receptor recycling markers plus Stim48hr activation-transcriptome shift",
    },
    "LETM2": {
        "axis": "organelle ion homeostasis and late activation state",
        "mechanism": (
            "LETM2 may affect the late stimulated CD4+ activation state through organelle ion-homeostasis biology, "
            "but its mechanistic bridge is weaker than PGGT1B or CCDC22 and must be tested directly."
        ),
        "why_it_matters": (
            "It survives the full frozen compute bar with a low-Rest Marson signal, Shifrut support, DICE expression, "
            "and multiple-sclerosis pathway context, while staying visibly caveated."
        ),
        "refuting_readout": "mitochondrial or organelle ion stress markers plus Stim48hr activation-transcriptome shift",
    },
}


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required source: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _source(path: Path, role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "role": role,
        "sha256": _sha256(path),
    }


def _by_gene(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["gene"]: row for row in rows}


def _screen_summary(gene: str, cross_sources: dict[str, Any]) -> dict[str, Any]:
    screens = cross_sources.get("screen_rows", {}).get(gene, {})
    shifrut_hits = [
        screen_id for screen_id, row in screens.items()
        if screen_id.startswith("shifrut") and row.get("hit_status") == "hit"
    ]
    schmidt = screens.get("schmidt_2022_2427")
    return {
        "shifrut_support": shifrut_hits,
        "schmidt_status": "orthogonal_phenotype" if schmidt else "not_assayed",
        "raw": screens,
    }


def _literature_context(gene: str, audit: dict[str, Any]) -> dict[str, Any]:
    claims = [row for row in audit["claims"] if row["gene"] == gene]
    counts: dict[str, int] = {}
    for row in claims:
        counts[row["typed_status"]] = counts.get(row["typed_status"], 0) + 1
    return {
        "claim_count": len(claims),
        "typed_status_counts": counts,
        "interpretation": (
            "No direct claim in the frozen literature corpus. This is absence in the bounded corpus, not proof of novelty."
            if not claims else
            "Direct literature claims exist in the bounded corpus and stay typed by Prospect."
        ),
        "claims": claims[:10],
    }


def _survivor_row(
    row: dict[str, Any],
    atlas: dict[str, dict[str, Any]],
    cross_sources: dict[str, Any],
    disease_by_gene: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any]:
    gene = row["gene"]
    atlas_row = atlas[gene]
    mechanism = MECHANISMS[gene]
    string_row = cross_sources.get("string_network", {}).get(gene, {"top_partners": [], "interactions": []})
    dice_row = cross_sources.get("dice_expression", {}).get(gene)
    disease_row = disease_by_gene.get(gene)
    screen = _screen_summary(gene, cross_sources)
    lit = _literature_context(gene, audit)
    return {
        "rank": row["rank"],
        "gene": gene,
        "typed_status": "evidence_attached",
        "accepted": False,
        "next": "human_signature_required",
        "axis": mechanism["axis"],
        "mechanism": mechanism["mechanism"],
        "why_it_matters": mechanism["why_it_matters"],
        "strongest_condition": row["strongest_condition"],
        "strongest_de": row["rank_input_strongest_de"],
        "direction": {
            "up_genes": atlas_row["strongest_n_up_genes"],
            "down_genes": atlas_row["strongest_n_down_genes"],
            "effect_size": atlas_row["strongest_effect_size"],
        },
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "orthogonal_dataset_count": row["orthogonal_dataset_count"],
        "orthogonal_datasets": row["orthogonal_datasets"],
        "shifrut_support": screen["shifrut_support"],
        "schmidt_status": screen["schmidt_status"],
        "string_partners": string_row.get("top_partners", [])[:10],
        "dice_activated_cd4_mean_tpm": None if not dice_row else dice_row.get("activated_cd4_mean_tpm"),
        "disease_context": None if not disease_row else {
            "overlay_class": disease_row["overlay_class"],
            "top_context": disease_row.get("top_context"),
        },
        "literature_audit": lit,
        "kill_attempts": row["kill_attempts"],
        "falsifiable_experiment": {
            "system": "stimulated primary human CD4+ T cells",
            "intervention": f"CRISPRi knockdown of {gene} with at least two independent guides",
            "condition": row["strongest_condition"],
            "readouts": [
                "activation-marker flow cytometry",
                "targeted RNA-seq or Perturb-seq activation program",
                mechanism["refuting_readout"],
                "viability and housekeeping stress control",
            ],
            "refutes_if": (
                f"adequate {gene} knockdown does not shift the registered activation program in "
                f"{row['strongest_condition']}, or the same shift is explained by broad viability or housekeeping stress"
            ),
        },
    }


def build_survivor_discovery() -> dict[str, Any]:
    leaderboard = _load(LEADERBOARD_JSON)
    atlas = _load(ATLAS_JSON)
    audit = _load(LITERATURE_AUDIT_JSON)
    cross_sources = _load(CROSS_SOURCES_JSON)
    disease = _load(DISEASE_JSON)
    atlas_by_gene = _by_gene(atlas["rows"])
    disease_by_gene = _by_gene(disease["rows"])
    survivors = [
        row for row in leaderboard["leaderboard"]
        if row["leaderboard_status"] == "clears_pre_registered_compute_bar"
    ]
    rows = [_survivor_row(row, atlas_by_gene, cross_sources, disease_by_gene, audit) for row in survivors]
    packet: dict[str, Any] = {
        "phase": "survivor_discovery",
        "title": "Three noncanonical activation-control survivor hypotheses",
        "status": "evidence_attached",
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "claim": (
            "The strict Prospect overnight gate reduced 2,734 novel causal-driver candidates to three "
            "proposal-only hypotheses: PGGT1B, CCDC22, and LETM2. They are not a settled module. "
            "They are three mechanistically distinct perturbation-backed hypotheses worth testing."
        ),
        "what_is_new": (
            "A genome-wide, pre-registered, adversarial gate over frozen released substrates retained only "
            "three noncanonical candidates after five kill axes, while the literature audit typed 51 of 229 "
            "published CD4+ regulatory claims as contradicted."
        ),
        "what_is_not_claimed": [
            "no wet-lab truth",
            "no accepted biological state",
            "no settled module",
            "no claim that bounded literature silence proves novelty",
        ],
        "source_counts": {
            "atlas_genes": atlas["gene_count"],
            "literature_claims": audit["claim_count"],
            "literature_contradicted": audit["typed_status_counts"]["contradicted"],
            "leaderboard_candidates_scored": leaderboard["candidate_count_scored"],
            "survivors": len(rows),
        },
        "survivors": rows,
        "source_artifacts": [
            _source(LEADERBOARD_JSON, "full overnight defended leaderboard"),
            _source(ATLAS_JSON, "genome-wide causal atlas"),
            _source(LITERATURE_AUDIT_JSON, "published-claim contradiction audit"),
            _source(CROSS_SOURCES_JSON, "frozen orthogonal source bundle"),
            _source(DISEASE_JSON, "frozen disease-context overlay"),
        ],
        "reproduce_command": "./prospect survivor-discovery",
    }
    packet["survivor_discovery_id"] = _hash_obj("survivor_discovery", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Survivor discovery",
        "",
        f"Status: `{packet['status']}`. accepted=false. next=human_signature_required.",
        "",
        f"Ceiling: {packet['honest_ceiling']}",
        "",
        packet["claim"],
        "",
        "## Three Numbers",
        "",
        f"- Genome-wide genes typed: {packet['source_counts']['atlas_genes']}",
        f"- Literature claims contradicted: {packet['source_counts']['literature_contradicted']} of {packet['source_counts']['literature_claims']}",
        f"- Novel driver candidates scored: {packet['source_counts']['leaderboard_candidates_scored']}",
        f"- Survivor hypotheses retained: {packet['source_counts']['survivors']}",
        "",
        "## Survivor Hypotheses",
        "",
        "| rank | gene | axis | strongest condition | strongest DE | K562 DE | orthogonal datasets |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in packet["survivors"]:
        k562 = "" if row["k562_de"] is None else str(row["k562_de"])
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['axis']} | {row['strongest_condition']} | "
            f"{row['strongest_de']} | {k562} | {row['orthogonal_dataset_count']} |"
        )
    lines += ["", "## Mechanistic Reads", ""]
    for row in packet["survivors"]:
        lines += [
            f"### {row['gene']}",
            "",
            row["mechanism"],
            "",
            f"Why it matters: {row['why_it_matters']}",
            "",
            f"Falsifiable experiment: {row['falsifiable_experiment']['intervention']} in {row['falsifiable_experiment']['condition']}; refutes if {row['falsifiable_experiment']['refutes_if']}.",
            "",
        ]
    lines += [
        "## What This Does Not Claim",
        "",
    ]
    lines += [f"- {item}" for item in packet["what_is_not_claimed"]]
    lines += [
        "",
        "## Public Artifact",
        "",
        "- `/data/survivor_discovery.json`",
        "",
        "## Reproduce",
        "",
        "```bash",
        "./prospect survivor-discovery",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_survivor_discovery() -> dict[str, Any]:
    packet = build_survivor_discovery()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    fields = [
        "rank", "gene", "axis", "typed_status", "strongest_condition", "strongest_de",
        "rest_de", "k562_de", "rpe1_de", "orthogonal_dataset_count", "schmidt_status",
    ]
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in packet["survivors"]:
            writer.writerow({field: row.get(field) for field in fields})
    OUT_DOC.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect survivor-discovery")
    parser.add_argument("--json", action="store_true", help="print packet JSON")
    args = parser.parse_args(argv)
    packet = write_survivor_discovery()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {OUT_JSON}")
        print(f"wrote {OUT_CSV}")
        print(f"wrote {OUT_DOC}")
        print(f"survivor_discovery_id={packet['survivor_discovery_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
