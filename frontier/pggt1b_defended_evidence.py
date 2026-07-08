"""Build the rank-1 PGGT1B defended-evidence packet from frozen snapshots."""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
SNAPSHOT_DIR = DATA / "pggt1b_defended_sources"
OUT_JSON = DATA / "pggt1b_defended_evidence.json"
OUT_DOC = ROOT / "docs" / "PGGT1B_DEFENDED_EVIDENCE.md"

DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
CROSS_VALIDATION_SOURCES_JSON = DATA / "cross_validation_sources.json"
PREREG_JSON = DATA / "defended_discovery_preregistration.json"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"

SNAPSHOT_URLS = {
    "chembl_target": "https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL4135.json",
    "chembl_activity": "https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL4135&limit=25",
    "ensembl_gene": "https://rest.ensembl.org/lookup/id/ENSG00000164219?expand=1",
    "ensembl_homology": "https://rest.ensembl.org/homology/symbol/human/PGGT1B?type=orthologues",
    "gwas_gene": "https://www.ebi.ac.uk/gwas/rest/api/v2/genes/PGGT1B",
    "string_interactions": "https://string-db.org/api/json/interaction_partners?identifiers=PGGT1B&species=9606&limit=10",
}


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


def _fetch_json(url: str) -> Any:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def _write_snapshot(name: str, payload: Any) -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    (SNAPSHOT_DIR / f"{name}.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def fetch_pggt1b_snapshots() -> None:
    """Refresh public snapshots. Scoring still uses the written files."""
    for name, url in SNAPSHOT_URLS.items():
        payload = {
            "source": name,
            "url": url,
            "gene": "PGGT1B",
            "payload": _fetch_json(url),
        }
        _write_snapshot(name, payload)

    cross_sources = _load(CROSS_VALIDATION_SOURCES_JSON)
    _write_snapshot(
        "dice_expression",
        {
            "source": "dice_expression",
            "url": cross_sources["source_urls"]["dice_cd4_stim_tpm"],
            "gene": "PGGT1B",
            "payload": cross_sources["dice_expression"]["PGGT1B"],
        },
    )
    _write_snapshot(
        "orcs_screen_rows",
        {
            "source": "orcs_screen_rows",
            "url": cross_sources["source_urls"]["orcs_shifrut_dataset"],
            "gene": "PGGT1B",
            "payload": cross_sources["screen_rows"]["PGGT1B"],
        },
    )
    _write_snapshot(
        "depmap_access",
        {
            "source": "depmap_dependency",
            "url": "https://depmap.org/portal/download/custom/",
            "gene": "PGGT1B",
            "status": "access_limited",
            "why_unscored": (
                "the public portal route returned a browser challenge, so no dependency score is frozen"
            ),
        },
    )


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


def _candidate_rows() -> tuple[dict[str, Any], dict[str, Any]]:
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    discovery_row = next(row for row in discovery["candidates"] if row["gene"] == "PGGT1B")
    cross_row = next(row for row in cross_validation["candidates"] if row["gene"] == "PGGT1B")
    return discovery_row, cross_row


def _scored_evidence(discovery_row: dict[str, Any], cross_row: dict[str, Any]) -> list[dict[str, Any]]:
    chembl_target = _snapshot("chembl_target")["payload"]
    chembl_activity = _snapshot("chembl_activity")["payload"]
    ensembl_homology = _snapshot("ensembl_homology")["payload"]
    gwas_gene = _snapshot("gwas_gene")["payload"]
    string_rows = _snapshot("string_interactions")["payload"]
    dice = _snapshot("dice_expression")["payload"]
    orcs = _snapshot("orcs_screen_rows")["payload"]

    chembl_activities = chembl_activity.get("activities", [])
    homologies = ensembl_homology.get("data", [{}])[0].get("homologies", [])
    string_partners = [row["preferredName_B"] for row in string_rows[:10]]
    return [
        {
            "source": "marson_frontier",
            "status": "computationally_reproduced",
            "scored_from_frozen_snapshot": True,
            "summary": (
                f"{discovery_row['stim_max_de']} stimulated DE genes, "
                f"{discovery_row['rest_de']} Rest DE genes, K562 {discovery_row['k562_de']}"
            ),
        },
        {
            "source": "shifrut_2018_orcs_1107",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": f"ORCS hit row with rank {orcs['shifrut_2018_1107']['rank']}",
        },
        {
            "source": "schmidt_2022_orcs_2427",
            "status": "orthogonal_phenotype",
            "scored_from_frozen_snapshot": True,
            "summary": "cytokine-production non-hit, not a comparable activation-transcriptome contradiction",
        },
        {
            "source": "string_interaction_partners",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": "top partners: " + ", ".join(string_partners[:5]),
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
            "summary": cross_row["open_targets"]["overlay_class"],
        },
        {
            "source": "chembl_target_and_activity",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": True,
            "summary": (
                f"{chembl_target['target_chembl_id']} with {len(chembl_activities)} "
                "activity rows against geranylgeranyl transferase type-1 subunit beta"
            ),
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
            "summary": f"GWAS Catalog gene object at {gwas_gene['location']}",
        },
    ]


def _unscored_or_blocked_sources() -> list[dict[str, Any]]:
    depmap = _snapshot("depmap_access")
    return [
        {
            "source": "depmap_dependency",
            "status": "evidence_attached",
            "scored_from_frozen_snapshot": False,
            "why_unscored": depmap["why_unscored"],
            "required_next": "freeze a public DepMap dependency table or a bounded PGGT1B extract",
        }
    ]


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "result": "survives_current_frozen_evidence",
            "basis": "Marson row has on-target stimulated knockdown and large stimulated effect",
            "missing": "guide-level off-target audit would strengthen this kill",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "result": "not_cleared",
            "basis": "Replogle K562 is low, but the registered DepMap dependency kill is not scored",
            "missing": "DepMap dependency score",
        },
        {
            "kill_id": "batch_or_dataset_specificity",
            "result": "not_cleared",
            "basis": "Shifrut 1107 supports PGGT1B, Schmidt is an orthogonal phenotype",
            "missing": "additional comparable primary T-cell screen",
        },
        {
            "kill_id": "alternative_mechanism",
            "result": "survives_current_frozen_evidence",
            "basis": "STRING and ChEMBL point to geranylgeranylation rather than an unrelated marker-only explanation",
            "missing": "direct substrate-level assay remains wet-lab work",
        },
    ]


def build_pggt1b_defended_evidence() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    discovery_row, cross_row = _candidate_rows()
    evidence = _scored_evidence(discovery_row, cross_row)
    blocked = _unscored_or_blocked_sources()
    packet = {
        "phase": "rank_1_pggt1b_defended_evidence",
        "title": "PGGT1B defended evidence",
        "gene": "PGGT1B",
        "status": "evidence_attached",
        "defended_discovery_status": "not_cleared_full_bar",
        "accepted": False,
        "acceptance": False,
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": prereg["pre_registration_id"],
        "candidate_rank": discovery_row["rank"],
        "snapshot_dir": str(SNAPSHOT_DIR.relative_to(ROOT)),
        "frozen_snapshots": _snapshots(),
        "orthogonal_public_dataset_count": sum(
            1 for row in evidence if row["source"] != "marson_frontier"
        ),
        "access_limited_public_dataset_count": len(blocked),
        "scored_evidence": evidence,
        "unscored_or_blocked_sources": blocked,
        "mechanism": (
            "PGGT1B encodes the beta subunit of geranylgeranyl transferase I. The current "
            "hypothesis is that perturbing this enzyme changes stimulated CD4+ activation by "
            "altering prenylation-dependent small-GTPase and immune-synapse traffic."
        ),
        "real_world_hook": (
            "ChEMBL has target and activity rows for geranylgeranyl transferase type-1 subunit beta. "
            "This is a druggability hook, not a therapeutic claim."
        ),
        "kill_attempts": _kill_attempts(),
        "falsifiable_experiment": {
            "system": "stimulated primary human CD4+ T cells",
            "perturbation": "PGGT1B CRISPRi with non-targeting, FNTA or FNTB pathway, and viability controls",
            "refutes_if": (
                "adequate PGGT1B knockdown produces no candidate-specific activation-program shift "
                "at 8h or 48h, or the same effect appears in non-immune controls"
            ),
        },
        "reproduce_command": "./prospect pggt1b-defended-evidence",
        "next_step": "freeze DepMap dependency and one more comparable primary T-cell screen before claiming the full bar",
    }
    packet["packet_id"] = _hash_obj("pggt1b_defended", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# PGGT1B defended evidence",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only.",
        "",
        f"Defended-discovery status: `{packet['defended_discovery_status']}`.",
        "Plain-language status: not cleared full bar.",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "This packet does not accept PGGT1B as settled biology. It records the current frozen evidence for the rank-1 candidate and the exact gaps that keep it below the full pre-registered bar.",
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
        "## Unscored or blocked sources",
        "",
        "| source | reason | next step |",
        "|---|---|---|",
    ]
    for row in packet["unscored_or_blocked_sources"]:
        lines.append(f"| `{row['source']}` | {row['why_unscored']} | {row['required_next']} |")
    lines += [
        "",
        "## Kill attempts",
        "",
        "| kill | result | missing |",
        "|---|---|---|",
    ]
    for row in packet["kill_attempts"]:
        lines.append(f"| `{row['kill_id']}` | `{row['result']}` | {row['missing']} |")
    lines += [
        "",
        "Mechanism: " + packet["mechanism"],
        "",
        "Real-world hook: " + packet["real_world_hook"],
        "",
        "Falsifiable experiment: " + packet["falsifiable_experiment"]["refutes_if"],
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect pggt1b-defended-evidence",
        "```",
        "",
        "Refresh public snapshots before a new scoring pass:",
        "",
        "```bash",
        "./prospect pggt1b-defended-evidence --fetch",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_pggt1b_defended_evidence(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_pggt1b_defended_evidence()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if "--fetch" in argv:
        fetch_pggt1b_snapshots()
    packet = write_pggt1b_defended_evidence()
    print(f"wrote {OUT_JSON} ({packet['defended_discovery_status']})")
    print(f"wrote {OUT_DOC}")
    print(f"packet_id {packet['packet_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
