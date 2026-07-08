"""Build the protocol-generalization replay packet across frozen substrates."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.transfer import build_transfer

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "substrate_replay_packet.json"
OUT_DOC = ROOT / "docs" / "SUBSTRATE_REPLAY_PACKET.md"
SIG = ROOT / "frontier" / "frontier.sig.json"


def _frontier_root() -> str:
    if not SIG.exists():
        return ""
    return json.loads(SIG.read_text()).get("root", "")


def _example_row(gene: str, per_gene: dict[str, dict[str, Any]], cls: str) -> dict[str, Any]:
    rec = per_gene[gene]
    return {
        "gene": gene,
        "class": cls,
        "marson_cd4_status": rec["marson"],
        "replogle_k562_status": rec["replogle"],
        "k562_de_genes": rec["k562_de"],
        "rpe1_de_genes": rec["rpe1_de"],
        "finding": rec["finding"],
    }


def build_packet() -> dict[str, Any]:
    finding = build_transfer()
    evidence = finding.evidence
    per_gene = evidence["per_gene"]
    essentiality = evidence["essentiality_replication"]
    activation = evidence["activation_specificity"]

    shared_examples = [
        _example_row("MED19", per_gene, "shared_cellular_machinery"),
        _example_row("TADA2B", per_gene, "shared_cellular_machinery"),
    ]
    immune_examples = [
        _example_row("BCL10", per_gene, "t_cell_specific_regulation"),
        _example_row("LAT", per_gene, "t_cell_specific_regulation"),
    ]

    return {
        "title": "Substrate replay packet",
        "status": "computationally_reproduced",
        "trust_boundary": "frozen_checkers_over_frozen_tables",
        "accepted_state_mutation": "none",
        "signed_frontier_root": _frontier_root(),
        "source_finding_kind": finding.kind,
        "source_finding_cid": finding.cid,
        "datasets": [
            {"id": "marson2025_cd4_perturbseq", "substrate": "primary_human_cd4_t_cells"},
            {"id": "replogle2022_k562_gwps", "substrate": "k562_non_immune_cell_line"},
            {"id": "replogle2022_rpe1", "substrate": "rpe1_non_immune_cell_line"},
        ],
        "method": {
            "claim_shape": "major_regulator",
            "checker_contract": "engine.registry.get_checker(dataset, path).check(Claim)",
            "marson_checker": "engine.checkers.marson_perturbseq",
            "replogle_checker": "engine.checkers.replogle_perturbseq",
            "model_in_trust_path": "no",
            "accepted_state_mutation": "none",
            "replay_command": "./prospect substrate-replay",
        },
        "counts": {
            "t_cell_regulators_compared": evidence["n_compared"],
            "essentiality_artifact_regulators": essentiality["n"],
            "essentiality_artifact_regulators_reproduced_in_k562": essentiality["replicated"],
            "activation_or_effector_regulators": activation["n"],
            "activation_or_effector_regulators_cell_type_specific": activation["immune_specific"],
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
        "substrate_classes": [
            {
                "class": "shared_cellular_machinery",
                "interpretation": "Broad regulators replay across primary T cells and non-immune cells.",
                "example_genes": shared_examples,
            },
            {
                "class": "t_cell_specific_regulation",
                "interpretation": "Activation regulators reproduce in primary T cells but not in K562.",
                "example_genes": immune_examples,
            },
        ],
        "replay_rows": [shared_examples[0], immune_examples[0], shared_examples[1], immune_examples[1]],
        "limitations": (
            "This packet proves replay of computation over released frozen tables. It does not prove "
            "wet-lab truth, clinical truth, or accepted biological state."
        ),
    }


def _markdown(packet: dict[str, Any]) -> str:
    counts = packet["counts"]
    rates = packet["rates"]
    lines = [
        "# Substrate replay packet",
        "",
        "Status: `computationally_reproduced`.",
        "",
        "No accepted state changes. This packet shows the checker contract replaying across primary human CD4+ T cells, K562, and RPE1 while keeping the signed frontier root unchanged.",
        "",
        f"Signed root: `{packet['signed_frontier_root']}`",
        "",
        "## Replay",
        "",
        "```bash",
        packet["method"]["replay_command"],
        "```",
        "",
        "## Frozen Substrates",
        "",
    ]
    lines += [f"- `{d['id']}`: {d['substrate'].replace('_', ' ')}" for d in packet["datasets"]]
    lines += [
        "",
        "## Results",
        "",
        f"- T-cell regulators compared: {counts['t_cell_regulators_compared']}",
        f"- Essentiality-artifact regulators reproduced in K562: {counts['essentiality_artifact_regulators_reproduced_in_k562']} of {counts['essentiality_artifact_regulators']} ({rates['essentiality_replication']['rate']})",
        f"- Activation or effector regulators cell-type-specific: {counts['activation_or_effector_regulators_cell_type_specific']} of {counts['activation_or_effector_regulators']} ({rates['activation_specificity']['rate']})",
        "",
        "## Example Rows",
        "",
        "| Gene | Class | Marson CD4 status | K562 status | K562 DE | RPE1 DE |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for row in packet["replay_rows"]:
        lines.append(
            f"| {row['gene']} | {row['class']} | {row['marson_cd4_status']} | "
            f"{row['replogle_k562_status']} | {row['k562_de_genes']} | {row['rpe1_de_genes']} |"
        )
    lines += [
        "",
        packet["limitations"],
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
    print(f"replayed {packet['counts']['t_cell_regulators_compared']} regulators across substrates")


if __name__ == "__main__":
    main()
