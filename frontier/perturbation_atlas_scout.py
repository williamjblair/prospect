"""Build a source-backed perturbation-atlas scout packet."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "perturbation_atlas_scout.json"
OUT_DOC = ROOT / "docs" / "PERTURBATION_ATLAS_SCOUT.md"
SIG = ROOT / "frontier" / "frontier.sig.json"


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


SOURCE_FACTS = [
    {
        "id": "czi_k562_essential",
        "name": "CZI K562 Essential Perturb-seq Benchmark Dataset",
        "source_url": "https://virtualcellmodels.cziscience.com/dataset/k562-essential-perturb-seq",
        "source_type": "dataset_card",
        "key_facts": [
            "single processed H5AD file",
            "K562 CRISPRi essential-gene Perturb-seq",
            "contains DE gene sets in unstructured AnnData fields",
            "median greater than 100 cells per perturbation after filtering",
            "license prohibits some commercial or unauthorized uses",
        ],
    },
    {
        "id": "scperturb",
        "name": "scPerturb",
        "source_url": "https://projects.sanderlab.org/scperturb/",
        "source_type": "resource_and_figshare_archive",
        "key_facts": [
            "standardized single-cell perturbation datasets",
            "dataset explorer includes publication links, perturbation type, and perturbation counts",
            "RNA and protein H5AD archive is 25.01 GB",
            "the resource includes E-distance tooling for perturbation effect testing",
        ],
    },
    {
        "id": "perturbase",
        "name": "PerturBase",
        "source_url": "https://academic.oup.com/nar/article-abstract/53/D1/D1099/7815638",
        "source_type": "paper_and_database",
        "key_facts": [
            "122 scPerturbation datasets from 46 public studies",
            "115 single-modal and 7 multi-modal datasets",
            "24,254 genetic and 230 chemical perturbations",
            "about 5 million cells",
            "web modules expose dataset and perturbation views",
        ],
    },
    {
        "id": "tahoe_100m",
        "name": "Tahoe-100M",
        "source_url": "https://arcinstitute.org/news/arc-vevo",
        "source_type": "atlas_release",
        "key_facts": [
            "100 million cells",
            "60,000 drug-cell interactions",
            "50 cancer cell lines",
            "1,200 drug perturbations",
            "open through Arc Virtual Cell Atlas",
        ],
    },
    {
        "id": "pertpy_replogle_loader",
        "name": "pertpy Replogle 2022 K562 GWPS loader",
        "source_url": "https://pertpy.readthedocs.io/en/stable/api/data/pertpy.data.replogle_2022_k562_gwps.html",
        "source_type": "tooling_doc",
        "key_facts": [
            "loads Replogle 2022 K562 genome-wide Perturb-seq as AnnData",
            "CRISPRi K562 day-8 loss-of-function assay",
            "obtained from scPerturb",
            "useful tooling path, not a distinct new biological substrate",
        ],
    },
]


SCOUT_ROWS = [
    {
        "id": "czi_k562_essential",
        "name": "CZI K562 Essential Perturb-seq Benchmark Dataset",
        "license_fit": "needs_review",
        "download_size": "single processed h5ad",
        "access_path": "CZI Virtual Cells Platform dataset card",
        "perturbation_type": "genetic_crispri",
        "cell_context": "K562 chronic myeloid leukemia cell line",
        "overlap_with_prospect": "high_for_shared_replogle_genes",
        "freeze_small_table_feasibility": "medium",
        "replay_fit": "highest",
        "decision": "scout_only",
        "reason": "single processed h5ad, but overlaps an already shipped Replogle substrate",
        "risk": "would spend time reproducing an existing substrate instead of advancing the frontier",
        "next_step": "use only if a full single-cell DE replay is needed after the current submission floor",
    },
    {
        "id": "scperturb",
        "name": "scPerturb",
        "license_fit": "needs_dataset_level_review",
        "download_size": "25.01 GB",
        "access_path": "resource site plus Figshare H5AD archive",
        "perturbation_type": "mixed_genetic_and_drug",
        "cell_context": "many public single-cell perturbation studies",
        "overlap_with_prospect": "unknown_until_dataset_table_is_filtered",
        "freeze_small_table_feasibility": "medium_after_metadata_filter",
        "replay_fit": "medium",
        "decision": "scout_only",
        "reason": "best broad genetic-perturbation catalog, but full archive is too large for immediate trust-path ingestion",
        "risk": "broad ingestion would create more parser and license work than discovery signal before July 13",
        "next_step": "filter the dataset explorer for small human CRISPRi or CRISPR knockout studies before any download",
    },
    {
        "id": "perturbase",
        "name": "PerturBase",
        "license_fit": "needs_database_terms_review",
        "download_size": "about 5 million cells across database",
        "access_path": "web database and published study",
        "perturbation_type": "mixed_genetic_and_chemical",
        "cell_context": "human and mouse scPerturbation studies",
        "overlap_with_prospect": "likely_high_at_gene_symbol_level",
        "freeze_small_table_feasibility": "low_until_export_path_is_confirmed",
        "replay_fit": "medium",
        "decision": "scout_only",
        "reason": "excellent search surface, but not yet a small reproducible replay extract",
        "risk": "manual web extraction would be hard to audit as a frozen checker input",
        "next_step": "use as discovery index only, then trace any candidate dataset back to primary downloadable files",
    },
    {
        "id": "tahoe_100m",
        "name": "Tahoe-100M",
        "license_fit": "promising_public_release",
        "download_size": "100 million cells",
        "access_path": "Arc Virtual Cell Atlas",
        "perturbation_type": "drug",
        "cell_context": "50 cancer cell lines",
        "overlap_with_prospect": "indirect_drug_response_only",
        "freeze_small_table_feasibility": "low_for_hackathon",
        "replay_fit": "low_for_current_question",
        "decision": "no_go_large_ingest",
        "reason": "large chemical perturbation atlas, not a direct genetic replay substrate for CD4+ candidates",
        "risk": "too large and chemical-only for a rushed accepted-state boundary",
        "next_step": "revisit after submission for drug-signature analogy packets, explicitly as hypothesis support",
    },
    {
        "id": "pertpy_replogle_loader",
        "name": "pertpy Replogle 2022 K562 GWPS loader",
        "license_fit": "tooling_only",
        "download_size": "AnnData loader",
        "access_path": "pertpy data API",
        "perturbation_type": "genetic_crispri",
        "cell_context": "K562 chronic myeloid leukemia cell line",
        "overlap_with_prospect": "already_used_as_reduced_replay_table",
        "freeze_small_table_feasibility": "high_but_redundant",
        "replay_fit": "redundant",
        "decision": "no_go_large_ingest",
        "reason": "useful loader, but not a new substrate beyond the shipped Replogle K562 replay",
        "risk": "would look like extra work while adding little frontier information",
        "next_step": "keep current reduced Replogle tables as the committed replay surface",
    },
]


def build_packet() -> dict[str, Any]:
    counts = Counter(row["decision"] for row in SCOUT_ROWS)
    return {
        "title": "Perturbation-atlas scout packet",
        "status": "evidence_attached",
        "trust_boundary": "source_backed_scout_no_ingest",
        "accepted_state_mutation": "none",
        "model_in_trust_path": "no",
        "signed_frontier_root": _frontier_root(),
        "replay_command": "./prospect perturbation-scout",
        "public_app_surface": "none",
        "counts": {
            "candidate_sources": len(SCOUT_ROWS),
            "go_now": counts.get("go_now", 0),
            "scout_only": counts.get("scout_only", 0),
            "no_go_large_ingest": counts.get("no_go_large_ingest", 0),
            "public_app_surface": 0,
        },
        "recommendation": {
            "decision": "do_not_ingest_new_large_dataset_before_submission",
            "why": (
                "The shipped cross-substrate, donor-condition, and disease-overlay packets already "
                "advance the frontier. A rushed large-corpus ingest would add trust-path risk without "
                "a stronger judge story."
            ),
            "next_best_action": "campaign_challenger_ledger",
        },
        "source_facts": SOURCE_FACTS,
        "candidate_sources": SCOUT_ROWS,
        "acceptance_rules_for_future_ingest": [
            "license and terms are clear enough for a committed frozen extract",
            "download or API path is reproducible without private credentials",
            "a small table can be frozen with source hashes",
            "the replay checks a claim not already covered by the shipped Replogle substrates",
            "status remains computationally_reproduced for frozen local facts and evidence_attached for interpretation",
        ],
        "limitations": (
            "This is a scout packet, not a replay packet. It attaches source-backed feasibility "
            "judgments and changes no accepted biological state."
        ),
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    lines = [
        "# Perturbation-atlas scout packet",
        "",
        "Status: `evidence_attached`.",
        "",
        "No accepted state changes. This packet ranks candidate perturbation resources for future replay work and does not ingest a new dataset.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["replay_command"],
        "```",
        "",
        "## Recommendation",
        "",
        f"Decision: `{packet['recommendation']['decision']}`.",
        "",
        packet["recommendation"]["why"],
        "",
        f"Next best action: `{packet['recommendation']['next_best_action']}`.",
        "",
        "## Counts",
        "",
        f"- Candidate sources: {counts['candidate_sources']}",
        f"- Go now: {counts['go_now']}",
        f"- Scout only: {counts['scout_only']}",
        f"- No-go large ingest: {counts['no_go_large_ingest']}",
        f"- Public app surface: {counts['public_app_surface']}",
        "",
        "## Candidate Sources",
        "",
        "| Source | Decision | Replay fit | Download size | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["candidate_sources"]:
        lines.append(
            f"| {row['name']} | `{row['decision']}` | {row['replay_fit']} | "
            f"{row['download_size']} | {row['reason']} |"
        )
    lines += [
        "",
        "## Future Ingest Rules",
        "",
    ]
    lines += [f"- {rule}" for rule in packet["acceptance_rules_for_future_ingest"]]
    lines += [
        "",
        "## Source Facts",
        "",
    ]
    for source in packet["source_facts"]:
        lines += [
            f"### {source['name']}",
            "",
            f"Source: {source['source_url']}",
            "",
        ]
        lines += [f"- {fact}" for fact in source["key_facts"]]
        lines.append("")
    lines += [
        packet["limitations"],
    ]
    return "\n".join(lines) + "\n"


def write_packet(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect perturbation-scout")
    parser.add_argument("--json", action="store_true", help="print the scout packet as JSON")
    args = parser.parse_args(argv)

    packet = write_packet()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"scouted {packet['counts']['candidate_sources']} perturbation sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
