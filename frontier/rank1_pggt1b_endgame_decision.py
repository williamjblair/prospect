"""Decide rank-1 PGGT1B under the endgame pre-registration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
PREREG_JSON = DATA / "defended_discovery_endgame_preregistration.json"
PGGT1B_JSON = DATA / "pggt1b_defended_evidence.json"
OUT_JSON = DATA / "pggt1b_endgame_decision.json"
OUT_DOC = ROOT / "docs" / "PGGT1B_ENDGAME_DECISION.md"


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


def _source(path: str, role: str) -> dict[str, str]:
    full = ROOT / path
    return {"path": path, "role": role, "sha256": _sha256(full)}


def _rank1(prereg: dict[str, Any]) -> dict[str, Any]:
    row = prereg["ranked_candidates"][0]
    if row["gene"] != "PGGT1B" or row["rank"] != 1:
        raise RuntimeError("endgame pre-registration rank 1 is not PGGT1B")
    return row


def _bar_rungs(rank1: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "rung": "novel_driver",
            "status": "evidence_attached",
            "basis": "rank-1 novelty survivor, 3014 stimulated DE genes, zero CollecTRI targets, absent from the standard T-cell annotation set",
        },
        {
            "rung": "zero_drift_reproducibility",
            "status": "computationally_reproduced",
            "basis": "frontier replays at 0 drift against root_a8b0dcdd4024e12f",
        },
        {
            "rung": "cell_type_specificity",
            "status": "not_cleared",
            "typed_detail": "rpe1_not_assayed",
            "basis": f"K562 DE is {rank1['k562_de']}, but RPE1 is not_assayed in the locked candidate row.",
        },
        {
            "rung": "five_frozen_orthogonal_public_datasets",
            "status": "evidence_attached",
            "count": prior["orthogonal_public_dataset_count"],
            "basis": "frozen PGGT1B snapshots include Shifrut, Schmidt, ORCS T-cell rows, STRING, DICE, GWAS Catalog, ChEMBL, Ensembl homology, and DepMap 19Q2",
        },
        {
            "rung": "readout_comparability",
            "status": "not_cleared",
            "basis": "Shifrut supports primary T-cell proliferation or stimulation-response behavior, but no frozen comparator replays the Marson activation-transcriptome breadth for PGGT1B. Schmidt cytokine output remains orthogonal_phenotype.",
        },
        {
            "rung": "mechanistic_coherence",
            "status": "evidence_attached",
            "basis": prior["mechanism"],
        },
        {
            "rung": "real_world_hook",
            "status": "evidence_attached",
            "basis": prior["real_world_hook"],
        },
        {
            "rung": "falsifiable_experiment",
            "status": "evidence_attached",
            "basis": prior["falsifiable_experiment"]["refutes_if"],
        },
    ]


def _kill_attempts() -> list[dict[str, str]]:
    return [
        {
            "kill_id": "technical_confound",
            "result": "survives_current_frozen_evidence",
            "basis": "Marson records on-target stimulated knockdown and a large stimulated effect, but guide-level audit remains a strengthening item.",
        },
        {
            "kill_id": "essentiality_or_proliferation_artifact",
            "result": "survives_current_frozen_evidence",
            "basis": "K562 DE is 1 and DepMap Achilles 19Q2 has median gene effect -0.1009 with 0 of 563 lines below -1.",
        },
        {
            "kill_id": "batch_or_donor_effect",
            "result": "not_cleared",
            "basis": "Shifrut is supportive but not an activation-transcriptome replay; Schmidt cytokine-output non-hit is an orthogonal phenotype, not a contradiction.",
        },
        {
            "kill_id": "reverse_causality_or_passenger_marker",
            "result": "survives_current_frozen_evidence",
            "basis": "The Marson perturbation effect is causal in this assay, and DICE expression does not by itself explain the signal as only a marker.",
        },
        {
            "kill_id": "better_alternative_mechanism",
            "result": "survives_current_frozen_evidence",
            "basis": "STRING and ChEMBL support the geranylgeranylation mechanism rather than an unrelated pathway node, while direct substrate-level biology remains wet-lab work.",
        },
    ]


def build_rank1_pggt1b_endgame_decision() -> dict[str, Any]:
    prereg = _load(PREREG_JSON)
    prior = _load(PGGT1B_JSON)
    rank1 = _rank1(prereg)
    packet: dict[str, Any] = {
        "phase": "rank_1_pggt1b_endgame_decision",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "gene": "PGGT1B",
        "rank": 1,
        "status": "evidence_attached",
        "accepted": False,
        "trust_boundary": "proposal_only",
        "decision": "not_cleared_full_bar",
        "why_not_discovery": [
            "RPE1 specificity is not_assayed in the frozen Replogle comparator.",
            "The strongest independent primary T-cell hit is Shifrut proliferation or stimulation-response support, not an activation-transcriptome replay.",
        ],
        "bar_rungs": _bar_rungs(rank1, prior),
        "kill_attempts": _kill_attempts(),
        "frozen_sources": [
            _source("examples/data/defended_discovery_endgame_preregistration.json", "endgame pre-registration"),
            _source("examples/data/pggt1b_defended_evidence.json", "prior PGGT1B defended evidence packet"),
            _source("examples/data/pggt1b_defended_sources/orcs_screen_rows.json", "primary T-cell ORCS support and orthogonal screens"),
            _source("examples/data/pggt1b_defended_sources/orcs_gene_tcell_rows.json", "ORCS T-cell row audit"),
            _source("examples/data/pggt1b_defended_sources/depmap_achilles_19q2.json", "dependency artifact kill"),
            _source("examples/data/pggt1b_defended_sources/string_interactions.json", "protein network mechanism"),
            _source("examples/data/pggt1b_defended_sources/dice_expression.json", "immune expression context"),
            _source("examples/data/pggt1b_defended_sources/chembl_target.json", "drug target hook"),
            _source("examples/data/pggt1b_defended_sources/chembl_activity.json", "compound activity hook"),
            _source("examples/data/pggt1b_defended_sources/gwas_gene.json", "GWAS gene context"),
        ],
        "honest_ceiling": prereg["honest_ceiling"],
        "next_candidate": "RCC1L",
        "reproduce_command": "./prospect pggt1b-endgame-decision",
    }
    packet["decision_id"] = _hash_obj("pggt1b_endgame", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# PGGT1B endgame decision",
        "",
        f"Decision id: `{packet['decision_id']}`",
        "",
        f"Pre-registration: `{packet['pre_registration_id']}`",
        "",
        "PGGT1B is not cleared full bar under the endgame pre-registration.",
        "",
        "It remains an `evidence_attached` hypothesis. accepted=false. The ceiling is "
        f"{packet['honest_ceiling']}.",
        "",
        "## Why it does not clear",
        "",
    ]
    for reason in packet["why_not_discovery"]:
        lines.append(f"- {reason}")
    lines += [
        "",
        "## Bar rungs",
        "",
        "| rung | status | basis |",
        "|---|---|---|",
    ]
    for rung in packet["bar_rungs"]:
        lines.append(f"| `{rung['rung']}` | `{rung['status']}` | {rung['basis']} |")
    lines += [
        "",
        "## Kills",
        "",
    ]
    for kill in packet["kill_attempts"]:
        lines.append(f"- `{kill['kill_id']}`: `{kill['result']}`. {kill['basis']}")
    lines += [
        "",
        f"Next candidate: `{packet['next_candidate']}`.",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_rank1_pggt1b_endgame_decision(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    packet = build_rank1_pggt1b_endgame_decision()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_rank1_pggt1b_endgame_decision()
    print(f"wrote {OUT_JSON} ({packet['decision']})")


if __name__ == "__main__":
    main()
