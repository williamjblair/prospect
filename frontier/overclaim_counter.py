"""Build the Phase 4 overclaim counter packet."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "examples" / "data"
PHANTOM_JSON = DATA / "phantom_summary.json"
MODELS_JSON = DATA / "model_comparison.json"
DISCOVERY_JSON = DATA / "discovery_campaign.json"
CROSS_VALIDATION_JSON = DATA / "cross_validation.json"
FLAGSHIP_JSON = DATA / "flagship_module.json"
OUT_JSON = DATA / "overclaim_counter.json"
OUT_DOC = ROOT / "docs" / "OVERCLAIM_COUNTER.md"


def _load(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required packet: {path}")
    return json.loads(path.read_text())


def _packet_id(packet: dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"overclaim_counter_{digest[:16]}"


def build_overclaim_counter() -> dict[str, Any]:
    phantom = _load(PHANTOM_JSON)
    models = _load(MODELS_JSON)
    discovery = _load(DISCOVERY_JSON)
    cross_validation = _load(CROSS_VALIDATION_JSON)
    flagship = _load(FLAGSHIP_JSON)
    phase1_survivors = discovery["filter_counts"]["cell_type_specific_replogle"]
    phase1_refused_total = discovery["filter_counts"]["frontier_genes"] - phase1_survivors
    phase2_with_hit = cross_validation["counts"]["candidates_with_external_screen_hit"]
    phase2_without_hit = cross_validation["candidate_count"] - phase2_with_hit
    counts = {
        "model_major_claims": phantom["ai_major_claims"],
        "model_checkable_claims": phantom["checkable"],
        "model_contradicted_claims": phantom["refuted"],
        "model_contradicted_rate": phantom["refuted_rate"],
        "effector_overclaimed": phantom["effector_overclaimed"],
        "effector_total": phantom["effector_total"],
        "effector_overclaim_rate": phantom["effector_overclaim_rate"],
        "phase1_frontier_genes": discovery["filter_counts"]["frontier_genes"],
        "phase1_survivors": phase1_survivors,
        "phase1_refused_total": phase1_refused_total,
        "phase2_without_external_screen_hit": phase2_without_hit,
        "phase2_schmidt_non_hits": cross_validation["counts"]["candidates_with_schmidt_non_hit"],
        "flagship_members": len(flagship["flagship_module"]["members"]),
    }
    rungs = [
        {
            "rung": "frozen_marson_checker",
            "status": "contradicted",
            "checked": phantom["checkable"],
            "contradicted": phantom["refuted"],
            "rate": phantom["refuted_rate"],
            "source": "examples/data/phantom_summary.json",
        },
        {
            "rung": "mutation_floor",
            "status": "refuted",
            "tampered_claims": 20,
            "false_admissions": 0,
            "source": "python benchmark/mutation_pack.py",
        },
        {
            "rung": "novelty_filter",
            "status": "evidence_attached",
            "scanned": discovery["filter_counts"]["frontier_genes"],
            "survivors": phase1_survivors,
            "refused": phase1_refused_total,
            "standard_annotation_refusals": discovery["refusal_counts"]["standard_t_cell_annotation"],
            "collectri_refusals": discovery["refusal_counts"]["collectri_present"],
            "source": "examples/data/discovery_campaign.json",
        },
        {
            "rung": "external_screen_ladder",
            "status": "contradicted",
            "candidates": cross_validation["candidate_count"],
            "supporting_screen_hit": phase2_with_hit,
            "no_supporting_screen_hit": phase2_without_hit,
            "schmidt_non_hits": cross_validation["counts"]["candidates_with_schmidt_non_hit"],
            "source": "examples/data/cross_validation.json",
        },
        {
            "rung": "module_selection",
            "status": "evidence_attached",
            "modules_ranked": len(flagship["modules"]),
            "non_flagship_modules": len(flagship["modules"]) - 1,
            "flagship_module": flagship["flagship_module"]["module_id"],
            "source": "examples/data/flagship_module.json",
        },
    ]
    packet = {
        "phase": "phase_4_overclaim_counter",
        "title": "Overclaim counter",
        "status": "evidence_attached",
        "replayability": "attested",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "accepted": False,
        "honest_ceiling": "computation over released data, not wet-lab or clinical truth",
        "counts": counts,
        "rungs": rungs,
        "model_breakdown": models,
        "flagship_boundary": {
            "module_id": flagship["flagship_module"]["module_id"],
            "anchor_gene": flagship["flagship_module"]["anchor_gene"],
            "accepted_state": "none",
            "next_acceptance_step": "human key signs only after a frozen re-derivation and review justify a state transition",
        },
        "reproduce_command": "./prospect overclaim-counter",
        "next_phase": "surface the flagship and refusal ladder in the app",
    }
    packet["packet_id"] = _packet_id(packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    lines = [
        "# Overclaim counter",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. The counter measures refusals, not accepted state.",
        "",
        f"Honest ceiling: {packet['honest_ceiling']}.",
        "",
        f"The benchmark caught {counts['model_contradicted_claims']} of {counts['model_checkable_claims']} checkable model major-regulator claims as `contradicted`.",
        "",
        f"The discovery ladder kept {counts['phase1_survivors']} of {counts['phase1_frontier_genes']:,} Phase 1 genes; {counts['phase2_without_external_screen_hit']} of {counts['phase1_survivors']} then lacked an independent screen-hit rung.",
        "",
        "PGGT1B advanced because it survived the novelty filter, gained Shifrut 2018 support, retained the Schmidt 2022 contradiction honestly, and anchored the highest-scoring module.",
        "",
        "## Rungs",
        "",
        "| rung | status | count | source |",
        "|---|---|---:|---|",
    ]
    for rung in packet["rungs"]:
        count = rung.get("contradicted", rung.get("refused", rung.get("no_supporting_screen_hit", rung.get("non_flagship_modules", 0))))
        lines.append(f"| {rung['rung']} | {rung['status']} | {count} | {rung['source']} |")
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "./prospect overclaim-counter",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_overclaim_counter(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_overclaim_counter()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_overclaim_counter()
    print(f"wrote {OUT_JSON} ({packet['counts']['model_contradicted_claims']} contradicted model claims)")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
