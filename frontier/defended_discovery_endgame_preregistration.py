"""Build the endgame defended-discovery pre-registration packet."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
FRONTIER_SIG_JSON = ROOT / "frontier" / "frontier.sig.json"
OUT_JSON = DATA / "defended_discovery_endgame_preregistration.json"
OUT_DOC = ROOT / "docs" / "DEFENDED_DISCOVERY_ENDGAME_PREREGISTRATION.md"

HONEST_CEILING = "computation over released data, not wet-lab or clinical truth"
ROOT_HASH = "root_a8b0dcdd4024e12f"


def _load_json(path: Path) -> Any:
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


def _canonical_artifact(path: str, role: str) -> dict[str, Any]:
    full = ROOT / path
    return {
        "path": path,
        "sha256": _sha256(full),
        "role": role,
        "content_addressed": True,
    }


def _read_discovery_candidates() -> list[dict[str, Any]]:
    discovery = _load_json(DISCOVERY_JSON)
    cross = _load_json(CROSS_VALIDATION_JSON)
    cross_by_gene = {row["gene"]: row for row in cross["candidates"]}
    rows = []
    for candidate in discovery["candidates"]:
        c = cross_by_gene[candidate["gene"]]
        rows.append(
            {
                "rank": candidate["rank"],
                "gene": candidate["gene"],
                "typed_status": "evidence_attached",
                "accepted": False,
                "trust_boundary": "proposal_only",
                "marson_stim_max_de": candidate["stim_max_de"],
                "strongest_condition": candidate["strongest_condition"],
                "rest_de": candidate["rest_de"],
                "k562_de": candidate["k562_de"],
                "rpe1_de": candidate["rpe1_de"],
                "known_regulon_targets": candidate["known_regulon_targets"],
                "standard_t_cell_annotation": candidate["standard_t_cell_annotation"],
                "phase_1_score": candidate["score"],
                "current_cross_validation_tier": c["tier"],
                "current_supporting_hits": c["external_screen_summary"]["supporting_hits"],
                "current_orthogonal_phenotypes": c["external_screen_summary"]["orthogonal_phenotypes"],
                "current_comparable_contradictions": c["external_screen_summary"]["contradictions"],
            }
        )
    return rows


def _artifact_inventory() -> list[dict[str, Any]]:
    artifacts = [
        _canonical_artifact("examples/data/discovery_campaign.json", "locked ranked candidate set"),
        _canonical_artifact("examples/data/discovery_candidates.csv", "locked ranked candidate table"),
        _canonical_artifact("examples/data/cross_validation.json", "existing cross-validation packet"),
        _canonical_artifact("examples/data/cross_validation.csv", "existing cross-validation table"),
        _canonical_artifact("examples/data/cross_validation_sources.json", "existing external source bundle"),
        _canonical_artifact("examples/data/marson_de_full.csv", "Marson causal typing source"),
        _canonical_artifact("examples/data/atlas_backbone.json", "frontier backbone source"),
        _canonical_artifact("examples/data/replogle_k562_de.csv", "K562 specificity comparator"),
        _canonical_artifact("examples/data/replogle_rpe1_de.csv", "RPE1 specificity comparator"),
        _canonical_artifact("examples/data/collectri_human.csv", "novelty exclusion source"),
        _canonical_artifact("frontier/frontier.sig.json", "signed frontier root reference"),
    ]
    for optional in [
        "examples/data/pggt1b_defended_evidence.json",
        "examples/data/rcc1l_defended_evidence.json",
        "examples/data/mcat_defended_evidence.json",
        "examples/data/rwdd2b_defended_evidence.json",
        "examples/data/ccdc22_defended_evidence.json",
    ]:
        path = ROOT / optional
        if path.exists():
            artifacts.append(_canonical_artifact(optional, "prior packet, must be re-scored under this endgame pre-registration"))
    return artifacts


def _dataset_slots() -> list[dict[str, Any]]:
    return [
        {
            "slot": "primary_t_cell_crispr_or_perturbseq",
            "minimum_role": "comparable perturbation support or an explicitly typed orthogonal phenotype",
            "candidate_sources": ["Shifrut 2018", "Schmidt 2022"],
            "freeze_before_scoring": True,
        },
        {
            "slot": "gwas_catalog_immune_traits",
            "minimum_role": "disease-genetics hook or absence of hook",
            "candidate_sources": ["NHGRI-EBI GWAS Catalog"],
            "freeze_before_scoring": True,
        },
        {
            "slot": "depmap_dependency",
            "minimum_role": "broad dependency and proliferation-artifact kill",
            "candidate_sources": ["Broad DepMap", "Sanger DepMap"],
            "freeze_before_scoring": True,
        },
        {
            "slot": "protein_interaction_network",
            "minimum_role": "mechanistic coherence and alternative-mechanism kill",
            "candidate_sources": ["STRING", "BioGRID"],
            "freeze_before_scoring": True,
        },
        {
            "slot": "immune_subset_expression_atlas",
            "minimum_role": "immune-cell expression context and cell-context kill",
            "candidate_sources": ["DICE"],
            "freeze_before_scoring": True,
        },
        {
            "slot": "drugbank_or_chembl_target_hook",
            "minimum_role": "druggability hook or evidence that no such hook is present",
            "candidate_sources": ["DrugBank", "ChEMBL"],
            "freeze_before_scoring": True,
        },
    ]


def _discovery_bar() -> dict[str, Any]:
    return {
        "minimum_orthogonal_public_datasets": 5,
        "required_rungs": [
            {
                "rung": "novel_driver",
                "criterion": "strong causal Marson CD4+ activation driver, absent from CollecTRI and standard T-cell regulator annotations",
            },
            {
                "rung": "zero_drift_reproducibility",
                "criterion": "re-derives from frozen data with frontier drift equal to zero",
            },
            {
                "rung": "cell_type_specificity",
                "criterion": "inert or housekeeping in Replogle K562 and RPE1, not a broad essentiality artifact",
            },
            {
                "rung": "five_frozen_orthogonal_public_datasets",
                "criterion": "at least five public comparator datasets are frozen, content-addressed, and scored",
            },
            {
                "rung": "readout_comparability",
                "criterion": "agreement or contradiction is assigned only when the comparator tests a comparable phenotype",
            },
            {
                "rung": "mechanistic_coherence",
                "criterion": "specific pathway, molecular role, and expected activation readout are stated",
            },
            {
                "rung": "real_world_hook",
                "criterion": "druggable target, disease-genetics link, or decisive correction of a named consensus claim",
            },
            {
                "rung": "falsifiable_experiment",
                "criterion": "one stimulated primary human CD4+ CRISPRi experiment would refute the hypothesis",
            },
        ],
    }


def _comparability_rules() -> dict[str, Any]:
    return {
        "default_for_nonmatching_readout": "orthogonal_phenotype",
        "agreement_requires": [
            "same perturbed gene or justified target mapping",
            "immune-cell or primary T-cell context, or a stated bridge to CD4+ activation",
            "activation regulation, activation transcriptome breadth, immune function, or a documented comparable readout",
            "direction and timepoint interpretable against the Marson Rest, Stim8hr, or Stim48hr condition",
        ],
        "contradiction_requires": [
            "an explicit driver claim under test",
            "same perturbed gene or justified target mapping",
            "comparable phenotype and assay direction",
            "adequate perturbation or target engagement evidence in the comparator",
            "the comparator null or opposite effect directly tests the claim",
        ],
        "locked_readout_mismatch": {
            "source": "Schmidt 2022 cytokine-production regulator calls",
            "typed_status": "orthogonal_phenotype",
            "reason": "a cytokine-production non-hit does not contradict broad activation-transcriptome regulation unless the claim is narrowed to cytokine output",
        },
    }


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "independent_axis": "perturbation quality",
            "candidate_fails_if": "the apparent Marson effect is explained by failed knockdown, off-target labeling, missing on-target stimulated perturbation, or one unstable guide",
            "dataset_or_evidence_needed": "Marson perturbation-quality fields and any released guide-level evidence available for the candidate",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "independent_axis": "broad dependency outside stimulated CD4+ cells",
            "candidate_fails_if": "Replogle, DepMap, or another dependency source explains the signal as general growth, viability, or housekeeping biology",
            "dataset_or_evidence_needed": "Replogle K562, Replogle RPE1, and frozen DepMap dependency evidence",
        },
        {
            "kill_id": "batch_or_donor_effect",
            "independent_axis": "dataset and donor robustness",
            "candidate_fails_if": "a comparable public primary T-cell perturbation dataset directly tests the activation-driver claim and shows no compatible effect",
            "dataset_or_evidence_needed": "Shifrut, Schmidt if comparable, or another frozen primary T-cell perturbation screen",
        },
        {
            "kill_id": "reverse_causality_or_passenger_marker",
            "independent_axis": "association versus causation",
            "candidate_fails_if": "expression, disease, or perturbation evidence supports the gene as a downstream activation marker or passenger rather than a driver",
            "dataset_or_evidence_needed": "DICE or equivalent expression, GWAS Catalog, and primary perturbation evidence",
        },
        {
            "kill_id": "better_alternative_mechanism",
            "independent_axis": "simpler mechanistic explanation",
            "candidate_fails_if": "protein network, pathway, disease, or chemistry evidence points to a different gene or pathway node as the better causal explanation",
            "dataset_or_evidence_needed": "STRING or BioGRID, ChEMBL or DrugBank, GWAS Catalog, and pathway context",
        },
    ]


def _falsifiable_experiment() -> dict[str, Any]:
    return {
        "system": "stimulated primary human CD4+ T cells",
        "intervention": "CRISPRi knockdown of the candidate with at least two independent guides",
        "controls": [
            "non-targeting guide",
            "safe-harbor guide",
            "positive activation-pathway control",
            "unstimulated matched culture",
        ],
        "readout": "activation-marker flow cytometry plus targeted RNA-seq or Perturb-seq at the registered strongest timepoint",
        "candidate_refutes_if": "on-target knockdown does not shift the activation program relative to controls, or shifts only a broad viability or housekeeping signature",
    }


def build_defended_discovery_endgame_preregistration() -> dict[str, Any]:
    candidates = _read_discovery_candidates()
    discovery = _load_json(DISCOVERY_JSON)
    frontier_sig = _load_json(FRONTIER_SIG_JSON)
    packet: dict[str, Any] = {
        "phase": "defended_discovery_endgame_preregistration",
        "pre_registered_on": "2026-07-08",
        "status": "evidence_attached",
        "accepted": False,
        "trust_boundary": "proposal_only",
        "frontier_root": frontier_sig.get("root", ROOT_HASH),
        "candidate_set_id": discovery["candidate_set_id"],
        "candidate_count": len(candidates),
        "ranked_candidates": candidates,
        "candidate_order_policy": {
            "skip_allowed": False,
            "rule": "evaluate candidates in locked rank order until one clears the full bar or every candidate has a recorded non-clearance",
            "prior_result_policy": "prior rank 5 CCDC22 and rank 1 PGGT1B packets are evidence only; neither can be treated as the endgame outcome without re-scoring under this packet",
        },
        "discovery_bar": _discovery_bar(),
        "dataset_freeze": {
            "attached_frozen_artifacts": _artifact_inventory(),
            "required_public_dataset_slots": _dataset_slots(),
            "new_dataset_rule": "any new public source must be stored or snapshotted under examples/data with sha256 before scoring",
        },
        "comparability_rules": _comparability_rules(),
        "pre_registered_kill_attempts": _kill_attempts(),
        "failure_policy": "Any landed pre-registered kill removes the candidate from the defended-discovery lane. The kill cannot be redefined to save the candidate.",
        "honest_fallback": {
            "also_counts_as_outcome": True,
            "condition": "if no candidate clears the full bar, publish the exhaustion ledger with the exact kill or missing rung for every candidate",
        },
        "positive_or_corrective": {
            "positive": "novel druggable activation driver clears the full bar",
            "corrective": "named consensus driver claim is typed as passenger or artifact with five-dataset corroboration",
        },
        "falsifiable_experiment": _falsifiable_experiment(),
        "honest_ceiling": HONEST_CEILING,
        "reproduce_command": "./prospect defended-discovery-endgame-preregister",
        "next_step": "commit this pre-registration before candidate-specific endgame scoring",
    }
    packet["pre_registration_id"] = _hash_obj("endgame_prereg", {
        "candidate_set_id": packet["candidate_set_id"],
        "ranked_candidates": [(row["rank"], row["gene"]) for row in candidates],
        "bar": packet["discovery_bar"],
        "kills": packet["pre_registered_kill_attempts"],
    })
    packet["content_signature"] = _hash_obj("endgame_prereg_sig", packet)
    packet["signature_scope"] = "content seal only, not accepted frontier state"
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Defended discovery endgame pre-registration",
        "",
        f"Pre-registration id: `{packet['pre_registration_id']}`",
        "",
        f"Frontier root: `{packet['frontier_root']}`",
        "",
        f"Status: `{packet['status']}`. accepted=false. Trust boundary: `{packet['trust_boundary']}`.",
        "",
        f"Ceiling: {packet['honest_ceiling']}.",
        "",
        "## Locked candidate order",
        "",
        "Candidates must be evaluated in this order. A prior packet is evidence only under this new bar.",
        "",
        "| rank | gene | Marson stimulated DE | strongest condition | K562 DE | current tier |",
        "|---:|---|---:|---|---:|---|",
    ]
    for row in packet["ranked_candidates"]:
        k562 = "" if row["k562_de"] is None else row["k562_de"]
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['marson_stim_max_de']} | "
            f"{row['strongest_condition']} | {k562} | {row['current_cross_validation_tier']} |"
        )
    lines += [
        "",
        "## Bar",
        "",
    ]
    for rung in packet["discovery_bar"]["required_rungs"]:
        lines.append(f"- `{rung['rung']}`: {rung['criterion']}")
    lines += [
        "",
        "## Required frozen public dataset slots",
        "",
    ]
    for slot in packet["dataset_freeze"]["required_public_dataset_slots"]:
        lines.append(f"- `{slot['slot']}`: {slot['minimum_role']}")
    lines += [
        "",
        "## Pre-registered kills",
        "",
    ]
    for kill in packet["pre_registered_kill_attempts"]:
        lines.append(
            f"- `{kill['kill_id']}`: fails if {kill['candidate_fails_if']}. "
            f"Evidence: {kill['dataset_or_evidence_needed']}."
        )
    lines += [
        "",
        "## Comparability rule",
        "",
        "Nonmatching readouts default to `orthogonal_phenotype`, not contradiction.",
        "",
        "## Falsifiable experiment",
        "",
        f"System: {packet['falsifiable_experiment']['system']}.",
        "",
        f"Refutes if: {packet['falsifiable_experiment']['candidate_refutes_if']}.",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_defended_discovery_endgame_preregistration(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_defended_discovery_endgame_preregistration()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_defended_discovery_endgame_preregistration()
    print(f"wrote {OUT_JSON} ({packet['pre_registration_id']})")


if __name__ == "__main__":
    main()
