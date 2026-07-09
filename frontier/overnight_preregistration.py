"""Build the overnight compute pre-registration packet without scoring."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "overnight_preregistration.json"
OUT_DOC = ROOT / "docs" / "OVERNIGHT_PREREGISTRATION.md"

HONEST_CEILING = "Computation over released data, not wet-lab or clinical truth."
ROOT_HASH = "root_a8b0dcdd4024e12f"

SOURCE_PATHS = [
    ("marson_cd4_activation", "examples/data/marson_de_full.csv", "primary causal substrate"),
    ("frontier_backbone", "examples/data/atlas_backbone.json", "frontier gene universe and classes"),
    ("replogle_k562", "examples/data/replogle_k562_de.csv", "genome-wide non-immune specificity comparator"),
    ("replogle_rpe1", "examples/data/replogle_rpe1_de.csv", "sparse non-immune specificity context"),
    ("collectri", "examples/data/collectri_human.csv", "known TF-target novelty exclusion"),
    ("cross_validation_sources", "examples/data/cross_validation_sources.json", "frozen Shifrut, Schmidt, DICE, STRING source bundle"),
    ("cross_validation", "examples/data/cross_validation.json", "prior candidate-level cross-validation packet"),
    ("disease_overlay", "examples/data/disease_genetics_overlay.json", "Open Targets disease context packet"),
    ("frontier_signature", "frontier/frontier.sig.json", "signed frontier root reference"),
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _source_inventory() -> list[dict[str, Any]]:
    rows = []
    for name, rel, role in SOURCE_PATHS:
        path = ROOT / rel
        rows.append(
            {
                "name": name,
                "path": rel,
                "role": role,
                "exists": path.exists(),
                "sha256": _sha256(path) if path.exists() else "",
            }
        )
    return rows


def build_preregistration() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "phase": "overnight_compute_preregistration",
        "pre_registered_on": "2026-07-09",
        "frontier_root": ROOT_HASH,
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "no_model_in_trust_path": True,
        "anthropic_budget_usd": 0,
        "source_inventory": _source_inventory(),
        "checkpoint_policy": {
            "log_path": "output/overnight_compute.log",
            "crash_loss_bound": "at most the current gene or current literature page",
            "gate_commands": [
                "./prospect verify",
                "python benchmark/mutation_pack.py",
                "python tests/test_skill_parity.py",
                "python tests/test_marson.py",
                "python -m pytest tests/ -q",
                "cd web && npm run build",
            ],
        },
        "typed_status_ladder": {
            "evidence_attached": "on-target perturbation has a causal activation-program effect in the comparable substrate, but remains proposal-only",
            "associative_only": "gene is present in an external signature or literature context, but perturbation does not support a causal driver role and no comparable driver claim is refuted",
            "contradicted": "an explicit causal or driver claim with a comparable readout is refuted by on-target perturbation evidence",
            "orthogonal_phenotype": "the comparator tests a different phenotype or readout, so it cannot support or contradict the activation-transcriptome claim",
            "not_assayed": "gene is absent, lacks on-target perturbation, or the comparator does not cover it",
            "refuted": "reserved for a stronger future packet where multiple comparable frozen sources overturn the same explicit claim",
        },
        "phase_1_genome_wide_atlas_rules": {
            "gene_universe": "all genes in examples/data/marson_de_full.csv grouped by target_contrast_gene_name",
            "conditions": ["Rest", "Stim8hr", "Stim48hr"],
            "strongest_effect": "maximum n_total_de_genes among on-target KD rows across Rest, Stim8hr, and Stim48hr",
            "driver_threshold": "strongest on-target n_total_de_genes greater than 10",
            "associative_only_threshold": "strongest on-target n_total_de_genes between 0 and 10 inclusive when no comparable explicit driver claim is under test",
            "not_assayed_rule": "no on-target KD row across all Marson conditions, or gene absent from a comparator",
            "direction_fields": ["n_up_genes", "n_down_genes", "ontarget_effect_size", "strongest_condition"],
            "specificity_rules": {
                "k562": "K562 coverage is genome-wide enough to score broad non-immune transfer; k562_de above 25 is a specificity warning",
                "rpe1": "RPE1 sparse coverage is context only; missing RPE1 is not_assayed and never a blocking failure",
                "shifrut": "primary T-cell support where the frozen ORCS bundle covers the gene",
                "schmidt": "cytokine-production non-hits are orthogonal_phenotype unless the claim is specifically cytokine output",
            },
            "atlas_status": "evidence_attached packet, accepted=false",
        },
        "phase_2_literature_audit_rules": {
            "corpus_source": "Europe PMC open API with PubMed IDs retained where available",
            "query_plan": [
                "human CD4 T cell activation regulator",
                "CD4 T cell transcriptional regulator activation",
                "T cell activation checkpoint regulator CD4",
                "CRISPR CD4 T cell regulator activation",
                "Perturb-seq T cell activation regulator",
            ],
            "page_limit_per_query": 100,
            "rate_limit_seconds": 0.35,
            "claim_extraction": {
                "gene_mapping": "uppercase approved symbols and aliases from frozen Marson symbols plus common checkpoint aliases",
                "claim_sentence": "title or abstract sentence containing a gene and a driver word",
                "driver_words": ["regulates", "regulator", "drives", "controls", "required", "essential", "mediates", "promotes", "inhibits"],
                "cd4_context_required": "CD4, T cell, T-cell, T lymphocyte, helper T, or TCR in title or abstract",
            },
            "comparability_rules": {
                "comparable": "activation, TCR stimulation, CD4 T-cell state, transcriptional program, proliferation only when the claim is proliferation-specific",
                "orthogonal": "cytokine secretion, exhaustion marker expression, disease association, immunotherapy response, or generic importance without an activation-driver readout",
                "contradiction_requires": "explicit driver claim plus comparable readout plus Marson on-target strongest effect at or below 10 DE genes",
                "support_requires": "explicit driver claim plus comparable readout plus Marson on-target strongest effect above 10 DE genes",
            },
            "dedupe_key": "pmid plus gene plus normalized claim sentence",
            "audit_status": "evidence_attached packet, accepted=false",
        },
        "phase_3_defended_leaderboard_rules": {
            "candidate_source": "phase 1 genome-wide drivers absent from CollecTRI and standard T-cell regulator annotations",
            "minimum_orthogonal_public_datasets": 5,
            "noncoverage_policy": "not_assayed is reported and never counted as a contradiction",
            "required_hook": "disease-genetics link, druggable target or compound evidence, or a decisive correction of a named consensus claim",
            "ranking": [
                "Marson strongest activation effect descending",
                "K562 specificity warning absent",
                "primary T-cell support present",
                "orthogonal dataset count descending",
                "kill attempts survived descending",
                "gene symbol ascending",
            ],
            "kill_attempts": [
                {
                    "kill_id": "technical_confound",
                    "fails_if": "no on-target stimulated perturbation, failed knockdown, or off-target warning explains the effect",
                },
                {
                    "kill_id": "essentiality_or_proliferation_artifact",
                    "fails_if": "Rest reach, K562 transfer, RPE1 covered transfer, or DepMap dependency better explains the signal as general machinery",
                },
                {
                    "kill_id": "batch_or_donor_effect",
                    "fails_if": "a comparable frozen primary T-cell perturbation screen directly tests and does not support the driver claim",
                },
                {
                    "kill_id": "reverse_causality_or_passenger_marker",
                    "fails_if": "the frozen evidence supports downstream expression or association rather than causal perturbation",
                },
                {
                    "kill_id": "better_alternative_mechanism",
                    "fails_if": "STRING, pathway, disease, or chemistry evidence points to another node as the better causal explanation",
                },
            ],
            "falsifiable_experiment_template": "CRISPRi knockdown in stimulated primary human CD4+ T cells with at least two guides, non-targeting and activation-pathway controls, activation-marker flow and RNA readout; refuted if on-target knockdown does not shift the registered activation program or only shifts a broad viability signature",
            "leaderboard_status": "evidence_attached packet, accepted=false",
        },
        "outputs": {
            "phase_1": ["examples/data/overnight_genome_wide_atlas.json", "examples/data/overnight_genome_wide_atlas.csv"],
            "phase_2": ["examples/data/overnight_literature_claims.json", "examples/data/overnight_literature_audit.json", "examples/data/overnight_literature_audit.csv"],
            "phase_3": ["examples/data/overnight_defended_leaderboard.json", "examples/data/overnight_defended_leaderboard.csv"],
            "doc": "docs/OVERNIGHT_COMPUTE_REPORT.md",
        },
    }
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    packet["pre_registration_id"] = f"overnight_prereg_{digest}"
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    sources = "\n".join(
        f"- `{row['name']}`: `{row['path']}` sha256 `{row['sha256']}`"
        for row in packet["source_inventory"]
    )
    kills = "\n".join(
        f"- `{row['kill_id']}`: fails if {row['fails_if']}"
        for row in packet["phase_3_defended_leaderboard_rules"]["kill_attempts"]
    )
    statuses = "\n".join(
        f"- `{key}`: {value}"
        for key, value in packet["typed_status_ladder"].items()
    )
    queries = "\n".join(f"- `{query}`" for query in packet["phase_2_literature_audit_rules"]["query_plan"])
    return (
        "# Overnight compute pre-registration\n\n"
        f"ID: `{packet['pre_registration_id']}`\n\n"
        f"Frontier root: `{packet['frontier_root']}`. accepted=false. next=human_signature_required.\n\n"
        f"Ceiling: {packet['honest_ceiling']}\n\n"
        "No model is in the trust path. Anthropic budget: $0. The run is compute-only over frozen or newly frozen released data.\n\n"
        "## Typed Status Ladder\n\n"
        f"{statuses}\n\n"
        "## Source Inventory\n\n"
        f"{sources}\n\n"
        "## Phase 1 Rules\n\n"
        "- Universe: all Marson genes grouped by `target_contrast_gene_name`.\n"
        "- Strongest effect: maximum `n_total_de_genes` among on-target KD rows across Rest, Stim8hr, and Stim48hr.\n"
        "- Driver threshold: strongest on-target effect greater than 10 DE genes.\n"
        "- `associative_only`: strongest on-target effect from 0 to 10 DE genes when no comparable explicit driver claim is under test.\n"
        "- `not_assayed`: no on-target KD row or missing comparator coverage.\n"
        "- K562 is the genome-wide specificity comparator. RPE1 non-coverage is context only.\n\n"
        "## Phase 2 Literature Rules\n\n"
        "Europe PMC query plan:\n\n"
        f"{queries}\n\n"
        "Contradiction requires an explicit causal or driver claim, a comparable activation readout, and Marson on-target strongest effect at or below 10 DE genes. Non-comparable cytokine, disease, exhaustion, or immunotherapy-response claims are `orthogonal_phenotype`.\n\n"
        "## Phase 3 Kill Rules\n\n"
        f"{kills}\n\n"
        "A leaderboard entry remains proposal-only and accepted=false. A human key accepts no state overnight.\n"
    )


def write_preregistration() -> dict[str, Any]:
    packet = build_preregistration()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    OUT_DOC.write_text(_markdown(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect overnight-preregister")
    parser.add_argument("--json", action="store_true", help="print packet JSON")
    args = parser.parse_args(argv)
    packet = write_preregistration()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {OUT_JSON}")
        print(f"wrote {OUT_DOC}")
        print(f"pre_registration_id={packet['pre_registration_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
