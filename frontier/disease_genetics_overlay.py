"""Build a score-neutral disease-genetics overlay for campaign rows."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
OUT_SOURCE = DATA / "disease_genetics_source_rows.json"
OUT_JSON = DATA / "disease_genetics_overlay.json"
OUT_DOC = ROOT / "docs" / "DISEASE_GENETICS_OVERLAY.md"
SIG = ROOT / "frontier" / "frontier.sig.json"
CAMPAIGN = DATA / "agent_campaign.json"

OPEN_TARGETS_GRAPHQL = "https://api.platform.opentargets.org/api/v4/graphql"
MIN_SELECTED_ASSOCIATION_SCORE = 0.05

IMMUNE_OR_HEMATOLOGIC_TERMS = [
    "allergic",
    "allergy",
    "asthma",
    "atopic",
    "b-cell",
    "crohn",
    "colitis",
    "dermatitis",
    "eczema",
    "hematologic",
    "immune",
    "immun",
    "inflammatory bowel",
    "juvenile idiopathic arthritis",
    "leukemia",
    "lymphoma",
    "lupus",
    "multiple sclerosis",
    "myeloma",
    "psoriasis",
    "rheumatoid",
    "t-cell",
    "type 1 diabetes",
    "vitiligo",
]

CLASS_ORDER = [
    "immune_or_hematologic_genetic_context",
    "immune_or_hematologic_non_genetic_context",
    "no_immune_or_hematologic_context",
]


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def _load_campaign() -> list[dict[str, Any]]:
    return json.loads(CAMPAIGN.read_text())["candidates"]


def _graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        OPEN_TARGETS_GRAPHQL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


def _target_for_gene(gene: str) -> dict[str, str]:
    query = """
    query Search($queryString: String!) {
      search(queryString: $queryString, entityNames: ["target"], page: {index: 0, size: 5}) {
        hits {
          object {
            ... on Target {
              id
              approvedSymbol
              approvedName
            }
          }
        }
      }
    }
    """
    data = _graphql(query, {"queryString": gene})
    for hit in data["search"]["hits"]:
        target = hit.get("object") or {}
        if target.get("approvedSymbol") == gene:
            return {
                "ensembl_id": target["id"],
                "approved_symbol": target["approvedSymbol"],
                "approved_name": target["approvedName"],
            }
    raise KeyError(f"Open Targets target not found for {gene}")


def _target_diseases(ensembl_id: str) -> dict[str, Any]:
    query = """
    query TargetDisease($ensemblId: String!) {
      target(ensemblId: $ensemblId) {
        id
        approvedSymbol
        associatedDiseases(page: {index: 0, size: 120}) {
          count
          rows {
            score
            disease {
              id
              name
            }
            datatypeScores {
              id
              score
            }
          }
        }
      }
    }
    """
    data = _graphql(query, {"ensemblId": ensembl_id})
    target = data["target"]
    return target["associatedDiseases"]


def _immune_or_hematologic(name: str) -> bool:
    lower = name.lower()
    return any(term in lower for term in IMMUNE_OR_HEMATOLOGIC_TERMS)


def _data_type_scores(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"id": score["id"], "score": round(float(score["score"]), 4)}
        for score in row.get("datatypeScores", [])
    ]


def _genetic_association_score(scores: list[dict[str, Any]]) -> float:
    for score in scores:
        if score["id"] == "genetic_association":
            return float(score["score"])
    return 0.0


def _primary_evidence_type(scores: list[dict[str, Any]]) -> str:
    positive = [score for score in scores if float(score["score"]) > 0]
    if not positive:
        return "association"
    return max(positive, key=lambda item: float(item["score"]))["id"]


def _selected_associations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for row in rows:
        disease = row["disease"]
        if not _immune_or_hematologic(disease["name"]):
            continue
        if float(row["score"]) < MIN_SELECTED_ASSOCIATION_SCORE:
            continue
        scores = _data_type_scores(row)
        selected.append(
            {
                "disease_id": disease["id"],
                "disease_or_trait": disease["name"],
                "association_score": round(float(row["score"]), 4),
                "datatype_scores": scores,
                "evidence_type": _primary_evidence_type(scores),
                "has_genetic_association": "yes" if _genetic_association_score(scores) > 0 else "no",
            }
        )
    return selected[:5]


def extract_source_rows() -> dict[str, Any]:
    """Extract a small Open Targets context packet for the campaign genes."""
    rows = []
    for candidate in _load_campaign():
        target = _target_for_gene(candidate["gene"])
        diseases = _target_diseases(target["ensembl_id"])
        rows.append(
            {
                "rank": int(candidate["rank"]),
                "gene": candidate["gene"],
                "campaign_status": candidate["status"],
                "strongest_condition": candidate["strongest_condition"],
                "ensembl_id": target["ensembl_id"],
                "approved_name": target["approved_name"],
                "open_targets_association_count": int(diseases["count"]),
                "selected_associations": _selected_associations(diseases["rows"]),
            }
        )
    return {
        "title": "Disease-genetics overlay source rows",
        "status": "evidence_attached",
        "retrieved_at": date.today().isoformat(),
        "source": {
            "name": "Open Targets Platform GraphQL API",
            "endpoint": OPEN_TARGETS_GRAPHQL,
            "target_query": "search target by approved symbol, then target.associatedDiseases",
            "page_size": 120,
        },
        "source_rows": "campaign genes with selected immune or hematologic target-disease associations",
        "regeneration_command": "./prospect disease-overlay --refresh-source",
        "rows": rows,
    }


def _load_source_rows(refresh_source: bool = False) -> dict[str, Any]:
    if refresh_source or not OUT_SOURCE.exists():
        source = extract_source_rows()
        OUT_SOURCE.write_text(json.dumps(source, indent=2) + "\n")
        return source
    return json.loads(OUT_SOURCE.read_text())


def _classify(row: dict[str, Any]) -> str:
    associations = _eligible_associations(row)
    if not associations:
        return "no_immune_or_hematologic_context"
    if any(assoc["has_genetic_association"] == "yes" for assoc in associations):
        return "immune_or_hematologic_genetic_context"
    return "immune_or_hematologic_non_genetic_context"


def _eligible_associations(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        assoc for assoc in row.get("selected_associations", [])
        if float(assoc["association_score"]) >= MIN_SELECTED_ASSOCIATION_SCORE
    ]


def _top_context(row: dict[str, Any]) -> dict[str, Any] | None:
    associations = _eligible_associations(row)
    if not associations:
        return None
    genetic = [assoc for assoc in associations if assoc["has_genetic_association"] == "yes"]
    pool = genetic or associations
    return max(pool, key=lambda assoc: assoc["association_score"])


def _with_overlay(row: dict[str, Any]) -> dict[str, Any]:
    overlay_class = _classify(row)
    top_context = _top_context(row)
    out = dict(row)
    out["overlay_class"] = overlay_class
    out["top_context"] = top_context
    out["selected_associations"] = _eligible_associations(row)
    out["has_external_association"] = "yes" if row.get("open_targets_association_count", 0) else "no"
    if top_context is None:
        out["why_it_matters"] = (
            "The campaign row remains a perturbation-first candidate with no selected immune or "
            "hematologic external context in this bounded Open Targets extract."
        )
    else:
        out["why_it_matters"] = (
            f"Open Targets attaches {top_context['disease_or_trait']} context to {row['gene']}, "
            "which helps frame follow-up assays without changing the Prospect status."
        )
    out["why_it_does_not_accept_state"] = (
        "External target-disease association is context only. Prospect accepted state still requires "
        "the frozen perturbation verifier and human signing path."
    )
    return out


def build_packet(refresh_source: bool = False) -> dict[str, Any]:
    source = _load_source_rows(refresh_source=refresh_source)
    rows = [_with_overlay(row) for row in source["rows"]]
    class_counts = Counter(row["overlay_class"] for row in rows)
    context_rows = [
        row for row in rows
        if row["overlay_class"] != "no_immune_or_hematologic_context"
    ]
    genetic_rows = [
        row for row in rows
        if row["overlay_class"] == "immune_or_hematologic_genetic_context"
    ]
    non_genetic_rows = [
        row for row in rows
        if row["overlay_class"] == "immune_or_hematologic_non_genetic_context"
    ]
    counts = {
        "campaign_rows": len(rows),
        "rows_with_external_context": sum(1 for row in rows if row["has_external_association"] == "yes"),
        "immune_or_hematologic_context": len(context_rows),
        "immune_or_hematologic_genetic_context": len(genetic_rows),
        "immune_or_hematologic_non_genetic_context": len(non_genetic_rows),
        "no_immune_or_hematologic_context": class_counts.get("no_immune_or_hematologic_context", 0),
    }
    return {
        "title": "Disease-genetics overlay packet",
        "status": "evidence_attached",
        "local_perturbation_status": "computationally_reproduced",
        "trust_boundary": "frozen_external_association_extract",
        "accepted_state_mutation": "none",
        "signed_frontier_root": _frontier_root(),
        "source": {
            "name": source["source"]["name"],
            "endpoint": source["source"]["endpoint"],
            "retrieved_at": source["retrieved_at"],
            "committed_extract": "examples/data/disease_genetics_source_rows.json",
            "source_status": source["status"],
            "source_rows": source["source_rows"],
        },
        "method": {
            "model_in_trust_path": "no",
            "accepted_state_mutation": "none",
            "replay_command": "./prospect disease-overlay",
            "source_regeneration_command": source["regeneration_command"],
            "classification": "fixed_terms_over_frozen_open_targets_associations",
        },
        "thresholds": {
            "min_selected_association_score": MIN_SELECTED_ASSOCIATION_SCORE,
        },
        "immune_or_hematologic_terms": IMMUNE_OR_HEMATOLOGIC_TERMS,
        "classes": [
            {
                "class": "immune_or_hematologic_genetic_context",
                "meaning": "Selected external context includes an immune or hematologic disease row with positive genetic association score.",
            },
            {
                "class": "immune_or_hematologic_non_genetic_context",
                "meaning": "Selected external context includes immune or hematologic disease context, but not positive genetic association support.",
            },
            {
                "class": "no_immune_or_hematologic_context",
                "meaning": "Open Targets has target-disease associations, but none selected by this bounded immune or hematologic filter.",
            },
        ],
        "counts": counts,
        "rows": rows,
        "context_rows": context_rows,
        "genetic_context_rows": genetic_rows,
        "limitations": (
            "This overlay attaches external disease context to campaign rows. It is not a therapeutic "
            "claim, clinical result, or accepted biological state."
        ),
    }


def _fmt_context(row: dict[str, Any]) -> tuple[str, str, str]:
    context = row["top_context"]
    if context is None:
        return "", "", ""
    return (
        context["disease_or_trait"],
        context["evidence_type"],
        str(context["association_score"]),
    )


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    lines = [
        "# Disease-genetics overlay packet",
        "",
        "Status: `evidence_attached`.",
        "",
        "No accepted state changes. This packet attaches external Open Targets disease context to campaign rows without changing Prospect state.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["method"]["replay_command"],
        "```",
        "",
        "Refresh source extract from Open Targets:",
        "",
        "```bash",
        packet["method"]["source_regeneration_command"],
        "```",
        "",
        "## Counts",
        "",
        f"- Campaign rows: {counts['campaign_rows']}",
        f"- Rows with external context: {counts['rows_with_external_context']}",
        f"- Immune or hematologic context: {counts['immune_or_hematologic_context']}",
        f"- Immune or hematologic genetic context: {counts['immune_or_hematologic_genetic_context']}",
        f"- Immune or hematologic non-genetic context: {counts['immune_or_hematologic_non_genetic_context']}",
        f"- No immune or hematologic context: {counts['no_immune_or_hematologic_context']}",
        "",
        "## Campaign Rows",
        "",
        "| Rank | Gene | Overlay class | Top context | Evidence type | Score |",
        "| ---: | --- | --- | --- | --- | ---: |",
    ]
    for row in packet["rows"]:
        disease, evidence_type, score = _fmt_context(row)
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['overlay_class']} | "
            f"{disease} | {evidence_type} | {score} |"
        )
    lines += [
        "",
        packet["limitations"],
    ]
    return "\n".join(lines) + "\n"


def write_packet(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
    refresh_source: bool = False,
) -> dict[str, Any]:
    packet = build_packet(refresh_source=refresh_source)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect disease-overlay")
    parser.add_argument("--refresh-source", action="store_true", help="refresh the source extract from Open Targets")
    parser.add_argument("--json", action="store_true", help="print the packet as JSON")
    args = parser.parse_args(argv)

    packet = write_packet(refresh_source=args.refresh_source)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_SOURCE}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"classified {packet['counts']['campaign_rows']} campaign rows by external disease context")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
