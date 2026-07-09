"""Anti-overclaim audit for Prospect public surfaces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DOC = ROOT / "docs" / "RIGOR_AUDIT.md"

PUBLIC_SURFACES = [
    "README.md",
    "docs/SUBMISSION.md",
    "docs/DEMO.md",
    "docs/DEMO_RECORDING_RUNBOOK.md",
    "docs/JUDGE_HANDOUT.md",
    "docs/JUDGE_TECHNICAL_NOTE.md",
    "docs/DEPLOY_READINESS.md",
    "docs/RECEIPT_BRIDGE.md",
    "docs/RUN_YOUR_OWN_CLAIM.md",
    "docs/PGGT1B_DEFENDED_EVIDENCE.md",
    "docs/FINDINGS.md",
    "web/app/page.tsx",
]

BLOCKED_PHRASES = [
    "PGGT1B clears the fixed bar",
    "fixed-bar lead",
    "independently validated",
    "signature is wrong",
    "verified biology",
    "validated module",
    "10 datasets",
    "0 cleared",
    "claims were wrong",
]

TRACEABLE_CLAIMS = [
    {
        "claim": "48-64% overclaim pressure",
        "artifact": "/data/overclaim_counter.json",
        "command": "./prospect overclaim-counter",
        "surface": "web/app/page.tsx",
    },
    {
        "claim": "real Claude Science export typed as drivers, passengers, and not_assayed",
        "artifact": "/data/claude_science_acceptance_demo.json",
        "command": "python examples/claude_science_connector_client.py --json",
        "surface": "web/app/page.tsx",
    },
    {
        "claim": "PGGT1B proposal-only lead worth testing",
        "artifact": "/data/pggt1b_defended_evidence.json",
        "command": "./prospect pggt1b-defended-evidence",
        "surface": "web/app/page.tsx",
    },
    {
        "claim": "five signed CD4+ findings",
        "artifact": "/data/finding_index.json",
        "command": "./prospect findings-index",
        "surface": "web/app/page.tsx",
    },
    {
        "claim": "receipt bridge returns proposal-only state",
        "artifact": "/data/receipt_bridge/receipt_contract.json",
        "command": "python examples/receipt_bridge_client.py --json",
        "surface": "docs/RECEIPT_BRIDGE.md",
    },
]

DOWNGRADES = [
    {
        "surface": "web/app/page.tsx",
        "before": "generic wrongness language",
        "after": "claims were contradicted by the frozen table",
    },
    {
        "surface": "web/app/page.tsx and docs",
        "before": "fixed-bar completion language for PGGT1B",
        "after": "PGGT1B is retained as a proposal-only lead worth testing",
    },
    {
        "surface": "docs/FINDINGS.md",
        "before": "validation language for a computational comparison",
        "after": "independently corroborated computation",
    },
]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def build_audit() -> dict[str, Any]:
    blocked_hits: list[dict[str, str]] = []
    for surface in PUBLIC_SURFACES:
        text = _read(surface)
        for phrase in BLOCKED_PHRASES:
            if phrase.lower() in text.lower():
                blocked_hits.append({"surface": surface, "phrase": phrase})

    trace_results = []
    for item in TRACEABLE_CLAIMS:
        text = _read(item["surface"])
        trace_results.append({
            **item,
            "artifact_present": item["artifact"] in text,
            "command_present": item["command"] in text,
        })

    return {
        "title": "Prospect anti-overclaim rigor audit",
        "surfaces": PUBLIC_SURFACES,
        "blocked_phrase_hits": blocked_hits,
        "traceable_claims": trace_results,
        "downgrades_made": DOWNGRADES,
        "framing_guards": {
            "claude_science": "driver-versus-passenger, not signature-is-wrong",
            "pggt1b": "proposal-only lead worth testing, not accepted biology",
            "acceptance": "accepted=false until human_signature_required",
            "ceiling": "Computation over released data, not wet-lab or clinical truth.",
        },
        "passed": not blocked_hits and all(row["artifact_present"] and row["command_present"] for row in trace_results),
    }


def _markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Prospect anti-overclaim rigor audit",
        "",
        f"Passed: `{'yes' if audit['passed'] else 'no'}`",
        "",
        "Ceiling: computation over released data, not wet-lab or clinical truth.",
        "",
        "## Public surfaces scanned",
        "",
    ]
    lines += [f"- `{surface}`" for surface in audit["surfaces"]]
    lines += ["", "## Downgrades made", ""]
    lines += [
        f"- `{row['surface']}`: `{row['before']}` became `{row['after']}`"
        for row in audit["downgrades_made"]
    ]
    lines += ["", "## Traceable headline claims", ""]
    lines += [
        f"- {row['claim']}: artifact `{row['artifact']}`, command `{row['command']}`"
        for row in audit["traceable_claims"]
    ]
    lines += ["", "## Blocked phrase hits", ""]
    if audit["blocked_phrase_hits"]:
        lines += [f"- `{row['surface']}`: `{row['phrase']}`" for row in audit["blocked_phrase_hits"]]
    else:
        lines.append("- none")
    lines += ["", "## Framing guards", ""]
    lines += [f"- {key}: {value}" for key, value in audit["framing_guards"].items()]
    return "\n".join(lines) + "\n"


def write_audit(out_doc: Path = OUT_DOC) -> dict[str, Any]:
    audit = build_audit()
    out_doc.write_text(_markdown(audit))
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect rigor-audit")
    parser.add_argument("--json", action="store_true", help="emit audit JSON")
    args = parser.parse_args(argv)
    audit = write_audit()
    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print(f"wrote {OUT_DOC}")
        print(f"passed={str(audit['passed']).lower()}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
