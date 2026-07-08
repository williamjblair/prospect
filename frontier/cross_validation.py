"""Build the Phase 2 independent cross-validation packet."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
SOURCE_JSON = DATA / "cross_validation_sources.json"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
DISEASE_JSON = DATA / "disease_genetics_overlay.json"
OUT_JSON = DATA / "cross_validation.json"
OUT_CSV = DATA / "cross_validation.csv"
OUT_DOC = ROOT / "docs" / "CROSS_VALIDATION.md"

READOUT_COMPARABILITY = {
    "schmidt_2022_2427": {
        "typed_status": "orthogonal_phenotype",
        "determination": "not tested comparably",
        "marson_readout": (
            "CRISPRi Perturb-seq breadth of the activation transcriptome in primary human CD4+ T cells, "
            "summarized as stimulated differential-expression gene counts."
        ),
        "schmidt_readout": (
            "CRISPRa cytokine production screen in primary human CD4+ T cells, recorded by ORCS as "
            "regulation of stimulation-responsive cytokine production and protein/peptide accumulation."
        ),
        "interpretation": (
            "A Schmidt 2022 non-hit does not contradict a Marson activation-transcriptome regulator claim "
            "unless the claim is narrowed to cytokine production."
        ),
        "source": "https://orcs.thebiogrid.org/Screen/2427",
    }
}


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required frozen source: {path}")
    return json.loads(path.read_text())


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _screen_summary(screen_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    supporting_hits = [
        screen_id
        for screen_id, row in screen_rows.items()
        if row.get("hit_status") == "hit"
    ]
    orthogonal_phenotypes = [
        screen_id
        for screen_id, row in screen_rows.items()
        if row.get("hit_status") == "non_hit"
        and READOUT_COMPARABILITY.get(screen_id, {}).get("typed_status") == "orthogonal_phenotype"
    ]
    contradictions = [
        screen_id
        for screen_id, row in screen_rows.items()
        if row.get("hit_status") == "non_hit"
        and READOUT_COMPARABILITY.get(screen_id, {}).get("typed_status") == "contradicted"
    ]
    non_hits = [
        screen_id
        for screen_id, row in screen_rows.items()
        if row.get("hit_status") == "non_hit"
    ]
    missing = [
        screen_id
        for screen_id, row in screen_rows.items()
        if row.get("hit_status") == "not_in_table"
    ]
    return {
        "supporting_hits": supporting_hits,
        "orthogonal_phenotypes": orthogonal_phenotypes,
        "contradictions": contradictions,
        "non_hits": non_hits,
        "missing_rows": missing,
    }


def _disease_context(overlay_class: str) -> str:
    if "genetic" in overlay_class and "non_genetic" not in overlay_class:
        return "genetic_context"
    if "immune_or_hematologic" in overlay_class:
        return "immune_context"
    return "no_immune_or_hematologic_context"


def _row_for_candidate(
    candidate: dict[str, Any],
    source: dict[str, Any],
    disease_by_gene: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gene = candidate["gene"]
    screen_rows = source["screen_rows"][gene]
    screen_summary = _screen_summary(screen_rows)
    string_network = source["string_network"].get(gene, {"top_partners": [], "interactions": []})
    dice_expression = source["dice_expression"][gene]
    open_targets = disease_by_gene[gene]
    tier = "context_only"
    if screen_summary["supporting_hits"]:
        tier = "screen_hit_plus_context"
    row = {
        "rank": candidate["rank"],
        "gene": gene,
        "status": "evidence_attached",
        "tier": tier,
        "trust_boundary": "proposal_only",
        "marson_stim_max_de": candidate["stim_max_de"],
        "external_screen_summary": screen_summary,
        "string_network": string_network,
        "dice_expression": dice_expression,
        "open_targets": {
            "overlay_class": open_targets["overlay_class"],
            "top_context": open_targets.get("top_context"),
            "selected_associations": open_targets.get("selected_associations", []),
        },
        "disease_context": _disease_context(open_targets["overlay_class"]),
        "evidence_ladder": [
            {
                "rung": "marson_frontier",
                "status": "computationally_reproduced",
                "detail": f"{candidate['stim_max_de']} stimulated DE genes",
            },
            {
                "rung": "primary_t_cell_screen",
                "status": "evidence_attached" if screen_summary["supporting_hits"] else "orthogonal_phenotype",
                "detail": ", ".join(
                    screen_summary["supporting_hits"]
                    or screen_summary["orthogonal_phenotypes"]
                    or screen_summary["non_hits"]
                ),
            },
            {
                "rung": "schmidt_cytokine_screen",
                "status": "orthogonal_phenotype"
                if "schmidt_2022_2427" in screen_summary["orthogonal_phenotypes"]
                else "evidence_attached",
                "detail": READOUT_COMPARABILITY["schmidt_2022_2427"]["interpretation"],
            },
            {
                "rung": "protein_network",
                "status": "evidence_attached" if string_network["top_partners"] else "contradicted",
                "detail": ", ".join(string_network["top_partners"][:5]),
            },
            {
                "rung": "immune_expression",
                "status": "evidence_attached",
                "detail": f"DICE activated CD4 mean TPM {dice_expression['activated_cd4_mean_tpm']}",
            },
            {
                "rung": "disease_genetics",
                "status": "evidence_attached",
                "detail": open_targets["overlay_class"],
            },
        ],
        "why_not_accepted": (
            "The evidence supports a hypothesis, but it is computation over released data, "
            "not wet-lab or clinical truth."
        ),
    }
    return row


def build_cross_validation() -> dict[str, Any]:
    source = _load(SOURCE_JSON)
    discovery = _load(DISCOVERY_JSON)
    disease = _load(DISEASE_JSON)
    disease_by_gene = {row["gene"]: row for row in disease["rows"]}
    rows = [_row_for_candidate(candidate, source, disease_by_gene) for candidate in discovery["candidates"]]
    counts = {
        "candidate_count": len(rows),
        "candidates_with_external_screen_hit": sum(
            1 for row in rows if row["external_screen_summary"]["supporting_hits"]
        ),
        "candidates_with_schmidt_non_hit": sum(
            1 for row in rows if "schmidt_2022_2427" in row["external_screen_summary"]["non_hits"]
        ),
        "candidates_with_schmidt_orthogonal_phenotype": sum(
            1 for row in rows if "schmidt_2022_2427" in row["external_screen_summary"]["orthogonal_phenotypes"]
        ),
        "candidates_with_comparable_external_contradiction": sum(
            1 for row in rows if row["external_screen_summary"]["contradictions"]
        ),
        "candidates_with_string_network": sum(1 for row in rows if row["string_network"]["top_partners"]),
        "candidates_with_dice_cd4_expression": sum(
            1 for row in rows if row["dice_expression"].get("activated_cd4_mean_tpm") is not None
        ),
        "candidates_with_open_targets_context": sum(1 for row in rows if row["open_targets"]["overlay_class"]),
    }
    packet = {
        "phase": "phase_2_independent_cross_validation",
        "title": "Phase 2 cross-validation",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted": False,
        "honest_ceiling": "computation over released data, not wet-lab or clinical truth",
        "source_bundle_id": _hash_obj("external_sources", source),
        "source_bundle_path": "examples/data/cross_validation_sources.json",
        "source_urls": source["source_urls"],
        "readout_comparability": READOUT_COMPARABILITY,
        "candidate_count": len(rows),
        "counts": counts,
        "candidates": rows,
        "reproduce_command": "./prospect cross-validation",
        "next_phase": "carry the best-supported single hypothesis without treating orthogonal non-hits as contradictions",
    }
    packet["packet_id"] = _hash_obj("cross_validation", packet)
    return packet


def _write_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    fields = [
        "rank", "gene", "status", "tier", "marson_stim_max_de", "supporting_hits",
        "orthogonal_phenotypes", "contradictions", "activated_cd4_mean_tpm",
        "top_string_partners", "disease_context",
    ]
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "rank": row["rank"],
                "gene": row["gene"],
                "status": row["status"],
                "tier": row["tier"],
                "marson_stim_max_de": row["marson_stim_max_de"],
                "supporting_hits": ",".join(row["external_screen_summary"]["supporting_hits"]),
                "orthogonal_phenotypes": ",".join(row["external_screen_summary"]["orthogonal_phenotypes"]),
                "contradictions": ",".join(row["external_screen_summary"]["contradictions"]),
                "activated_cd4_mean_tpm": row["dice_expression"]["activated_cd4_mean_tpm"],
                "top_string_partners": ",".join(row["string_network"]["top_partners"][:5]),
                "disease_context": row["disease_context"],
            })


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    lines = [
        "# Phase 2 cross-validation",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No external evidence moves accepted state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "Sources: Shifrut 2018 primary human T-cell SLICE screens, Schmidt 2022 primary human CD4+ CRISPRa cytokine screen, STRING protein network, DICE immune-cell expression, and the existing Open Targets overlay.",
        "",
        "Schmidt comparability: `orthogonal_phenotype`. The Schmidt screen calls regulators of stimulation-responsive cytokine production and protein accumulation. The Marson replay measures activation-transcriptome breadth by stimulated differential-expression counts. A Schmidt non-hit is retained as evidence, but it is not a comparable contradiction of the Marson activation-transcriptome hypothesis.",
        "",
        "## Counts",
        "",
        f"- Candidates: {counts['candidate_count']}",
        f"- With at least one independent screen hit: {counts['candidates_with_external_screen_hit']}",
        f"- With explicit Schmidt 2022 non-hit rows: {counts['candidates_with_schmidt_non_hit']}",
        f"- Retyped as Schmidt orthogonal phenotype: {counts['candidates_with_schmidt_orthogonal_phenotype']}",
        f"- With comparable external contradictions: {counts['candidates_with_comparable_external_contradiction']}",
        f"- With STRING interaction context: {counts['candidates_with_string_network']}",
        f"- With DICE activated CD4 expression: {counts['candidates_with_dice_cd4_expression']}",
        "",
        "## Candidate ladder",
        "",
        "| rank | gene | tier | screen support | Schmidt status | contradiction | DICE activated CD4 mean TPM | STRING partners | disease context |",
        "|---:|---|---|---|---|---|---:|---|---|",
    ]
    for row in packet["candidates"]:
        support = ", ".join(row["external_screen_summary"]["supporting_hits"])
        orthogonal = ", ".join(row["external_screen_summary"]["orthogonal_phenotypes"])
        contra = ", ".join(row["external_screen_summary"]["contradictions"])
        partners = ", ".join(row["string_network"]["top_partners"][:4])
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['tier']} | {support} | {orthogonal} | {contra} | "
            f"{row['dice_expression']['activated_cd4_mean_tpm']} | {partners} | {row['disease_context']} |"
        )
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect cross-validation",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_cross_validation(
    out_json: Path = OUT_JSON,
    out_csv: Path = OUT_CSV,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_cross_validation()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    _write_csv(packet["candidates"], out_csv)
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_cross_validation()
    print(f"wrote {OUT_JSON} ({packet['candidate_count']} candidates)")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
