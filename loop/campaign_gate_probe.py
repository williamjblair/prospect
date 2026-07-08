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
        "gene": "RWDD2B",
        "gate_recommendation": "add_control",
        "rationale": "The higher Rest signal makes matched unstimulated culture a required control.",
    },
    {
        "gene": "CCDC22",
        "gate_recommendation": "lower_priority",
        "rationale": "The gate is reasonable, but lower magnitude makes it less urgent than stronger rows.",
    },
    {
        "gene": "CYB5RL",
        "gate_recommendation": "gate_sufficient",
        "rationale": "The K562-inert specificity and matched-condition gate cover the main promotion risk.",
    },
]


def _triage_rows() -> list[dict[str, Any]]:
    return build_triage()["rows"]


def triage_genes() -> list[str]:
    """Return current disagreement-gate genes in rank order."""
    return [row["gene"] for row in _triage_rows()]


def parse_gene_list(value: str | None) -> list[str] | None:
    """Parse a comma-separated focused gate list in current triage order."""
    if not value:
        return None
    requested = []
    seen = set()
    for raw in value.split(","):
        gene = raw.strip().upper()
        if not gene or gene in seen:
            continue
        requested.append(gene)
        seen.add(gene)
    triage_order = triage_genes()
    triage_set = set(triage_order)
    invalid = [gene for gene in requested if gene not in triage_set]
    if invalid:
        raise ValueError(f"{', '.join(invalid)} not in campaign disagreement triage")
    requested_set = set(requested)
    return [gene for gene in triage_order if gene in requested_set]


def chunk_gene_batches(genes: list[str], chunk_size: int) -> list[list[str]]:
    """Split gate genes into non-empty rank-preserving batches."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    return [genes[i:i + chunk_size] for i in range(0, len(genes), chunk_size)]


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
    requested_genes: list[str] | None = None,
) -> dict[str, Any]:
    triage = build_triage()
    triage_by_gene = {row["gene"]: row for row in triage["rows"]}
    requested_gene_list = [gene.upper() for gene in requested_genes] if requested_genes is not None else []
    requested_set = set(requested_gene_list)
    seen_genes: set[str] = set()
    rows = []
    for item in decisions:
        gene = str(item.get("gene", "")).upper()
        if gene not in triage_by_gene:
            continue
        if requested_set and gene not in requested_set:
            continue
        if gene in seen_genes:
            continue
        seen_genes.add(gene)
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
    returned_genes = [row["gene"] for row in rows]
    requested_gene_list = requested_gene_list or returned_genes
    requested = len(requested_gene_list)
    missing_genes = [gene for gene in requested_gene_list if gene not in returned_genes]
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
        "coverage": {
            "requested_limit": requested,
            "returned_decisions": len(rows),
            "coverage_status": "complete" if not missing_genes else "partial",
            "missing_decisions": len(missing_genes),
            "requested_genes": requested_gene_list,
            "returned_genes": returned_genes,
            "missing_genes": missing_genes,
        },
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
        (
            f"Coverage: {probe['coverage']['returned_decisions']} returned / "
            f"{probe['coverage']['requested_limit']} requested. Complete: "
            f"{'yes' if probe['coverage']['coverage_status'] == 'complete' else 'no'}."
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
    requested_genes: list[str] | None = None,
) -> dict[str, Any]:
    probe = build_gate_probe(
        decisions=decisions or SAMPLE_DECISIONS,
        model=model,
        tool_calls=tool_calls or [],
        cost_usd=cost_usd,
        requested_genes=requested_genes,
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(probe, indent=2) + "\n")
    out_doc.write_text(_markdown(probe))
    return probe


def merge_probe_decisions(existing_probe: dict[str, Any], followup_probe: dict[str, Any]) -> list[dict[str, str]]:
    """Return decision inputs from two probe artifacts, preserving first decision per gene."""
    decisions: list[dict[str, str]] = []
    seen: set[str] = set()
    for probe in (existing_probe, followup_probe):
        for row in probe.get("rows", []):
            gene = str(row.get("gene", "")).upper()
            if not gene or gene in seen:
                continue
            seen.add(gene)
            decisions.append({
                "gene": gene,
                "gate_recommendation": str(row.get("gate_recommendation", "")),
                "rationale": str(row.get("gate_rationale", row.get("rationale", ""))),
            })
    return decisions


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


def _goal_for_genes(genes: list[str]) -> str:
    joined = ", ".join(genes)
    return f"""You are pressure-testing Prospect's proposal-only disagreement assay gates.
Every tool is a frozen lookup against released data or an existing deterministic gate row.

Task: inspect exactly these campaign disagreement gates: {joined}.
For each row, call triage_row, check_regulator, and cross_cell_type. Recommend exactly one:
- gate_sufficient
- add_control
- lower_priority

Return a JSON object on its own line with exactly one decision for each requested gene:
{{"decisions":[{{"gene":"...","gate_recommendation":"...","rationale":"one sentence grounded in tool facts"}}]}}

Do not claim wet-lab truth. Do not accept state. This is a proposal-only review artifact."""


def _run_live_prompt(goal: str, requested_genes: list[str] | None = None) -> dict[str, Any]:
    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set in .env")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": goal}]
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
                "requested_genes": requested_genes or [],
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
    return {"decisions": decisions, "tool_calls": transcript, "cost_usd": cost}


def run_live(
    chunk_size: int | None = None,
    requested_genes: list[str] | None = None,
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
) -> dict[str, Any]:
    requested_genes = requested_genes or triage_genes()
    if chunk_size is not None:
        decisions: list[dict[str, Any]] = []
        transcript: list[dict[str, Any]] = []
        cost = 0.0
        for batch in chunk_gene_batches(requested_genes, chunk_size):
            result = _run_live_prompt(_goal_for_genes(batch), requested_genes=batch)
            decisions.extend(result["decisions"])
            transcript.extend(result["tool_calls"])
            cost += result["cost_usd"]
        return write_gate_probe(
            out_json=out_json,
            out_doc=out_doc,
            decisions=decisions,
            model=MODEL,
            tool_calls=transcript,
            cost_usd=cost,
            requested_genes=requested_genes,
        )

    result = _run_live_prompt(_goal(), requested_genes=requested_genes)
    return write_gate_probe(
        out_json=out_json,
        out_doc=out_doc,
        decisions=result["decisions"],
        model=MODEL,
        tool_calls=result["tool_calls"],
        cost_usd=result["cost_usd"],
        requested_genes=requested_genes,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="campaign_gate_probe")
    parser.add_argument("--sample", action="store_true", help="write a fixture gate probe without calling the API")
    parser.add_argument("--chunk-size", type=int, help="run live gate probes in rank-ordered gene batches")
    parser.add_argument("--genes", help="comma-separated disagreement gate genes to request")
    parser.add_argument("--merge-existing", type=Path, help="merge a focused live probe with an existing gate-probe artifact")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-doc", type=Path, default=OUT_DOC)
    args = parser.parse_args(argv)
    requested_genes = parse_gene_list(args.genes)
    if args.sample:
        requested = requested_genes or [item["gene"] for item in SAMPLE_DECISIONS]
        probe = write_gate_probe(out_json=args.out_json, out_doc=args.out_doc, requested_genes=requested)
    else:
        live_probe = run_live(
            chunk_size=args.chunk_size,
            requested_genes=requested_genes,
            out_json=args.out_json,
            out_doc=args.out_doc,
        )
        probe = live_probe
        if args.merge_existing:
            existing = json.loads(args.merge_existing.read_text())
            decisions = merge_probe_decisions(existing, live_probe)
            requested = triage_genes()
            probe = write_gate_probe(
                out_json=args.out_json,
                out_doc=args.out_doc,
                decisions=decisions,
                model=live_probe["model"],
                tool_calls=existing.get("tool_calls", []) + live_probe["tool_calls"],
                cost_usd=float(existing.get("cost_usd", 0.0)) + float(live_probe["cost_usd"]),
                requested_genes=requested,
            )
    print(f"wrote {args.out_json} ({probe['candidate_count']} candidates)")
    print(f"wrote {args.out_doc}")


if __name__ == "__main__":
    main()
