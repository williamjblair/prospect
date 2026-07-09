"""Build a scannable index over the signed Prospect findings."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FRONTIER = ROOT / "frontier"
DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "finding_index.json"
OUT_DOC = ROOT / "docs" / "FINDING_INDEX.md"

ORDER = [
    "activation_module",
    "regulator_vs_effector",
    "essentiality_artifact",
    "cross_cell_type_transfer",
    "regulon_recovery",
]

SUMMARIES = {
    "activation_module": {
        "title": "Activation module",
        "question": "Does the perturbation screen recover known T-cell signaling without priors?",
        "readout": "245 genes are quiet at Rest and become broad regulators after stimulation.",
        "takeaway": "The screen recovers the TCR activation cascade from perturbation effects alone.",
        "demo_genes": ["CD3E", "LAT", "PLCG1", "BCL10"],
        "challenge_status": "none",
    },
    "regulator_vs_effector": {
        "title": "Driver claim versus assay response",
        "question": "Do field-targeted checkpoint and cytokine genes broadly drive this assay's transcriptome?",
        "readout": "18 field-targeted genes have confirmed knockdown and near-zero stimulated DE.",
        "takeaway": "The result limits a broad driver claim for this readout; it does not imply biological irrelevance.",
        "demo_genes": ["PDCD1", "CTLA4", "HAVCR2", "IL2"],
        "challenge_status": "none",
    },
    "essentiality_artifact": {
        "title": "Rest reach is not activation specificity",
        "question": "What does high Rest reach establish about activation specificity?",
        "readout": "139 genes have high Rest reach under the frozen threshold.",
        "takeaway": "High Rest reach argues against activation specificity, but does not establish housekeeping or essentiality.",
        "demo_genes": ["TADA2B", "SGF29", "MED12", "MED19"],
        "challenge_status": "none",
    },
    "cross_cell_type_transfer": {
        "title": "Cross-cell-context comparison",
        "question": "How does the same checker behave in K562 and covered RPE1 perturbations?",
        "readout": "The high-Rest group has broader K562 effects than the activation module among covered genes.",
        "takeaway": "Cross-cell reach is orthogonal context; noncoverage is not refutation and breadth is not an essentiality label.",
        "demo_genes": ["MED19", "BCL10"],
        "challenge_status": "none",
    },
    "regulon_recovery": {
        "title": "Regulon recovery",
        "question": "Can perturbation alone recover known TF target biology?",
        "readout": "CollecTRI targets are 4.03x enriched among moved genes, with combined p near 1e-26.",
        "takeaway": "Known regulons reappear from the data, while sign disagreements remain context-sensitive review candidates.",
        "demo_genes": ["TBX21", "GATA3", "IRF1", "MYC"],
        "challenge_status": "none",
    },
}


def _load_findings() -> dict[str, dict[str, Any]]:
    path = FRONTIER / "findings.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"missing findings: {path}")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return {row["kind"]: row for row in rows}


def build_index() -> dict[str, Any]:
    findings = _load_findings()
    items = []
    for rank, kind in enumerate(ORDER, 1):
        finding = findings[kind]
        summary = SUMMARIES[kind]
        items.append({
            "rank": rank,
            "kind": kind,
            "title": summary["title"],
            "status": "computationally_reproduced",
            "challenge_status": summary["challenge_status"],
            "n_genes": len(finding.get("genes", [])),
            "cid": finding["cid"],
            "question": summary["question"],
            "readout": summary["readout"],
            "takeaway": summary["takeaway"],
            "demo_genes": summary["demo_genes"],
        })
    return {
        "title": "Scannable findings index",
        "status": "computationally_reproduced",
        "source": "frontier/findings.jsonl",
        "items": items,
    }


def _markdown(index: dict[str, Any]) -> str:
    lines = [
        "# Scannable findings index",
        "",
        "Status: `computationally_reproduced`. Source: `frontier/findings.jsonl`.",
        "",
        "| rank | finding | genes | readout |",
        "|---:|---|---:|---|",
    ]
    for item in index["items"]:
        lines.append(
            f"| {item['rank']} | `{item['kind']}` | {item['n_genes']} | {item['readout']} |"
        )
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/finding_index.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_index(out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC) -> dict[str, Any]:
    index = build_index()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(index, indent=2) + "\n")
    out_doc.write_text(_markdown(index))
    return index


def main() -> None:
    index = write_index()
    print(f"wrote {OUT_JSON} ({len(index['items'])} findings)")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
