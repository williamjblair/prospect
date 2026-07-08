"""Build the defended-discovery pre-registration packet."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
FRONTIER_SIG_JSON = ROOT / "frontier" / "frontier.sig.json"
OUT_JSON = DATA / "defended_discovery_preregistration.json"
OUT_DOC = ROOT / "docs" / "DEFENDED_DISCOVERY_PREREGISTRATION.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"


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


def _ranked_candidates(discovery: dict[str, Any], cross_validation: dict[str, Any]) -> list[dict[str, Any]]:
    cross_by_gene = {row["gene"]: row for row in cross_validation["candidates"]}
    rows = []
    for candidate in discovery["candidates"]:
        cross = cross_by_gene[candidate["gene"]]
        rows.append(
            {
                "rank": candidate["rank"],
                "gene": candidate["gene"],
                "status": "evidence_attached",
                "accepted": False,
                "trust_boundary": "proposal_only",
                "marson_stim_max_de": candidate["stim_max_de"],
                "strongest_condition": candidate["strongest_condition"],
                "rest_de": candidate["rest_de"],
                "k562_de": candidate["k562_de"],
                "rpe1_de": candidate["rpe1_de"],
                "score": candidate["score"],
                "known_regulon_targets": candidate["known_regulon_targets"],
                "standard_t_cell_annotation": candidate["standard_t_cell_annotation"],
                "current_external_screen_hits": cross["external_screen_summary"]["supporting_hits"],
                "current_orthogonal_phenotypes": cross["external_screen_summary"][
                    "orthogonal_phenotypes"
                ],
                "current_comparable_contradictions": cross["external_screen_summary"][
                    "contradictions"
                ],
                "current_context_tier": cross["tier"],
            }
        )
    return rows


def _attached_artifacts(discovery: dict[str, Any], cross_validation: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, rel in discovery["source_artifacts"].items():
        rows.append(
            {
                "artifact": key,
                "path": rel,
                "sha256": discovery["source_artifact_hashes"][key],
                "frozen": True,
                "role": "phase_1_candidate_filter",
            }
        )
    for path, role in [
        ("examples/data/discovery_campaign.json", "ranked_candidate_set"),
        ("examples/data/cross_validation_sources.json", "phase_2_external_context_sources"),
        ("examples/data/cross_validation.json", "phase_2_external_context_packet"),
        ("frontier/frontier.sig.json", "accepted_frontier_root_reference"),
    ]:
        full = ROOT / path
        rows.append(
            {
                "artifact": Path(path).stem,
                "path": path,
                "sha256": _sha256(full),
                "frozen": True,
                "role": role,
            }
        )
    rows.append(
        {
            "artifact": "phase_2_source_bundle",
            "path": cross_validation["source_bundle_path"],
            "sha256": cross_validation["source_bundle_id"],
            "frozen": True,
            "role": "content-addressed_external_context_bundle",
        }
    )
    return rows


def _planned_dataset_slots() -> list[dict[str, Any]]:
    return [
        {
            "slot": "additional_primary_t_cell_crispr_screen",
            "minimum_role": "comparable activation or immune-function perturbation screen",
            "candidate_sources": [
                {
                    "name": "Shifrut et al. 2018 Cell SLICE screen",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/30449619/",
                    "current_use": "already attached where ORCS rows exist",
                },
                {
                    "name": "Schmidt et al. 2022 Science primary T-cell CRISPRa or CRISPRi screens",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/35113687/",
                    "current_use": "orthogonal unless the specific readout is comparable",
                },
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "gwas_catalog_immune_traits",
            "minimum_role": "immune-trait disease-genetics hook",
            "candidate_sources": [
                {
                    "name": "NHGRI-EBI GWAS Catalog REST API v2",
                    "url": "https://www.ebi.ac.uk/gwas/rest/api/v2/docs",
                }
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "depmap_dependency",
            "minimum_role": "broad dependency or proliferation artifact kill",
            "candidate_sources": [
                {
                    "name": "Broad DepMap CRISPR dependency downloads",
                    "url": "https://depmap.org/",
                },
                {
                    "name": "Sanger DepMap CRISPR knockout processed data",
                    "url": "https://depmap.sanger.ac.uk/documentation/datasets/wg-crispr-knockout/",
                },
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "protein_interaction_network",
            "minimum_role": "mechanistic coherence or alternative-mechanism kill",
            "candidate_sources": [
                {
                    "name": "STRING functional protein association API",
                    "url": "https://string-db.org/help/api/",
                }
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "immune_subset_expression_atlas",
            "minimum_role": "immune-subset expression support or cell-context kill",
            "candidate_sources": [
                {
                    "name": "DICE immune cell expression downloads",
                    "url": "https://dice-database.org/downloads",
                }
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "evolutionary_conservation",
            "minimum_role": "orthology or conservation context, not acceptance by itself",
            "candidate_sources": [
                {
                    "name": "Ensembl Compara homology API",
                    "url": "https://rest.ensembl.org/",
                }
            ],
            "freeze_required_before_scoring": True,
        },
        {
            "slot": "drugbank_or_chembl_target_hook",
            "minimum_role": "druggability hook or absence of targetable chemistry",
            "candidate_sources": [
                {
                    "name": "ChEMBL data web services",
                    "url": "https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services",
                }
            ],
            "freeze_required_before_scoring": True,
        },
    ]


def _win_condition() -> dict[str, Any]:
    return {
        "minimum_orthogonal_public_datasets": 5,
        "required_rungs": [
            {
                "rung": "novelty",
                "criterion": (
                    "strong stimulated Marson CD4+ activation effect, absent from CollecTRI "
                    "and standard T-cell regulator annotations"
                ),
            },
            {
                "rung": "frozen_replay",
                "criterion": "re-derives from frozen Prospect packets at zero drift",
            },
            {
                "rung": "cell_type_specificity",
                "criterion": "not a broad Replogle K562 or RPE1 effect under the registered ceiling",
            },
            {
                "rung": "five_orthogonal_public_datasets",
                "criterion": (
                    "at least five frozen public comparator datasets support the candidate or "
                    "establish the honest limit of the claim"
                ),
            },
            {
                "rung": "phenotype_comparability",
                "criterion": "agreement or contradiction can be assigned only after readout comparability is documented",
            },
            {
                "rung": "mechanism",
                "criterion": "a specific mechanism names pathway, molecule class, and expected activation readout",
            },
            {
                "rung": "real_world_hook",
                "criterion": "drug target, disease-genetics link, or named consensus correction",
            },
            {
                "rung": "falsifiable_experiment",
                "criterion": "one CRISPRi experiment in stimulated primary human CD4+ cells would refute the hypothesis",
            },
        ],
    }


def _comparability_rules() -> dict[str, Any]:
    return {
        "default_noncomparable_status": "orthogonal_phenotype",
        "agreement_requires": [
            "same perturbed gene",
            "primary human T-cell or justified immune-cell context",
            "activation-regulation readout or a stated bridge to activation-transcriptome breadth",
            "direction and timepoint interpretable against the Marson stimulated phenotype",
        ],
        "contradiction_requires": [
            "same perturbed gene",
            "comparable phenotype and assay direction",
            "adequate perturbation evidence in the comparator",
            "the comparator's null or opposite effect directly tests the active claim",
        ],
        "locked_examples": {
            "schmidt_2022_2427": {
                "status": "orthogonal_phenotype",
                "reason": (
                    "Schmidt 2022 calls cytokine-production regulators, while the Marson lane "
                    "scores activation-transcriptome breadth. A non-hit does not contradict "
                    "the broader Marson claim unless the claim is narrowed to cytokine output."
                ),
            }
        },
    }


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "independent_axis": "perturbation quality and guide behavior",
            "candidate_fails_if": (
                "the Marson effect is driven by failed knockdown calls, one unstable guide, "
                "off-target behavior, or a missing on-target stimulated perturbation"
            ),
            "evidence_needed": "guide-level or released perturbation-quality fields where available",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "independent_axis": "broad dependency outside the CD4+ activation setting",
            "candidate_fails_if": (
                "Replogle, DepMap, or another frozen dependency source shows broad growth or "
                "housekeeping behavior that explains the activation signature better than immune regulation"
            ),
            "evidence_needed": "Replogle K562/RPE1 plus frozen DepMap dependency scores",
        },
        {
            "kill_id": "batch_or_dataset_specificity",
            "independent_axis": "replication across public datasets and assay contexts",
            "candidate_fails_if": (
                "a comparable primary T-cell screen or donor-aware public dataset directly tests "
                "the activation-regulator claim and shows no compatible effect"
            ),
            "evidence_needed": "at least one comparable primary T-cell perturbation comparator",
        },
        {
            "kill_id": "alternative_mechanism",
            "independent_axis": "simpler biological explanation",
            "candidate_fails_if": (
                "network, expression, disease, or chemistry evidence supports a better explanation, "
                "such as downstream effector labeling, activation-state marker behavior, or another pathway node"
            ),
            "evidence_needed": "STRING or BioGRID, DICE or equivalent, GWAS Catalog, and ChEMBL or DrugBank",
        },
    ]


def _falsifiable_experiment_template() -> dict[str, Any]:
    return {
        "system": "stimulated primary human CD4+ T cells",
        "perturbation": "CRISPRi knockdown of the candidate gene, with non-targeting and pathway controls",
        "readouts": [
            "target knockdown quality",
            "activation-marker flow cytometry",
            "targeted RNA-seq or Perturb-seq at 8h and 48h",
            "cell viability and proliferation",
        ],
        "refutes_if": (
            "on-target knockdown is adequate but the stimulated activation program, marker readouts, "
            "and viability controls show no candidate-specific activation-regulator effect"
        ),
    }


def build_defended_discovery_preregistration() -> dict[str, Any]:
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    frontier_sig = _load(FRONTIER_SIG_JSON)
    root = frontier_sig["root"]
    ranked_candidates = _ranked_candidates(discovery, cross_validation)
    base = {
        "phase": "defended_discovery_preregistration",
        "title": "Defended discovery pre-registration",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted": False,
        "honest_ceiling": HONEST_CEILING,
        "frontier_root": root,
        "candidate_set_id": discovery["candidate_set_id"],
        "candidate_count": len(ranked_candidates),
        "ranked_candidates": ranked_candidates,
        "win_condition": _win_condition(),
        "dataset_freeze": {
            "rule": "no new public comparator can score a candidate until its fetched payload is stored and hashed",
            "attached_frozen_artifacts": _attached_artifacts(discovery, cross_validation),
            "planned_public_dataset_slots": _planned_dataset_slots(),
        },
        "comparable_phenotype_rules": _comparability_rules(),
        "pre_registered_kill_attempts": _kill_attempts(),
        "failure_policy": (
            "A candidate is removed from the defended-discovery lane if any pre-registered kill "
            "criterion is met. The kill threshold cannot be edited after this packet id is committed."
        ),
        "goalpost_policy": (
            "candidate fails if any pre-registered kill criterion is met; thresholds cannot change "
            "after pre_registration_id is committed"
        ),
        "falsifiable_experiment_template": _falsifiable_experiment_template(),
        "pre_registered_on": "2026-07-08",
        "reproduce_command": "./prospect defended-discovery-preregister",
        "next_step": "human_signature_required before any accepted-state transition; then freeze external datasets",
    }
    base["pre_registration_id"] = _hash_obj("prereg", base)
    base["signature_scope"] = "content seal only, not accepted frontier state"
    base["content_signature"] = _hash_obj(
        "prereg_sig",
        {
            "frontier_root": root,
            "candidate_set_id": base["candidate_set_id"],
            "pre_registration_id": base["pre_registration_id"],
            "ranked_genes": [row["gene"] for row in ranked_candidates],
            "failure_policy": base["failure_policy"],
        },
    )
    return base


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Defended discovery pre-registration",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. This is a content-sealed plan, not accepted frontier state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        f"Frontier root: `{packet['frontier_root']}`.",
        f"Candidate set: `{packet['candidate_set_id']}`.",
        f"Pre-registration id: `{packet['pre_registration_id']}`.",
        f"Content seal: `{packet['content_signature']}`.",
        "",
        "## Fixed bar",
        "",
        f"A candidate must clear every rung below and at least {packet['win_condition']['minimum_orthogonal_public_datasets']} frozen public comparator datasets.",
        "",
    ]
    for rung in packet["win_condition"]["required_rungs"]:
        lines.append(f"- `{rung['rung']}`: {rung['criterion']}")
    lines += [
        "",
        "## Ranked candidate order",
        "",
        "| rank | gene | stim max DE | Rest DE | K562 DE | RPE1 DE | score | current context |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in packet["ranked_candidates"]:
        k562 = "" if row["k562_de"] is None else row["k562_de"]
        rpe1 = "" if row["rpe1_de"] is None else row["rpe1_de"]
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['marson_stim_max_de']} | {row['rest_de']} | "
            f"{k562} | {rpe1} | {row['score']} | {row['current_context_tier']} |"
        )
    lines += [
        "",
        "## Public dataset slots",
        "",
        "| slot | role | freeze rule |",
        "|---|---|---|",
    ]
    for slot in packet["dataset_freeze"]["planned_public_dataset_slots"]:
        lines.append(
            f"| `{slot['slot']}` | {slot['minimum_role']} | content-address before scoring |"
        )
    lines += [
        "",
        "## Comparability rule",
        "",
        "Agreement or contradiction can be assigned only when the perturbed gene, cell context, readout, direction, and timepoint are comparable to the Marson stimulated activation-transcriptome claim. Non-comparable screens stay `orthogonal_phenotype`.",
        "",
        "Locked example: Schmidt 2022 cytokine-production non-hit stays `orthogonal_phenotype` for the broader Marson activation-transcriptome claim.",
        "",
        "## Kill attempts",
        "",
    ]
    for kill in packet["pre_registered_kill_attempts"]:
        lines.append(
            f"- `{kill['kill_id']}`: {kill['candidate_fails_if']}"
        )
    lines += [
        "",
        "Failure policy: a candidate is removed from the defended-discovery lane if any pre-registered kill criterion is met.",
        "",
        "Falsifiable experiment: CRISPRi knockdown in stimulated primary human CD4+ T cells with activation-marker, transcriptome, viability, and proliferation readouts.",
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect defended-discovery-preregister",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_defended_discovery_preregistration(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_defended_discovery_preregistration()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_defended_discovery_preregistration()
    print(f"wrote {OUT_JSON} ({packet['candidate_count']} candidates)")
    print(f"wrote {OUT_DOC}")
    print(f"pre_registration_id {packet['pre_registration_id']}")


if __name__ == "__main__":
    main()
