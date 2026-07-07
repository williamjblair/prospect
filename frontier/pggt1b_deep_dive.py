"""Build a PGGT1B lab-facing evidence packet from frozen Prospect data."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier import predicates as P

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "pggt1b_deep_dive.json"
OUT_DOC = ROOT / "docs" / "PGGT1B_DEEP_DIVE.md"


def _load_backbone() -> dict[str, dict[str, Any]]:
    path = DATA / "atlas_backbone.json"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen backbone: {path}")
    return {n["gene"]: n for n in json.loads(path.read_text())}


def _load_de_csv(path: Path, field: str) -> dict[str, int]:
    if not path.exists():
        return {}
    with path.open() as fh:
        return {r["gene"]: int(r[field]) for r in csv.DictReader(fh)}


def _load_collectri_counts() -> dict[str, int]:
    path = DATA / "collectri_human.csv"
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    with path.open() as fh:
        for r in csv.DictReader(fh):
            counts[r["tf"]] = counts.get(r["tf"], 0) + 1
    return counts


def _load_agent_hypothesis() -> dict[str, Any]:
    path = DATA / "agent_run.json"
    if not path.exists():
        return {}
    agent = json.loads(path.read_text())
    return agent.get("hypothesis") or {}


def _load_condition_summary(gene: str) -> dict[str, dict[str, Any]]:
    path = DATA / "marson_de_full.csv"
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    with path.open() as fh:
        for row in csv.DictReader(fh):
            if row["target_contrast_gene_name"] != gene:
                continue
            out[row["culture_condition"]] = {
                "n_cells_target": int(float(row["n_cells_target"])),
                "n_up_genes": int(row["n_up_genes"]),
                "n_down_genes": int(row["n_down_genes"]),
                "n_total_de_genes": int(row["n_total_de_genes"]),
                "ontarget_effect_size": round(float(row["ontarget_effect_size"]), 3),
                "ontarget_significant": "yes" if row["ontarget_significant"] == "True" else "no",
                "ontarget_effect_category": row["ontarget_effect_category"],
            }
    return out


def _cond(node: dict[str, Any], name: str) -> dict[str, Any]:
    return node["conditions"].get(name, {})


def _cond_de(node: dict[str, Any], name: str) -> int:
    return int(_cond(node, name).get("n_de", 0))


def _cond_kd(node: dict[str, Any], name: str) -> str:
    return str(_cond(node, name).get("kd", ""))


def build_deep_dive() -> dict[str, Any]:
    backbone = _load_backbone()
    node = backbone["PGGT1B"]
    k562 = _load_de_csv(DATA / "replogle_k562_de.csv", "k562_de")
    rpe1 = _load_de_csv(DATA / "replogle_rpe1_de.csv", "rpe1_de")
    collectri = _load_collectri_counts()
    agent_h = _load_agent_hypothesis()
    condition_summary = _load_condition_summary("PGGT1B")

    facts = {
        "class": node["class"],
        "rest_de": _cond_de(node, "Rest"),
        "rest_kd": _cond_kd(node, "Rest"),
        "stim8hr_de": _cond_de(node, "Stim8hr"),
        "stim8hr_kd": _cond_kd(node, "Stim8hr"),
        "stim48hr_de": _cond_de(node, "Stim48hr"),
        "stim48hr_kd": _cond_kd(node, "Stim48hr"),
        "k562_de": k562.get("PGGT1B"),
        "rpe1_de": rpe1.get("PGGT1B"),
        "collectri_targets": collectri.get("PGGT1B", 0),
        "is_canonical_tcell_gene": "PGGT1B" in P.CANON,
        "is_activation_module": P.is_activation_module(node),
        "is_essentiality_artifact": P.is_essentiality_artifact(node),
        "graph_edges_sliced": 0,
        "condition_summary": condition_summary,
    }

    return {
        "gene": "PGGT1B",
        "status": "evidence_attached",
        "replayability": "attested",
        "claim_scope": "hypothesis_to_test",
        "claim": agent_h.get(
            "hypothesis",
            "PGGT1B is a stimulation-gated, cell-type-specific regulator of the CD4+ T-cell activation transcriptome.",
        ),
        "facts": facts,
        "prospect_read": (
            "PGGT1B has a large stimulated CD4+ transcriptional footprint at 8h with on-target knockdown, "
            "a smaller Rest footprint, no broad K562 footprint, and no CollecTRI regulon annotation."
        ),
        "assay_readout": (
            "repeat CRISPRi or orthogonal knockdown in stimulated primary CD4+ T cells; measure activation "
            "markers, targeted RNA-seq at 8h and 48h, and prenylation-linked RHOA or RAC pathway readouts"
        ),
        "validation_plan": {
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "sample": "primary human CD4+ T cells",
            "intervention": "CRISPRi knockdown plus an orthogonal knockdown or small-molecule prenylation perturbation",
            "primary_readout": "activation-marker flow cytometry plus targeted RNA-seq at 8h and 48h",
            "mechanism_readouts": [
                "RHOA or RAC pathway activity",
                "alpha4beta7 surface expression if homing biology is in scope",
                "prenylation-sensitive localization or signaling assay",
            ],
            "negative_controls": [
                "non-targeting guide",
                "safe-harbor guide",
                "unstimulated matched culture",
            ],
            "positive_controls": ["VAV1", "LAT", "CD3E"],
            "expected_pattern": (
                "advance only if stimulated PGGT1B perturbation shifts the activation program while Rest and "
                "non-immune controls remain comparatively small"
            ),
            "stop_rules": [
                "failed on-target knockdown in the stimulated condition",
                "Rest-only transcriptional shift",
                "broad K562 or RPE1 effect on replication",
                "canonical effector-only readout without upstream transcriptome movement",
            ],
        },
        "literature_context": [
            {
                "title": "Inhibiting PGGT1B disrupts RHOA function and T-cell intestinal homing in mouse colitis",
                "journal": "Gastroenterology",
                "year": 2019,
                "doi": "10.1053/j.gastro.2019.07.007",
                "url": "https://www.sciencedirect.com/science/article/pii/S0016508519410871",
                "why_it_matters": "mouse CD4+ T-cell PGGT1B links prenylation, RHOA function, alpha4beta7 expression, and intestinal inflammation",
            },
            {
                "title": "Protein prenylation drives discrete signaling programs for effector Treg differentiation and maintenance",
                "journal": "Cell Metabolism",
                "year": 2020,
                "doi": "10.1016/j.cmet.2020.10.022",
                "url": "https://www.cell.com/cell-metabolism/fulltext/S1550-4131(20)30591-X",
                "why_it_matters": "mouse Treg work places Pggt1b upstream of TCR-dependent transcriptional programming and Rac-mediated signaling",
            },
        ],
        "caveats": [
            "Stim48hr is not scored as on-target because the screen reports no on-target knockdown in that condition.",
            "The current frontier has no sliced PGGT1B gene-to-gene edge neighborhood, so the packet uses summary-count evidence.",
            "External papers make the mechanism plausible; they do not move accepted Prospect state.",
        ],
    }


def _markdown(dive: dict[str, Any]) -> str:
    f = dive["facts"]
    refs = dive["literature_context"]
    condition_summary = f.get("condition_summary", {})
    lines = [
        "# PGGT1B deep dive",
        "",
        "Status: `evidence_attached`. Claim scope: hypothesis to test.",
        "",
        "## Prospect read",
        "",
        dive["prospect_read"],
        "",
        "## Exact frozen facts",
        "",
        "| fact | value |",
        "|---|---:|",
        f"| Rest DE genes | {f['rest_de']} |",
        f"| Rest knockdown | {f['rest_kd']} |",
        f"| Stim8hr DE genes | {f['stim8hr_de']} |",
        f"| Stim8hr knockdown | {f['stim8hr_kd']} |",
        f"| Stim48hr DE genes | {f['stim48hr_de']} |",
        f"| Stim48hr knockdown | {f['stim48hr_kd']} |",
        f"| K562 DE genes | {f['k562_de']} |",
        f"| RPE1 DE genes | {f['rpe1_de'] if f['rpe1_de'] is not None else 'not measured'} |",
        f"| CollecTRI targets | {f['collectri_targets']} |",
        f"| Current PGGT1B graph edges | {f['graph_edges_sliced']} |",
        "",
        "## Condition-level summary",
        "",
        "| condition | target cells | up genes | down genes | total DE | effect | on-target |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for condition in ["Rest", "Stim8hr", "Stim48hr"]:
        row = condition_summary.get(condition, {})
        lines.append(
            f"| {condition} | {row.get('n_cells_target', 'n/a')} | "
            f"{int(row.get('n_up_genes', 0)):,} | {int(row.get('n_down_genes', 0)):,} | "
            f"{int(row.get('n_total_de_genes', 0)):,} | {row.get('ontarget_effect_size', 'n/a')} | "
            f"{row.get('ontarget_effect_category', 'n/a')} |"
        )
    lines += [
        "",
        "## Hypothesis",
        "",
        dive["claim"],
        "",
        "## Literature context",
        "",
    ]
    for ref in refs:
        lines.append(
            f"- {ref['year']}, {ref['journal']}, DOI [{ref['doi']}]({ref['url']}): {ref['why_it_matters']}."
        )
    lines += [
        "",
        "## Assay decision plan",
        "",
        f"- Sample: {dive['validation_plan']['sample']}.",
        f"- Intervention: {dive['validation_plan']['intervention']}.",
        f"- Primary readout: {dive['validation_plan']['primary_readout']}.",
        f"- Expected pattern: {dive['validation_plan']['expected_pattern']}.",
        f"- Negative controls: {', '.join(dive['validation_plan']['negative_controls'])}.",
        f"- Positive controls: {', '.join(dive['validation_plan']['positive_controls'])}.",
        "",
        "Stop rules:",
        "",
    ]
    lines += [f"- {rule}" for rule in dive["validation_plan"]["stop_rules"]]
    lines += [
        "",
        "## Wet-lab follow-up",
        "",
        dive["assay_readout"] + ".",
        "",
        "## Caveats",
        "",
    ]
    lines += [f"- {c}" for c in dive["caveats"]]
    lines += [
        "",
        "Rebuild:",
        "",
        "```bash",
        "python frontier/pggt1b_deep_dive.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_deep_dive(out_json: Path = OUT_JSON, out_doc: Path = OUT_DOC) -> dict[str, Any]:
    dive = build_deep_dive()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(dive, indent=2) + "\n")
    out_doc.write_text(_markdown(dive))
    return dive


def main() -> None:
    write_deep_dive()
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
