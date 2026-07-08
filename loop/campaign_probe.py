"""Claude probes for the proposal-only campaign leaderboard.

The live path asks Claude to cross-examine campaign candidates with frozen
lookup tools. The durable artifact compares Claude's recommendations to the
deterministic review lanes without moving accepted state.
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

from frontier.agent_campaign import build_campaign
from frontier.campaign_review import build_review
from loop.run import load_env, price_for

DATA = ROOT / "examples" / "data"
OUT_JSON = DATA / "campaign_agent_probe.json"
OUT_DOC = ROOT / "docs" / "CAMPAIGN_AGENT_PROBE.md"
MODEL = "claude-opus-4-8"

VALID_RECOMMENDATIONS = {
    "advance_to_assay_design",
    "advance_if_capacity_allows",
    "hold_as_ranked_backup",
    "use_as_regulon_anchor",
}

DECISION_ORDER = {
    "hold_as_ranked_backup": 1,
    "advance_if_capacity_allows": 2,
    "use_as_regulon_anchor": 2,
    "advance_to_assay_design": 3,
}

SAMPLE_DECISIONS = [
    {
        "gene": "PGGT1B",
        "recommendation": "advance_to_assay_design",
        "rationale": "Largest stimulated footprint and low non-immune transfer.",
    },
    {
        "gene": "RCC1L",
        "recommendation": "advance_if_capacity_allows",
        "rationale": "Strong stimulated signal, but not the top assay row.",
    },
    {
        "gene": "MCAT",
        "recommendation": "hold_as_ranked_backup",
        "rationale": "Useful backup with a smaller signal.",
    },
]


def _candidate_facts(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "gene": row["gene"],
        "score": row["score"],
        "status": row["status"],
        "trust_boundary": row["trust_boundary"],
        "stim_max_de": row["stim_max_de"],
        "strongest_condition": row["strongest_condition"],
        "strongest_kd": row["strongest_kd"],
        "rest_de": row["rest_de"],
        "k562_de": row["k562_de"],
        "rpe1_de": row["rpe1_de"],
        "known_regulon_targets": row["known_regulon_targets"],
        "evidence": row["evidence"],
        "main_risk": row["main_risk"],
        "what_would_weaken": row["what_would_weaken"],
    }


def t_campaign_candidates(limit: int = 5) -> dict[str, Any]:
    """Return the top proposal-only campaign candidates without review decisions."""
    campaign = build_campaign(limit=limit)
    return {
        "campaign_id": campaign["campaign_id"],
        "status": campaign["status"],
        "trust_boundary": campaign["trust_boundary"],
        "acceptance": campaign["acceptance"],
        "candidates": [_candidate_facts(row) for row in campaign["candidates"]],
    }


def t_campaign_candidate(gene: str) -> dict[str, Any]:
    """Return one proposal-only candidate row without the deterministic review decision."""
    gene = gene.upper()
    campaign = build_campaign(limit=20)
    by_gene = {row["gene"]: row for row in campaign["candidates"]}
    row = by_gene.get(gene)
    if not row:
        return {"gene": gene, "in_campaign": False}
    return {"in_campaign": True, **_candidate_facts(row)}


def t_check_regulator(gene: str) -> dict[str, Any]:
    from loop.agent import t_check_regulator as tool
    return tool(gene)


def t_cross_cell_type(gene: str) -> dict[str, Any]:
    from loop.agent import t_cross_cell_type as tool
    return tool(gene)


def t_known_regulon(gene: str) -> dict[str, Any]:
    from loop.agent import t_known_regulon as tool
    return tool(gene)


TOOLS = [
    {
        "name": "campaign_candidates",
        "description": "Return the top proposal-only campaign candidates and frozen evidence atoms.",
        "input_schema": {
            "type": "object",
            "properties": {"limit": {"type": "integer"}},
        },
    },
    {
        "name": "campaign_candidate",
        "description": "Return one proposal-only campaign candidate and frozen evidence atoms.",
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
    {
        "name": "check_regulator",
        "description": "Frozen lookup: per-condition DE profile, knockdown status, class, and key flags.",
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
    {
        "name": "known_regulon",
        "description": "Frozen lookup: CollecTRI target count for a gene.",
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
]

DISPATCH = {
    "campaign_candidates": t_campaign_candidates,
    "campaign_candidate": t_campaign_candidate,
    "check_regulator": t_check_regulator,
    "cross_cell_type": t_cross_cell_type,
    "known_regulon": t_known_regulon,
}


def _alignment(agent: str, deterministic: str) -> str:
    if agent not in VALID_RECOMMENDATIONS:
        return "needs_human_review"
    a = DECISION_ORDER.get(agent)
    d = DECISION_ORDER.get(deterministic)
    if a == d:
        return "aligned"
    if a is None or d is None:
        return "needs_human_review"
    return "more_aggressive" if a > d else "more_cautious"


def _probe_id(rows: list[dict[str, Any]], model: str) -> str:
    basis = json.dumps({"model": model, "rows": rows}, sort_keys=True)
    return "campaign_probe_" + hashlib.sha256(basis.encode()).hexdigest()[:16]


def build_probe(
    decisions: list[dict[str, Any]],
    model: str,
    tool_calls: list[dict[str, Any]],
    cost_usd: float,
    requested_limit: int | None = None,
) -> dict[str, Any]:
    review = build_review()
    review_by_gene = {row["gene"]: row for row in review["rows"]}
    campaign_by_gene = {row["gene"]: row for row in build_campaign(limit=20)["candidates"]}
    rows = []
    for item in decisions:
        gene = str(item.get("gene", "")).upper()
        if gene not in review_by_gene or gene not in campaign_by_gene:
            continue
        deterministic = review_by_gene[gene]
        recommendation = str(item.get("recommendation", "")).strip()
        row = {
            "rank": campaign_by_gene[gene]["rank"],
            "gene": gene,
            "status": "evidence_attached",
            "trust_boundary": "proposal_only",
            "deterministic_lane": deterministic["review_lane"],
            "deterministic_decision": deterministic["decision"],
            "agent_recommendation": recommendation,
            "alignment": _alignment(recommendation, deterministic["decision"]),
            "agent_rationale": str(item.get("rationale", "")).strip(),
            "stimulated_signal": deterministic["stimulated_signal"],
            "specificity": deterministic["specificity"],
            "stop_rules": deterministic["stop_rules"],
        }
        rows.append(row)
    rows.sort(key=lambda row: row["rank"])
    summary = Counter(row["alignment"] for row in rows)
    campaign = build_campaign(limit=20)
    requested = requested_limit if requested_limit is not None else len(rows)
    missing = max(requested - len(rows), 0)
    return {
        "probe_id": _probe_id(rows, model),
        "title": "Campaign agent probes",
        "status": "evidence_attached",
        "trust_boundary": "proposal_only",
        "acceptance": False,
        "scope": "model cross-examination of proposal-only campaign rows",
        "source": "loop.campaign_probe",
        "campaign_id": campaign["campaign_id"],
        "model": model,
        "candidate_count": len(rows),
        "coverage": {
            "requested_limit": requested,
            "returned_decisions": len(rows),
            "coverage_status": "complete" if missing == 0 else "partial",
            "missing_decisions": missing,
        },
        "cost_usd": round(cost_usd, 4),
        "tool_call_count": len(tool_calls),
        "tool_calls": tool_calls,
        "summary": dict(sorted(summary.items())),
        "rows": rows,
    }


def _markdown(probe: dict[str, Any]) -> str:
    lines = [
        "# Campaign agent probes",
        "",
        "Status: `evidence_attached`. Trust boundary: proposal only. No candidate enters accepted state from these probes.",
        "",
        (
            f"Probe: `{probe['probe_id']}`. Campaign: `{probe['campaign_id']}`. "
            f"Model: `{probe['model']}`. Tool calls: {probe['tool_call_count']}."
        ),
        (
            f"Coverage: {probe['coverage']['returned_decisions']} returned / "
            f"{probe['coverage']['requested_limit']} requested. Complete: "
            f"{'yes' if probe['coverage']['coverage_status'] == 'complete' else 'no'}."
        ),
        "",
        "## Summary",
        "",
    ]
    for key, value in probe["summary"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Probe rows",
        "",
        "| rank | gene | deterministic decision | agent recommendation | alignment | rationale |",
        "|---:|---|---|---|---|---|",
    ]
    for row in probe["rows"]:
        lines.append(
            f"| {row['rank']} | {row['gene']} | {row['deterministic_decision']} | "
            f"{row['agent_recommendation']} | {row['alignment']} | {row['agent_rationale']} |"
        )
    lines += [
        "",
        "Rebuild with a live model run:",
        "",
        "```bash",
        f"python loop/campaign_probe.py --limit {probe['coverage']['requested_limit']}",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_probe(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
    decisions: list[dict[str, Any]] | None = None,
    model: str = MODEL,
    tool_calls: list[dict[str, Any]] | None = None,
    cost_usd: float = 0.0,
    requested_limit: int | None = None,
) -> dict[str, Any]:
    probe = build_probe(
        decisions=decisions or SAMPLE_DECISIONS,
        model=model,
        tool_calls=tool_calls or [],
        cost_usd=cost_usd,
        requested_limit=requested_limit,
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(probe, indent=2) + "\n")
    out_doc.write_text(_markdown(probe))
    return probe


def parse_decisions(text: str) -> list[dict[str, Any]]:
    candidates: list[str] = []
    stripped = text.strip()
    candidates.append(stripped)
    for line in reversed(stripped.splitlines()):
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


def _goal(limit: int) -> str:
    return f"""You are cross-examining a proposal-only campaign leaderboard from Prospect.
Every tool you call is a frozen lookup against released data or a deterministic campaign row.

Task: inspect the top {limit} campaign candidates. For each candidate, use tools to check the
campaign row, the regulator profile, cross-cell-type behavior, and known regulon context. Then
recommend one of exactly:
- advance_to_assay_design
- advance_if_capacity_allows
- hold_as_ranked_backup
- use_as_regulon_anchor

Return a JSON object on its own line:
{{"decisions":[{{"gene":"...","recommendation":"...","rationale":"one sentence grounded in tool facts"}}]}}

Do not claim wet-lab truth. Do not accept state. Your output is a proposal-only review artifact."""


def run_live(limit: int) -> dict[str, Any]:
    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set in .env")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": _goal(limit)}]
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
    return write_probe(
        decisions=decisions,
        model=MODEL,
        tool_calls=transcript,
        cost_usd=cost,
        requested_limit=limit,
    )


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="campaign_probe")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--sample", action="store_true", help="write a fixture probe without calling the API")
    ap.add_argument("--out-json", type=Path, default=OUT_JSON)
    ap.add_argument("--out-doc", type=Path, default=OUT_DOC)
    args = ap.parse_args(argv)
    if args.sample:
        probe = write_probe(out_json=args.out_json, out_doc=args.out_doc)
    else:
        probe = run_live(limit=args.limit)
        if args.out_json != OUT_JSON or args.out_doc != OUT_DOC:
            write_probe(
                out_json=args.out_json,
                out_doc=args.out_doc,
                decisions=[{
                    "gene": row["gene"],
                    "recommendation": row["agent_recommendation"],
                    "rationale": row["agent_rationale"],
                } for row in probe["rows"]],
                model=probe["model"],
                tool_calls=probe["tool_calls"],
                cost_usd=probe["cost_usd"],
                requested_limit=probe["coverage"]["requested_limit"],
            )
    print(f"wrote {args.out_json} ({probe['candidate_count']} candidates)")
    print(f"wrote {args.out_doc}")


if __name__ == "__main__":
    main()
