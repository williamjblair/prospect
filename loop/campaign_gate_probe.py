"""Claude probes for campaign disagreement assay gates.

This artifact asks whether the deterministic gates produced by campaign triage
are sufficient, need another control, or should be lower priority. It is a
proposal-only review artifact and never moves accepted state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.campaign_triage import build_triage
from loop.run import load_env, price_for

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "campaign_gate_probe.json"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_GATE_PROBE.md"
MODEL = "claude-opus-4-8"

VALID_GATE_RECOMMENDATIONS = {"gate_sufficient", "add_control", "lower_priority"}

SAMPLE_DECISIONS = [
    {
        "gene": "RCC1L",
        "gate_recommendation": "gate_sufficient",
        "rationale": "The matched Rest, Stim8hr, and Stim48hr orthogonal knockdown gate covers the main risk.",
    },
    {
        "gene": "MCAT",
        "gate_recommendation": "add_control",
        "rationale": "The Rest knockdown caveat needs a second guide and transfer check before capacity is spent.",
    },
    {
        "gene": "RWDD2B",
        "gate_recommendation": "add_control",
        "rationale": "The higher Rest signal makes matched unstimulated culture a required control.",
    },
    {
        "gene": "CCDC22",
        "gate_recommendation": "lower_priority",
        "rationale": "The gate is reasonable, but lower magnitude makes it less urgent than stronger rows.",
    },
]


def _triage_rows() -> list[dict[str, Any]]:
    return build_triage()["rows"]


def t_triage_rows() -> dict[str, Any]:
    """Return the current proposal-only disagreement gate rows."""
    triage = build_triage()
    return {
        "status": triage["status"],
        "trust_boundary": triage["trust_boundary"],
        "acceptance": triage["acceptance"],
        "source_probe_id": triage["source_probe_id"],
        "rows": triage["rows"],
    }


def t_triage_row(gene: str) -> dict[str, Any]:
    """Return one proposal-only disagreement gate row."""
    gene = gene.upper()
    by_gene = {row["gene"]: row for row in _triage_rows()}
    row = by_gene.get(gene)
    if not row:
        return {"gene": gene, "in_triage": False}
    return {"in_triage": True, **row}


def t_check_regulator(gene: str) -> dict[str, Any]:
    from loop.agent import t_check_regulator as tool
    return tool(gene)


def t_cross_cell_type(gene: str) -> dict[str, Any]:
    from loop.agent import t_cross_cell_type as tool
    return tool(gene)


TOOLS = [
    {
        "name": "triage_rows",
        "description": "Return proposal-only campaign disagreement gates and frozen evidence fields.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "triage_row",
        "description": "Return one proposal-only campaign disagreement gate row.",
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
    {
        "name": "check_regulator",
        "description": "Frozen lookup: per-condition DE profile, knockdown status, class, and flags.",
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
    {
        "name": "cross_cell_type",
        "description": "Frozen lookup: whether the perturbation has broad non-immune effects in K562 or RPE1.",
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
]

DISPATCH = {
    "triage_rows": t_triage_rows,
    "triage_row": t_triage_row,
    "check_regulator": t_check_regulator,
    "cross_cell_type": t_cross_cell_type,
}


def _probe_id(rows: list[dict[str, Any]], model: str) -> str:
    basis = json.dumps({"model": model, "rows": rows}, sort_keys=True)
    return "campaign_gate_probe_" + hashlib.sha256(basis.encode()).hexdigest()[:16]


def _public_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return [_public_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _public_value(item) for key, item in value.items()}
    return value


def build_gate_probe(
    decisions: list[dict[str, Any]],
    model: str,
    tool_calls: list[dict[str, Any]],
    cost_usd: float,
) -> dict[str, Any]:
    triage = build_triage()
    triage_by_gene = {row["gene"]: row for row in triage["rows"]}
    rows = []
    for item in decisions:
        gene = str(item.get("gene", "")).upper()
        if gene not in triage_by_gene:
            continue
        recommendation = str(item.get("gate_recommendation", "")).strip()
        if recommendation not in VALID_GATE_RECOMMENDATIONS:
            recommendation = "add_control"
        source = triage_by_gene[gene]
        rows.append({
            "rank": source["rank"],
            "gene": gene,
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "alignment": source["alignment"],
            "source_triage_decision": source["triage_decision"],
            "deterministic_decision": source["deterministic_decision"],
            "agent_recommendation": source["agent_recommendation"],
            "assay_gate": source["assay_gate"],
            "gate_recommendation": recommendation,
            "gate_rationale": str(item.get("rationale", "")).strip(),
            "stimulated_signal": source["stimulated_signal"],
            "specificity": source["specificity"],
            "stop_rules": source["stop_rules"],
        })
    rows.sort(key=lambda row: row["rank"])
    summary = Counter(row["gate_recommendation"] for row in rows)
    return {
        "probe_id": _probe_id(rows, model),
        "title": "Campaign gate probe",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "scope": "model pressure test of deterministic disagreement assay gates",
        "source": "loop.campaign_gate_probe",
        "source_triage_id": triage["source_probe_id"],
        "campaign_id": triage["campaign_id"],
        "model": model,
        "candidate_count": len(rows),
        "cost_usd": round(cost_usd, 4),
        "tool_call_count": len(tool_calls),
        "tool_calls": _public_value(tool_calls),
        "valid_recommendations": sorted(VALID_GATE_RECOMMENDATIONS),
        "summary": dict(sorted(summary.items())),
        "rows": rows,
    }


def _markdown(probe: dict[str, Any]) -> str:
    lines = [
        "# Campaign gate probe",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. Gate pressure can add controls or lower priority; it cannot accept state.",
        "",
        (
            f"Probe: `{probe['probe_id']}`. Source triage: `{probe['source_triage_id']}`. "
            f"Model: `{probe['model']}`. Tool calls: {probe['tool_call_count']}."
        ),
        "",
        "Allowed recommendations: `gate_sufficient`, `add_control`, `lower_priority`.",
        "",
        "## Summary",
        "",
    ]
    for key, value in probe["summary"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Gate rows",
        "",
        "| rank | gene | triage decision | gate recommendation | rationale |",
        "|---:|---|---|---|---|",
    ]
    for row in probe["rows"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['source_triage_decision']} | "
            f"{row['gate_recommendation']} | {row['gate_rationale']} |"
        )
    lines += [
        "",
        "Fixture rebuild:",
        "",
        "```bash",
        "python loop/campaign_gate_probe.py --sample",
        "```",
        "",
        "Live rebuild:",
        "",
        "```bash",
        "python loop/campaign_gate_probe.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_gate_probe(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
    decisions: list[dict[str, Any]] | None = None,
    model: str = MODEL,
    tool_calls: list[dict[str, Any]] | None = None,
    cost_usd: float = 0.0,
) -> dict[str, Any]:
    probe = build_gate_probe(
        decisions=decisions or SAMPLE_DECISIONS,
        model=model,
        tool_calls=tool_calls or [],
        cost_usd=cost_usd,
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(probe, indent=2) + "\n")
    out_doc.write_text(_markdown(probe))
    return probe


def parse_decisions(text: str) -> list[dict[str, Any]]:
    candidates: list[str] = [text.strip()]
    for line in reversed(text.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") or line.startswith("["):
            candidates.append(line)
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict) and isinstance(parsed.get("decisions"), list):
            return parsed["decisions"]
        if isinstance(parsed, list):
            return parsed
    return []


def _goal() -> str:
    return """You are pressure-testing Prospect's proposal-only disagreement assay gates.
Every tool is a frozen lookup against released data or an existing deterministic gate row.

Task: inspect every campaign disagreement gate. For each row, call triage_row, check_regulator,
and cross_cell_type. Recommend exactly one:
- gate_sufficient
- add_control
- lower_priority

Return a JSON object on its own line:
{"decisions":[{"gene":"...","gate_recommendation":"...","rationale":"one sentence grounded in tool facts"}]}

Do not claim wet-lab truth. Do not accept state. This is a proposal-only review artifact."""


def run_live() -> dict[str, Any]:
    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set in .env")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": _goal()}]
    transcript: list[dict[str, Any]] = []
    tin = 0
    tout = 0
    final_text = ""
    for rnd in range(8):
        msg = client.messages.create(
            model=MODEL,
            max_tokens=5000,
            thinking={"type": "adaptive"},
            tools=TOOLS,
            messages=messages,
        )
        tin += msg.usage.input_tokens
        tout += msg.usage.output_tokens
        messages.append({"role": "assistant", "content": msg.content})
        text = "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")
        tool_uses = [block for block in msg.content if getattr(block, "type", "") == "tool_use"]
        if not tool_uses:
            final_text = text
            break
        results = []
        for block in tool_uses:
            tool_input = dict(block.input)
            result = DISPATCH[block.name](**tool_input)
            transcript.append({
                "round": rnd + 1,
                "tool": block.name,
                "input": tool_input,
                "result": result,
            })
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result)[:5000],
            })
        messages.append({"role": "user", "content": results})
    decisions = parse_decisions(final_text)
    pin, pout = price_for(MODEL)
    cost = tin / 1e6 * pin + tout / 1e6 * pout
    return write_gate_probe(decisions=decisions, model=MODEL, tool_calls=transcript, cost_usd=cost)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="campaign_gate_probe")
    parser.add_argument("--sample", action="store_true", help="write a fixture gate probe without calling the API")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-doc", type=Path, default=OUT_DOC)
    args = parser.parse_args(argv)
    if args.sample:
        probe = write_gate_probe(out_json=args.out_json, out_doc=args.out_doc)
    else:
        probe = run_live()
        if args.out_json != OUT_JSON or args.out_doc != OUT_DOC:
            write_gate_probe(
                out_json=args.out_json,
                out_doc=args.out_doc,
                decisions=[{
                    "gene": row["gene"],
                    "gate_recommendation": row["gate_recommendation"],
                    "rationale": row["gate_rationale"],
                } for row in probe["rows"]],
                model=probe["model"],
                tool_calls=probe["tool_calls"],
                cost_usd=probe["cost_usd"],
            )
    print(f"wrote {args.out_json} ({probe['candidate_count']} candidates)")
    print(f"wrote {args.out_doc}")


if __name__ == "__main__":
    main()
