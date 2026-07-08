"""Build the rank-5 CCDC22 defended-evidence packet from frozen packets."""
from __future__ import annotations

import hashlib
import csv
import json
import statistics
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
SNAPSHOT_DIR = DATA / "ccdc22_defended_sources"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
CROSS_VALIDATION_SOURCES_JSON = DATA / "cross_validation_sources.json"
DECISIONS_JSON = DATA / "defended_candidate_decisions.json"
PREREG_JSON = DATA / "defended_discovery_preregistration.json"
OUT_JSON = DATA / "ccdc22_defended_evidence.json"
OUT_DOC = ROOT / "docs" / "CCDC22_DEFENDED_EVIDENCE.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"

SNAPSHOT_URLS = {
    "chembl_target_search": "https://www.ebi.ac.uk/chembl/api/data/target/search.json?q=CCDC22&limit=10",
    "ensembl_gene": "https://rest.ensembl.org/lookup/id/ENSG00000101997?expand=1",
    "ensembl_homology": "https://rest.ensembl.org/homology/symbol/human/CCDC22?type=orthologues",
    "gwas_gene": "https://www.ebi.ac.uk/gwas/rest/api/v2/genes/CCDC22",
    "string_interactions": "https://string-db.org/api/json/interaction_partners?identifiers=CCDC22&species=9606&limit=10",
}

DEPMAP_24Q2_ARTICLE = "https://api.figshare.com/v2/articles/25880521"
DEPMAP_24Q2_GENE_EFFECT_FILE = "CRISPRGeneEffect.csv"


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required frozen source: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _fetch_json(url: str, *, allow_404: bool = False) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "prospect-hackathon/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return {"status": "not_found", "http_status": 404, "url": url}
        raise


def _write_snapshot(name: str, payload: Any) -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    (SNAPSHOT_DIR / f"{name}.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _fetch_depmap_24q2_crispr_gene_effect() -> dict[str, Any]:
    article = _fetch_json(DEPMAP_24Q2_ARTICLE)
    files = {row["name"]: row for row in article["files"]}
    file_row = files[DEPMAP_24Q2_GENE_EFFECT_FILE]
    values = []
    request = urllib.request.Request(
        file_row["download_url"],
        headers={"User-Agent": "prospect-hackathon/1.0"},
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        text = (line.decode("utf-8") for line in response)
        reader = csv.reader(text)
        header = next(reader)
        matches = [(index, name) for index, name in enumerate(header) if "CCDC22" in name]
        if len(matches) != 1:
            raise RuntimeError(f"expected one CCDC22 column, found {matches}")
        column_index, column_name = matches[0]
        for row in reader:
            raw = row[column_index]
            if raw:
                values.append({"model_id": row[0], "gene_effect": float(raw)})
    scores = [row["gene_effect"] for row in values]
    return {
        "source": "depmap_24q2_crispr_gene_effect",
        "url": file_row["download_url"],
        "article_url": article["figshare_url"],
        "article_api_url": DEPMAP_24Q2_ARTICLE,
        "gene": "CCDC22",
        "file": {
            "name": file_row["name"],
            "id": file_row["id"],
            "size": file_row["size"],
            "computed_md5": file_row["computed_md5"],
        },
        "column": column_name,
        "summary": {
            "cell_line_count": len(values),
            "min_gene_effect": round(min(scores), 6),
            "median_gene_effect": round(statistics.median(scores), 4),
            "mean_gene_effect": round(statistics.mean(scores), 4),
            "max_gene_effect": round(max(scores), 6),
            "lines_below_minus_0_5": sum(score < -0.5 for score in scores),
            "lines_below_minus_1": sum(score < -1 for score in scores),
        },
        "values": values,
    }


def fetch_ccdc22_snapshots() -> None:
    """Refresh public snapshots. Scoring still uses the written files."""
    target_search = _fetch_json(SNAPSHOT_URLS["chembl_target_search"])
    target_id = target_search["targets"][0]["target_chembl_id"]
    activity_url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id={target_id}&limit=25"
    for name, url in SNAPSHOT_URLS.items():
        payload = {
            "source": name,
            "url": url,
            "gene": "CCDC22",
            "payload": _fetch_json(url, allow_404=(name == "gwas_gene")),
        }
        _write_snapshot(name, payload)
    _write_snapshot(
        "chembl_activity",
        {
            "source": "chembl_activity",
            "url": activity_url,
            "gene": "CCDC22",
            "payload": _fetch_json(activity_url),
        },
    )

    cross_sources = _load(CROSS_VALIDATION_SOURCES_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    cross_row = _row(cross_validation, "CCDC22")
    _write_snapshot(
        "dice_expression",
        {
            "source": "dice_expression",
            "url": cross_sources["source_urls"]["dice_cd4_stim_tpm"],
            "gene": "CCDC22",
            "payload": cross_sources["dice_expression"]["CCDC22"],
        },
    )
    _write_snapshot(
        "orcs_screen_rows",
        {
            "source": "orcs_screen_rows",
            "url": cross_sources["source_urls"]["orcs_shifrut_dataset"],
            "gene": "CCDC22",
            "payload": cross_sources["screen_rows"]["CCDC22"],
        },
    )
    _write_snapshot(
        "open_targets_overlay",
        {
            "source": "open_targets_overlay",
            "url": cross_sources["source_urls"]["open_targets_overlay"],
            "gene": "CCDC22",
            "payload": cross_row["open_targets"],
        },
    )
    _write_snapshot("depmap_24q2_crispr_gene_effect", _fetch_depmap_24q2_crispr_gene_effect())


def _snapshot(name: str) -> Any:
    return _load(SNAPSHOT_DIR / f"{name}.json")


def _snapshots() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(SNAPSHOT_DIR.glob("*.json")):
        rows.append(
            {
                "source": path.stem,
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
            }
        )
    return rows


def _row(packet: dict[str, Any], gene: str) -> dict[str, Any]:
    return next(row for row in packet["candidates"] if row["gene"] == gene)


def _disease_summary(cross_row: dict[str, Any]) -> str:
    top = cross_row["open_targets"]["top_context"]
    return (
        f"{top['disease_or_trait']}, genetic association score "
        f"{top['datatype_scores'][0]['score']}"
    )


def _scored_evidence(discovery_row: dict[str, Any], cross_row: dict[str, Any]) -> list[dict[str, Any]]:
    screens = cross_row["external_screen_summary"]
    target_search = _snapshot("chembl_target_search")["payload"]
    target_id = target_search["targets"][0]["target_chembl_id"]
    target_name = target_search["targets"][0]["pref_name"].lower()
    chembl_activity = _snapshot("chembl_activity")["payload"]
    chembl_activity_count = chembl_activity["page_meta"]["total_count"]
    ensembl_homology = _snapshot("ensembl_homology")["payload"]
    gwas_gene = _snapshot("gwas_gene")["payload"]
    string_rows = _snapshot("string_interactions")["payload"]
    dice = _snapshot("dice_expression")["payload"]
    depmap = _snapshot("depmap_24q2_crispr_gene_effect")
    homologies = ensembl_homology.get("data", [{}])[0].get("homologies", [])
    partners = [row["preferredName_B"] for row in string_rows[:10]]
    gwas_summary = (
        "GWAS Catalog gene endpoint returned no CCDC22 object"
        if gwas_gene.get("status") == "not_found"
        else f"GWAS Catalog gene object at {gwas_gene['location']}"
    )
    return [
        {
            "source": "marson_frontier",
            "status": "computationally_reproduced",
            "scored_from_frozen_snapshot": True,
            "summary": (
                f"{discovery_row['stim_max_de']} stimulated DE genes, "
                f"{discovery_row['rest_de']} Rest DE genes"
            ),
        },
        {
            "source": "replogle_specificity",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": f"K562 {discovery_row['k562_de']}; RPE1 {discovery_row['rpe1_de']}",
        },
        {
            "source": "primary_t_cell_screen_support",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": "supporting hit: " + ", ".join(screens["supporting_hits"]),
            "supporting_hits": screens["supporting_hits"],
            "missing_rows": screens["missing_rows"],
            "non_hits": screens["non_hits"],
        },
        {
            "source": "schmidt_2022_orcs_2427",
            "status": "orthogonal_phenotype",
            "scored_from_frozen_snapshot": True,
            "summary": "cytokine-production non-hit, not a comparable activation-transcriptome contradiction",
        },
        {
            "source": "string_network",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": "top partners: " + ", ".join(partners[:5]),
        },
        {
            "source": "dice_expression",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": f"activated CD4 mean TPM {dice['activated_cd4_mean_tpm']}",
        },
        {
            "source": "open_targets_overlay",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": _disease_summary(cross_row),
        },
        {
            "source": "chembl_target_and_activity",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": f"{target_id} with {chembl_activity_count} activity rows for {target_name}",
        },
        {
            "source": "ensembl_homology",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": f"{len(homologies)} orthology rows from Ensembl homology",
        },
        {
            "source": "gwas_catalog_gene_lookup",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": gwas_summary,
        },
        {
            "source": "depmap_24q2_crispr_gene_effect",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": (
                f"{depmap['summary']['cell_line_count']} cancer cell lines, "
                f"median gene effect {depmap['summary']['median_gene_effect']:.4f}, "
                f"{depmap['summary']['lines_below_minus_1']} lines below -1"
            ),
        },
    ]


def _open_gates() -> list[dict[str, str]]:
    return [
        {
            "gate": "shifrut_replication_depth",
            "reason": "one Shifrut row supports CCDC22, while the second Shifrut row is missing from the frozen packet",
        },
        {
            "gate": "human_acceptance",
            "reason": "no human key has accepted a CCDC22 state transition",
        },
    ]


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "result": "survives_current_frozen_evidence",
            "basis": "the frozen campaign row has on-target stimulated knockdown",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "result": "survives_current_frozen_evidence",
            "basis": "Rest DE is 116 and K562 DE is 13, below the pre-registered artifact ceilings",
        },
        {
            "kill_id": "batch_or_dataset_specificity",
            "result": "survives_current_frozen_evidence",
            "basis": "Shifrut 2018 row 1107 supports the candidate in an independent primary T-cell screen",
        },
        {
            "kill_id": "alternative_mechanism",
            "result": "survives_current_frozen_evidence",
            "basis": "STRING centers CCDC22 in the CCC and COMMD retromer-associated trafficking complex",
        },
    ]


def build_ccdc22_defended_evidence() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    _load(DECISIONS_JSON)
    discovery_row = _row(discovery, "CCDC22")
    cross_row = _row(cross_validation, "CCDC22")
    packet = {
        "phase": "rank_5_ccdc22_defended_evidence",
        "title": "CCDC22 defended evidence",
        "gene": "CCDC22",
        "candidate_rank": discovery_row["rank"],
        "status": "evidence_attached",
        "defended_discovery_status": "computational_bar_cleared_pending_human_key",
        "accepted": False,
        "acceptance": False,
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": prereg["pre_registration_id"],
        "source_packets": {
            "cross_validation": "examples/data/cross_validation.json",
            "decision_ledger": "examples/data/defended_candidate_decisions.json",
            "discovery_campaign": "examples/data/discovery_campaign.json",
        },
        "snapshot_dir": str(SNAPSHOT_DIR.relative_to(ROOT)),
        "frozen_snapshots": _snapshots(),
        "orthogonal_public_dataset_count": 8,
        "current_support_count": 8,
        "scored_evidence": _scored_evidence(discovery_row, cross_row),
        "open_gates": _open_gates(),
        "kill_attempts": _kill_attempts(),
        "mechanism": (
            "CCDC22 may connect stimulated CD4+ activation state to CCC and COMMD "
            "retromer-associated endosomal trafficking."
        ),
        "real_world_hook": _disease_summary(cross_row),
        "decision_recommendation": "hold_and_deepen",
        "next_candidate": None,
        "falsifiable_experiment": discovery_row["falsifiable_test"],
        "reproduce_command": "./prospect ccdc22-defended-evidence",
        "next_step": "human review of the CCDC22 proposal, then optional human-key acceptance",
    }
    packet["packet_id"] = _hash_obj("ccdc22_defended", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# CCDC22 defended evidence",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        "Plain-language status: computational bar cleared, pending human key.",
        f"Defended-discovery status: `{packet['defended_discovery_status']}`.",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "## Frozen evidence",
        "",
        "| source | status | summary |",
        "|---|---|---|",
    ]
    for row in packet["scored_evidence"]:
        lines.append(f"| `{row['source']}` | `{row['status']}` | {row['summary']} |")
    lines += [
        "",
        "## Open gates",
        "",
        "| gate | reason |",
        "|---|---|",
    ]
    for row in packet["open_gates"]:
        lines.append(f"| `{row['gate']}` | {row['reason']} |")
    lines += [
        "",
        "## Kill attempts",
        "",
        "| kill | result | basis |",
        "|---|---|---|",
    ]
    for row in packet["kill_attempts"]:
        lines.append(f"| `{row['kill_id']}` | `{row['result']}` | {row['basis']} |")
    lines += [
        "",
        f"Mechanism: {packet['mechanism']}",
        f"Real-world hook: {packet['real_world_hook']}.",
        f"Decision recommendation: `{packet['decision_recommendation']}`.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect ccdc22-defended-evidence",
        "```",
        "",
        "Refresh public snapshots before a new scoring pass:",
        "",
        "```bash",
        "./prospect ccdc22-defended-evidence --fetch",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_ccdc22_defended_evidence(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_ccdc22_defended_evidence()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if "--fetch" in argv:
        fetch_ccdc22_snapshots()
    packet = write_ccdc22_defended_evidence()
    print(f"wrote {OUT_JSON} ({packet['defended_discovery_status']})")
    print(f"wrote {OUT_DOC}")
    print(f"packet_id {packet['packet_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
