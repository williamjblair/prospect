"""Build the verifier breadth and coverage packet from frozen substrates."""
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from receipt.acceptance_service import build_submission_result
from receipt.causal_bridge import build_claude_science_packet
from receipt.substrate_router import DATA, ORCS_TCELL, artifact_hashes, clear_caches

OUT_JSON = DATA / "substrate_coverage_report.json"
OUT_DOC = ROOT / "docs" / "SUBSTRATE_COVERAGE.md"
ORCS_DATATABLE_URL = "https://orcs.thebiogrid.org/scripts/datatableTools.php"
NCBI_GENE_URL = "https://clinicaltables.nlm.nih.gov/api/ncbi_genes/v3/search"


def _clean_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(text).split())


def _orcs_link_id(pattern: str, value: str) -> str | None:
    match = re.search(pattern, value)
    return match.group(1) if match else None


def _orcs_rank(value: str) -> dict[str, int | None]:
    cleaned = _clean_html(value)
    match = re.search(r"#\s*([0-9,]+)\s*/\s*([0-9,]+)", cleaned)
    if not match:
        return {"rank": None, "total": None}
    return {
        "rank": int(match.group(1).replace(",", "")),
        "total": int(match.group(2).replace(",", "")),
    }


def _gene_id(symbol: str) -> str | None:
    url = NCBI_GENE_URL + "?" + urllib.parse.urlencode(
        {"terms": symbol, "df": "Symbol,GeneID,description", "sf": "Symbol,Synonyms", "maxList": 5}
    )
    request = urllib.request.Request(url, headers={"User-Agent": "prospect-hackathon/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode())
    for row in data[3]:
        if str(row[0]).upper() == symbol.upper():
            return str(row[1])
    return None


def _fetch_orcs_rows(symbol: str, gene_id: str | None) -> dict[str, Any]:
    if not gene_id:
        return {"gene": symbol, "gene_id": None, "records_filtered": 0, "rows": [], "mapping_status": "unmapped"}
    payload = {
        "draw": 1,
        "columns": [],
        "order": [{"column": 9, "dir": "asc"}, {"column": 10, "dir": "asc"}],
        "start": 0,
        "length": 100,
        "search": {"value": "T cell", "regex": False},
        "tool": "serverSideRows",
        "totalRecords": "1417",
        "checkedBoxes": [],
        "identifierValue": gene_id,
        "identifierType": "gene",
        "type": "gene",
    }
    form = payload.copy()
    form["expData"] = json.dumps(payload)
    request = urllib.request.Request(
        ORCS_DATATABLE_URL,
        data=urllib.parse.urlencode(form).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "prospect-hackathon/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode())
    rows = []
    for row in body.get("data", []):
        rank = _orcs_rank(row[10])
        rows.append({
            "dataset_id": _orcs_link_id(r"/Dataset/(\d+)", row[0]),
            "screen_id": _orcs_link_id(r"/Screen/(\d+)", row[1]),
            "first_author": _clean_html(row[0]),
            "screen_name": _clean_html(row[1]),
            "cell_type": _clean_html(row[2]),
            "cell_line": _clean_html(row[3]),
            "phenotype": _clean_html(row[4]),
            "condition": _clean_html(row[5]),
            "library_type": _clean_html(row[6]),
            "enzyme": _clean_html(row[7]),
            "analysis": _clean_html(row[8]),
            "hit_status": "hit" if "Yes" in _clean_html(row[9]) else "non_hit",
            "rank": rank["rank"],
            "total": rank["total"],
            "details": _clean_html(row[11]),
        })
    return {
        "gene": symbol,
        "gene_id": gene_id,
        "records_filtered": int(body.get("recordsFiltered") or 0),
        "query": payload,
        "rows": rows,
        "mapping_status": "mapped",
    }


def fetch_orcs_signature_rows() -> dict[str, Any]:
    packet = build_claude_science_packet()
    genes = [row["gene"] for row in packet["verdicts"]]
    return {
        "source": "BioGRID ORCS datatableTools plus NIH NCBI Genes lookup",
        "source_urls": {
            "orcs": ORCS_DATATABLE_URL,
            "ncbi_genes": NCBI_GENE_URL,
        },
        "query": "T cell rows for the real Claude Science Sade-Feldman signature genes",
        "genes": [_fetch_orcs_rows(gene, _gene_id(gene)) for gene in genes],
    }


def build_packet() -> dict[str, Any]:
    claude_packet = build_claude_science_packet()
    k562 = build_submission_result(
        "MED19\nBCL10\nIL7R",
        filename="k562_markers.txt",
        source_name="external_k562_screen",
        claim_context="k562",
    )
    rpe1 = build_submission_result(
        "SMN2\nWARS\nIL7R",
        filename="rpe1_markers.txt",
        source_name="external_rpe1_screen",
        claim_context="rpe1",
    )
    return {
        "packet_id": "substrate_coverage_report_v1",
        "accepted": False,
        "next": "human_signature_required",
        "status": "evidence_attached",
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        "coverage": {
            "sade_feldman_signature": claude_packet["prospect"]["coverage_report"],
        },
        "route_examples": {
            "tcell_immunotherapy": claude_packet["prospect"]["route"],
            "k562": k562["prospect"]["route"],
            "rpe1": rpe1["prospect"]["route"],
        },
        "typed_counts": {
            "sade_feldman_signature": claude_packet["prospect"]["typed_status_counts"],
            "k562_example": k562["prospect"]["typed_status_counts"],
            "rpe1_example": rpe1["prospect"]["typed_status_counts"],
        },
        "artifacts": artifact_hashes(),
        "commands": {
            "build": "./prospect substrate-coverage",
            "serve": "./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service",
            "k562_submit": "curl -s http://127.0.0.1:8130/submit -H 'content-type: application/json' -d '{\"claim_context\":\"k562\",\"text\":\"MED19\\nBCL10\\nIL7R\"}'",
        },
    }


def write_outputs(packet: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    cov = packet["coverage"]["sade_feldman_signature"]
    lines = [
        "# Substrate coverage report",
        "",
        "Prospect now routes external claims to a contextually appropriate frozen substrate.",
        "The route is still proposal only: `accepted=false`, `human_signature_required`.",
        "",
        "Ceiling: computation over released data, not wet-lab or clinical truth.",
        "",
        "## Sade-Feldman signature coverage",
        "",
        f"- Before ORCS primary T-cell context: {cov['before']['not_assayed']} of {cov['before']['genes']} genes were `not_assayed` in the primary Marson CD4+ substrate.",
        f"- After frozen ORCS primary T-cell context: {cov['after']['not_assayed']} of {cov['after']['genes']} genes remain uncovered by primary T-cell perturbation context.",
        f"- ORCS primary T-cell covered genes: {', '.join(cov['substrates']['orcs_primary_tcell']['covered_not_assayed_genes'])}.",
        "",
        "The ORCS rows shrink uncovered biology. They do not silently accept state, and they stay orthogonal context unless the submitted claim is about that phenotype.",
        "",
        "## Route examples",
        "",
        f"- T-cell or immunotherapy claim: `{packet['route_examples']['tcell_immunotherapy']['primary_substrate']}`.",
        f"- K562 claim: `{packet['route_examples']['k562']['primary_substrate']}`.",
        f"- RPE1 claim: `{packet['route_examples']['rpe1']['primary_substrate']}`.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "./prospect substrate-coverage",
        "```",
    ]
    OUT_DOC.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-orcs", action="store_true", help="refresh the frozen ORCS reduced table")
    args = parser.parse_args(argv)
    if args.fetch_orcs:
        ORCS_TCELL.write_text(json.dumps(fetch_orcs_signature_rows(), indent=2, sort_keys=True) + "\n")
        clear_caches()
    packet = build_packet()
    write_outputs(packet)
    cov = packet["coverage"]["sade_feldman_signature"]
    print(
        "wrote examples/data/substrate_coverage_report.json "
        f"(Sade-Feldman not_assayed {cov['before']['not_assayed']} -> {cov['after']['not_assayed']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
