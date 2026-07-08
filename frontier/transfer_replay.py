"""Build a compact replay packet for the cross-cell-type transfer finding."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.transfer import build_transfer

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "transfer_replay_packet.json"
OUT_DOC = ROOT / "docs" / "TRANSFER_REPLAY_PACKET.md"
SIG = ROOT / "frontier" / "frontier.sig.json"


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def build_packet() -> dict[str, Any]:
    finding = build_transfer()
    evidence = finding.evidence
    essentiality = evidence["essentiality_replication"]
    activation = evidence["activation_specificity"]

    return {
        "title": "Transfer replay packet",
        "status": "computationally_reproduced",
        "trust_boundary": "frozen_checkers_over_frozen_tables",
        "accepted_state_mutation": "none",
        "signed_frontier_root": _frontier_root(),
        "source_finding_kind": finding.kind,
        "source_finding_cid": finding.cid,
        "datasets": [
            finding.dataset,
            evidence["second_dataset"],
            evidence["third_dataset"],
        ],
        "method": {
            "claim_shape": "major_regulator",
            "marson_checker": "engine.checkers.marson_perturbseq",
            "replogle_checker": "engine.checkers.replogle_perturbseq",
            "model_in_trust_path": "no",
            "replay_command": "./prospect transfer-replay",
        },
        "counts": {
            "t_cell_regulators_compared": evidence["n_compared"],
            "essentiality_genes": essentiality["n"],
            "essentiality_genes_reproduced_in_k562": essentiality["replicated"],
            "activation_or_effector_genes": activation["n"],
            "activation_or_effector_genes_cell_type_specific": activation["immune_specific"],
        },
        "rates": {
            "essentiality_replication": {
                "numerator": essentiality["replicated"],
                "denominator": essentiality["n"],
                "rate": essentiality["rate"],
            },
            "activation_specificity": {
                "numerator": activation["immune_specific"],
                "denominator": activation["n"],
                "rate": activation["rate"],
            },
        },
        "medians": {
            "k562_de_essentiality": evidence["median_k562_de"]["essentiality_artifact"],
            "k562_de_activation": evidence["median_k562_de"]["activation_module"],
            "rpe1_de_essentiality": evidence["median_rpe1_de_essentiality"],
        },
        "exemplars": {
            "housekeeping": evidence["housekeeping_exemplar"],
            "immune_specific": evidence["immune_exemplar"],
        },
        "interpretation": (
            "The same major-regulator claim is replayed through Marson CD4+ T cells and Replogle "
            "K562/RPE1 checkers. The packet supports checker transfer and assay triage, not a new "
            "accepted biological state."
        ),
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    rates = packet["rates"]
    lines = [
        "# Transfer replay packet",
        "",
        "Status: `computationally_reproduced`.",
        "",
        "No accepted state changes. This packet summarizes the signed cross-cell-type finding and keeps the signed frontier root unchanged.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        f"Source finding: `{packet['source_finding_kind']}` / `{packet['source_finding_cid']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["method"]["replay_command"],
        "```",
        "",
        "## Frozen Tables",
        "",
    ]
    lines += [f"- `{dataset}`" for dataset in packet["datasets"]]
    lines += [
        "",
        "## Results",
        "",
        f"- T-cell regulators compared: {counts['t_cell_regulators_compared']}",
        f"- Essentiality-artifact regulators reproduced in K562: {counts['essentiality_genes_reproduced_in_k562']} of {counts['essentiality_genes']} ({rates['essentiality_replication']['rate']})",
        f"- Activation or effector genes cell-type-specific: {counts['activation_or_effector_genes_cell_type_specific']} of {counts['activation_or_effector_genes']} ({rates['activation_specificity']['rate']})",
        f"- Housekeeping exemplars: {', '.join(packet['exemplars']['housekeeping'])}",
        f"- Immune-specific exemplars: {', '.join(packet['exemplars']['immune_specific'])}",
        "",
        "The replay strengthens the protocol claim: the same checker interface separates broad cellular machinery from T-cell-specific regulation across independent Perturb-seq releases.",
    ]
    return "\n".join(lines) + "\n"


def write_packet(out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC) -> dict[str, Any]:
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2) + "\n")
    out_doc.write_text(_markdown(packet))
    return packet


def main() -> None:
    packet = write_packet()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")
    print(f"replayed {packet['counts']['t_cell_regulators_compared']} regulators")


if __name__ == "__main__":
    main()
