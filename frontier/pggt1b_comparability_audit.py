"""Build the frozen PGGT1B cross-study comparability audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ORCS_SNAPSHOT = ROOT / "examples" / "data" / "pggt1b_defended_sources" / "orcs_gene_tcell_rows.json"
REGISTRY_SEARCHES = ROOT / "examples" / "data" / "pggt1b_registry_searches.json"
OUT_JSON = ROOT / "examples" / "data" / "pggt1b_comparability_audit.json"
OUT_DOC = ROOT / "docs" / "PGGT1B_COMPARABILITY_AUDIT.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"
ORCS_SHA256 = "b217f04249e6a39eb7d9b0b622337004c9e50340a67f29e86eae546c33abff48"
REGISTRY_SEARCHES_SHA256 = "035bb3187b4827941c611f74b1a5934cb51ecc788a653ea99b6e3f5ed872c036"

SHIFRUT_CROPSEQ_TARGETS = (
    "ARID1A", "BTLA", "C10orf54", "CBLB", "CD3D", "CD5", "CDKN1B", "DGKA", "DGKZ",
    "HAVCR2", "LAG3", "LCP2", "MEF2D", "PDCD1", "RASA2", "SOCS1", "STAT6", "TCEB2",
    "TMEM222", "TNFRSF9",
)

SCHMIDT_PERTURBSEQ_TARGETS = (
    "ABCB10", "AKAP12", "ALX4", "APOBEC3C", "APOBEC3D", "APOL2", "ARHGDIB", "BICDL2",
    "CBY1", "CD2", "CD247", "CD27", "CD28", "CEACAM1", "CNR2", "DEF6", "DEPDC7",
    "EMP1", "EMP3", "EOMES", "FOSB", "FOSL1", "FOXD2", "FOXL2NB", "FOXQ1", "GATA3",
    "GRAP", "HELZ2", "IFNG", "IKZF3", "IL1R1", "IL2", "IL2RB", "IL2RG", "IL9R",
    "INPPL1", "IRX4", "ITPKA", "JMJD1C", "LAT", "LAT2", "LCP2", "LHX4", "LHX6",
    "LTBR", "MAP4K1", "MGST3", "MUC1", "NLRC3", "NOTCH1", "OTUD7A", "OTUD7B",
    "P2RY14", "PAPOLG", "PIK3AP1", "PLCG2", "PRDM1", "PRDM13", "PRKD2", "RAC2",
    "RELA", "SLA2", "TAGAP", "TBX21", "TCF7", "TNFRSF12A", "TNFRSF1A", "TNFRSF1B",
    "TNFRSF9", "TRAF3IP2", "TRIM21", "VAV1", "WT1",
)

SCREEN_EXPECTATIONS = {
    "1107": {"first_author": "Shifrut E (2018)", "hit_status": "hit", "rank": 1095, "total": 19108},
    "1109": {"first_author": "Shifrut E (2018)", "hit_status": "non_hit", "rank": 18667, "total": 19089},
    "2423": {"first_author": "Schmidt R (2022)", "hit_status": "non_hit", "rank": 8935, "total": 18920},
    "2424": {"first_author": "Schmidt R (2022)", "hit_status": "non_hit", "rank": 18016, "total": 18900},
    "2427": {"first_author": "Schmidt R (2022)", "hit_status": "non_hit", "rank": 4529, "total": 18894},
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _content_id(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "pggt1b_comparability_" + hashlib.sha256(body).hexdigest()[:16]


def _load_screen_rows() -> dict[str, dict[str, Any]]:
    if _sha256(ORCS_SNAPSHOT) != ORCS_SHA256:
        raise RuntimeError("PGGT1B ORCS snapshot does not match the frozen audit source")
    rows = {row["screen_id"]: row for row in json.loads(ORCS_SNAPSHOT.read_text())["rows"]}
    for screen_id, expected in SCREEN_EXPECTATIONS.items():
        row = rows.get(screen_id)
        if row is None:
            raise RuntimeError(f"missing frozen ORCS screen {screen_id}")
        for field, value in expected.items():
            if row[field] != value:
                raise RuntimeError(f"frozen ORCS screen {screen_id} changed field {field}")
    return rows


def _screen_record(row: dict[str, Any], readout: str) -> dict[str, Any]:
    return {
        "screen_id": row["screen_id"],
        "url": f"https://orcs.thebiogrid.org/Screen/{row['screen_id']}",
        "dataset_id": row["dataset_id"],
        "first_author": row["first_author"],
        "cell_line": row["cell_line"],
        "perturbation": row["library_type"],
        "readout": readout,
        "pggt1b_coverage": "covered",
        "hit_status": row["hit_status"],
        "rank": row["rank"],
        "total": row["total"],
        "typed_status": "orthogonal_phenotype",
        "comparability": "nonmatching_readout",
    }


def build_pggt1b_comparability_audit() -> dict[str, Any]:
    rows = _load_screen_rows()
    if _sha256(REGISTRY_SEARCHES) != REGISTRY_SEARCHES_SHA256:
        raise RuntimeError("PGGT1B registry search packet does not match the frozen audit source")
    registry_searches = json.loads(REGISTRY_SEARCHES.read_text())
    body: dict[str, Any] = {
        "schema_version": "prospect.pggt1b_comparability_audit.v1",
        "gene": "PGGT1B",
        "status": "evidence_attached",
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "audit_question": (
            "Does an independent public primary human T-cell dataset directly perturb PGGT1B and "
            "measure a matched stimulated activation transcriptome?"
        ),
        "source_files": [
            {
                "source_id": "biogrid_orcs_pggt1b_tcell_rows",
                "path": str(ORCS_SNAPSHOT.relative_to(ROOT)),
                "url": "https://orcs.thebiogrid.org/Gene/5229",
                "sha256": ORCS_SHA256,
                "bytes": ORCS_SNAPSHOT.stat().st_size,
            },
            {
                "source_id": "pggt1b_registry_searches",
                "path": str(REGISTRY_SEARCHES.relative_to(ROOT)),
                "sha256": REGISTRY_SEARCHES_SHA256,
                "bytes": REGISTRY_SEARCHES.stat().st_size,
                "derivation": "frozen Europe PMC, GEO, SRA, BioStudies, ORCS, and accession coverage audit",
            },
            {
                "source_id": "shifrut_gse119450_d1_no_stim_guide_assignments",
                "url": (
                    "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM3375nnn/GSM3375487/suppl/"
                    "GSM3375487_D1N_CellBC_sgRNA.csv.gz"
                ),
                "sha256": "5a64ffdc48c03466f30d6734112e671626f1cf77e12f140b3308c6a3bc3e663d",
                "bytes": 51063,
                "derivation": "unique gRNA.ID target labels from the public assignment table",
            },
            {
                "source_id": "schmidt_gse190604_guide_calls",
                "url": (
                    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE190nnn/GSE190604/suppl/"
                    "GSE190604_cellranger-guidecalls-aggregated-unfiltered.txt.gz"
                ),
                "sha256": "0ffd5a3050a69d013ddc09a43fae63642a7659cdb778f78c865e0829207e17b7c",
                "bytes": 999849,
                "derivation": "unique feature_call target labels from the public guide-call table",
            },
        ],
        "studies": [
            {
                "study_id": "shifrut_2018",
                "pmid": "30449619",
                "doi": "10.1016/j.cell.2018.10.024",
                "genome_wide_screens": [
                    _screen_record(rows["1107"], "CFSE-separated proliferation after TCR stimulation"),
                    _screen_record(rows["1109"], "CFSE-separated proliferation after TCR stimulation"),
                ],
                "transcriptomic_panel": {
                    "accession": "GSE119450",
                    "cell_system": "primary human CD8+ T cells from two donors",
                    "conditions": ["TCR stimulated", "not stimulated"],
                    "perturbation": "CRISPR knockout",
                    "readout": "single-cell transcriptome",
                    "guide_count": 48,
                    "gene_target_count": len(SHIFRUT_CROPSEQ_TARGETS),
                    "non_targeting_control_count": 8,
                    "gene_targets": list(SHIFRUT_CROPSEQ_TARGETS),
                    "pggt1b_targeted": False,
                    "typed_status": "not_assayed",
                    "comparability": "potentially_comparable_design_but_pggt1b_not_targeted",
                },
            },
            {
                "study_id": "schmidt_2022",
                "pmid": "35113687",
                "doi": "10.1126/science.abj4008",
                "genome_wide_screens": [
                    _screen_record(rows["2423"], "IL-2 protein accumulation after stimulation"),
                    _screen_record(rows["2424"], "IFN-gamma protein accumulation after stimulation"),
                    _screen_record(rows["2427"], "TNF-alpha protein accumulation after stimulation"),
                ],
                "transcriptomic_panel": {
                    "accession": "GSE190604",
                    "cell_system": "primary human T cells",
                    "conditions": ["resting", "restimulated"],
                    "perturbation": "CRISPR activation",
                    "readout": "single-cell transcriptome",
                    "target_label_count_in_public_guide_calls": len(SCHMIDT_PERTURBSEQ_TARGETS) + 1,
                    "gene_target_count": len(SCHMIDT_PERTURBSEQ_TARGETS),
                    "control_target_labels": ["NO-TARGET"],
                    "gene_targets": list(SCHMIDT_PERTURBSEQ_TARGETS),
                    "pggt1b_targeted": False,
                    "typed_status": "not_assayed",
                    "comparability": "transcriptomic_readout_but_pggt1b_not_targeted_and_opposite_perturbation_mode",
                },
            },
        ],
        "registry_searches": registry_searches,
        "determination": {
            "comparable_pggt1b_transcriptomic_reproduction_found": False,
            "batch_or_dataset_specificity_kill": "not_cleared",
            "status_after_audit": "evidence_attached",
            "statement": (
                "No independent public dataset in this audit directly perturbs PGGT1B and measures a "
                "matched stimulated activation transcriptome."
            ),
            "status_effects": [
                "Shifrut proliferation results remain orthogonal_phenotype, not transcriptomic reproduction.",
                "Schmidt cytokine-production results remain orthogonal_phenotype, not contradiction.",
                "Both transcriptomic panels type PGGT1B as not_assayed because their target manifests omit it.",
                "E-MTAB-13324, GSE171737/GSE271788, and GSE278572 also omit PGGT1B from primary-human-CD4 transcriptomic panels.",
                "GSE249595 uses Jurkat cells; GSE318876 uses an HIV-infection readout. Both remain orthogonal_phenotype.",
            ],
        },
        "stop_criteria": {
            "action": "stop_public_search_and_retain_evidence_attached",
            "resume_only_if_one_accession_meets_all": [
                "primary human CD4+ T cells",
                "direct PGGT1B loss-of-function with guide identity and on-target evidence",
                "matched stimulated and resting or unstimulated controls",
                "transcriptome-wide RNA readout linked to PGGT1B-perturbed cells",
                "at least two donors or independent biological replicates",
                "processed matrix, guide assignments, and metadata available without controlled access",
                "source files can be content-addressed and replayed deterministically",
            ],
            "nonqualifying_readouts": [
                "proliferation alone",
                "cytokine abundance alone",
                "FOXP3 abundance alone",
                "activation-marker abundance alone",
                "viral infection alone",
            ],
        },
    }
    body["audit_id"] = _content_id(body)
    return body


def render_markdown(packet: dict[str, Any]) -> str:
    studies = {study["study_id"]: study for study in packet["studies"]}
    shifrut = studies["shifrut_2018"]
    schmidt = studies["schmidt_2022"]
    lines = [
        "# PGGT1B comparability audit",
        "",
        "Status: `evidence_attached`. Accepted: `false`. Next: `human_signature_required`.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        "## Determination",
        "",
        packet["determination"]["statement"],
        "",
        "The frozen comparators do not clear the batch or dataset specificity kill. They also do not "
        "contradict the PGGT1B activation-transcriptome hypothesis because their PGGT1B readouts are "
        "nonmatching phenotypes. The two transcriptomic panels omit PGGT1B from their target manifests.",
        "",
        "## Coverage audit",
        "",
        "| study object | PGGT1B coverage | readout | typed status | determination |",
        "|---|---:|---|---|---|",
    ]
    for study in (shifrut, schmidt):
        for screen in study["genome_wide_screens"]:
            lines.append(
                f"| {study['study_id']} ORCS {screen['screen_id']} | yes | {screen['readout']} | "
                f"`{screen['typed_status']}` | {screen['hit_status']}, rank {screen['rank']} of {screen['total']} |"
            )
        panel = study["transcriptomic_panel"]
        lines.append(
            f"| {study['study_id']} {panel['accession']} | no | {panel['readout']} | "
            f"`{panel['typed_status']}` | PGGT1B absent from {panel['gene_target_count']}-gene target manifest |"
        )
    lines.extend([
        "",
        "Shifrut GSE119450 uses 48 guides: 40 guides across 20 genes and 8 non-targeting controls. "
        "It profiles stimulated and unstimulated primary human CD8+ T cells from two donors, but PGGT1B "
        "is not among the 20 gene targets.",
        "",
        "Schmidt GSE190604 contains 73 non-control target labels plus `NO-TARGET` in the public guide-call "
        "table. It profiles resting and restimulated primary human T cells using CRISPR activation, but "
        "PGGT1B is not among those target labels.",
        "",
        "## Source anchors",
        "",
        "- [Shifrut et al. 2018](https://pubmed.ncbi.nlm.nih.gov/30449619/): DOI 10.1016/j.cell.2018.10.024, [GEO GSE119450](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE119450).",
        "- [Schmidt et al. 2022](https://pubmed.ncbi.nlm.nih.gov/35113687/): DOI 10.1126/science.abj4008, [GEO GSE190604](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190604).",
        "- PGGT1B screen rows: [BioGRID ORCS gene 5229](https://orcs.thebiogrid.org/Gene/5229) and the frozen Prospect snapshot named in the JSON artifact.",
        "- Exact source URLs, byte sizes, SHA-256 hashes, and extraction rules are frozen in the JSON artifact.",
        "",
        "## Bounded registry search",
        "",
        "The frozen registry packet records exact queries over Europe PMC, NCBI GEO, NCBI SRA, EBI BioStudies, and BioGRID ORCS. No accession clears every stop criterion.",
        "",
        "| accession | system | readout | PGGT1B status | comparability |",
        "|---|---|---|---|---|",
    ])
    for row in packet["registry_searches"]["candidate_accession_audit"]:
        lines.append(
            f"| {row['accession']} | {row['system']} | {row['readout']} | `{row['typed_status']}` | {row['comparability']} |"
        )
    lines.extend([
        "",
        "## Stop criteria",
        "",
        "Stop the public search and retain `evidence_attached` unless one accession meets every criterion:",
        "",
    ])
    lines.extend(f"- {criterion}." for criterion in packet["stop_criteria"]["resume_only_if_one_accession_meets_all"])
    lines.extend([
        "",
        "Proliferation, cytokine abundance, FOXP3 abundance, or activation-marker abundance alone remains "
        "`orthogonal_phenotype`. Sparse target-manifest coverage remains `not_assayed`.",
        "",
        "## Rebuild",
        "",
        "```bash",
        "python frontier/pggt1b_comparability_audit.py --check",
        "python -m pytest tests/test_pggt1b_comparability_audit.py -q",
        "```",
        "",
    ])
    return "\n".join(lines)


def write_audit() -> dict[str, Any]:
    packet = build_pggt1b_comparability_audit()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    OUT_DOC.write_text(render_markdown(packet))
    return packet


def check_audit() -> None:
    packet = build_pggt1b_comparability_audit()
    expected_json = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    expected_doc = render_markdown(packet)
    if OUT_JSON.read_text() != expected_json or OUT_DOC.read_text() != expected_doc:
        raise SystemExit("PGGT1B comparability audit artifacts are stale")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when committed artifacts are stale")
    args = parser.parse_args()
    if args.check:
        check_audit()
        print(f"ok {OUT_JSON.relative_to(ROOT)}")
    else:
        packet = write_audit()
        print(packet["audit_id"])
