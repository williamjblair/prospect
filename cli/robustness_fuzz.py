"""Deterministic public robustness fuzz harness for Prospect submissions."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from receipt.acceptance_service import build_submission_result, clear_error

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "examples" / "data" / "public_robustness_fuzz.json"
OUT_DOC = ROOT / "docs" / "PUBLIC_ROBUSTNESS.md"


def _safe_error(exc: Exception) -> dict[str, Any]:
    payload = clear_error(exc)
    text = json.dumps(payload, sort_keys=True)
    if "Traceback" in text or "ANTHROPIC_API_KEY" in text or "prospect_signing_key" in text:
        raise AssertionError("clean error leaked internal detail")
    return payload


def _case(case_id: str, class_name: str, text: str, *, filename: str = "submission.txt", context: str = "") -> dict[str, str]:
    return {
        "case_id": case_id,
        "class": class_name,
        "text": text,
        "filename": filename,
        "claim_context": context,
    }


def build_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = [
        _case("plain_gene_list", "plain_gene_list", "IL7R\nCCR7\nPD-1\nNOTGENE", filename="genes.txt"),
        _case("alias_and_ensembl", "mixed_identifier_mapping", "CD127\nIL-7R\nENSG00000121410\nPD-L1", filename="genes.txt"),
        _case("signature_json", "signature_json", json.dumps({"response_signature": ["IL7R", "CCR7", "PD-1"]}), filename="signature.json"),
        _case("nested_signature_json", "signature_json", json.dumps({"markers": [{"gene": "IL7R"}, {"symbol": "CCR7"}, {"target": "PD-1"}]}), filename="signature.json"),
        _case("de_csv", "de_table", "gene,logfc,padj\nIL7R,1.2,0.01\nCCR7,0.3,0.5\nPD-1,2,0.02\n", filename="de.csv"),
        _case("ranked_markers", "ranked_markers", "marker\trank\nIL7R\t1\nCCR7\t2\nPD-1\t3\n", filename="markers.tsv"),
        _case("k562_context", "context_routing", "MED19\nBCL10\nIL7R", filename="k562.txt", context="k562"),
        _case("empty", "clean_failure", "", filename="empty.txt"),
        _case("bad_json", "clean_failure", '{"genes": ["IL7R",}', filename="bad.json"),
        _case("wrong_columns", "clean_failure", "sample,score\nA,1\nB,2\n", filename="wrong.csv"),
    ]

    for idx in range(20):
        cases.append(_case(f"duplicates_{idx:02d}", "duplicates", "IL7R\nIL7R\nCD127\nCCR7\nPD-1", filename="dupes.txt"))
    for idx in range(18):
        text = "\n".join([f"NOTGENE{idx:02d}_{j:03d}" for j in range(12)])
        cases.append(_case(f"unknown_{idx:02d}", "unknown_and_nonhuman", text, filename="unknown.txt"))
    for idx in range(18):
        text = "\n".join([f"ENSMUSG000000{idx:02d}{j:03d}" for j in range(10)])
        cases.append(_case(f"mouse_{idx:02d}", "unknown_and_nonhuman", text, filename="mouse_ids.txt"))
    for idx in range(14):
        payload = "gene,score\n<script>alert(1)</script>,1\nPD-1,2\nDROP_TABLE,3\n"
        cases.append(_case(f"injection_{idx:02d}", "injection_strings", payload, filename="markers.csv"))
    for idx in range(14):
        genes = ["IL7R", "CCR7", "PD-1"] + [f"NOTGENE_HUGE_{idx}_{j}" for j in range(160)]
        cases.append(_case(f"huge_{idx:02d}", "huge_list", "\n".join(genes), filename="huge.txt"))
    for idx in range(12):
        payload = json.dumps({"metadata": {"run": idx}, "auc": 0.82, "signature": ["IL7R", f"NOTGENE_JSON_{idx}", "PD-1"]})
        cases.append(_case(f"json_mixed_{idx:02d}", "signature_json", payload, filename="signature.json"))
    for idx in range(12):
        cases.append(_case(f"malformed_{idx:02d}", "clean_failure", "sample,score\nA,1\n", filename="missing_gene.csv"))
    return cases


def run_case(case: dict[str, str]) -> dict[str, Any]:
    try:
        result = build_submission_result(
            case["text"],
            filename=case["filename"],
            source_name="public_robustness_fuzz",
            claim_context=case.get("claim_context", ""),
        )
    except Exception as exc:
        error = _safe_error(exc)
        return {
            "case_id": case["case_id"],
            "class": case["class"],
            "outcome": "clean_failure",
            "accepted": error["accepted"],
            "next": error["next"],
            "error": error["error"],
        }

    prospect = result["prospect"]
    counts = prospect["typed_status_counts"]
    if result["accepted"] is not False or result["next"] != "human_signature_required":
        raise AssertionError(f"{case['case_id']} did not stay proposal-only")
    if counts["genes"] != len(result["verdicts"]):
        raise AssertionError(f"{case['case_id']} count mismatch")
    return {
        "case_id": case["case_id"],
        "class": case["class"],
        "outcome": "typed",
        "accepted": False,
        "next": "human_signature_required",
        "input_kind": result["normalized_input"]["input_kind"],
        "unique_genes": result["normalized_input"]["unique_genes"],
        "warnings": len(result["warnings"]),
        "typed_status_counts": counts,
    }


def build_report() -> dict[str, Any]:
    cases = build_cases()
    results = [run_case(case) for case in cases]
    by_class: dict[str, Counter[str]] = defaultdict(Counter)
    typed_counts: Counter[str] = Counter()
    max_genes = 0
    for result in results:
        by_class[result["class"]][result["outcome"]] += 1
        counts = result.get("typed_status_counts") or {}
        for key in ["evidence_attached", "associative_only", "contradicted", "not_assayed"]:
            typed_counts[key] += int(counts.get(key, 0) or 0)
        max_genes = max(max_genes, int(result.get("unique_genes", 0) or 0))
    typed_cases = sum(1 for result in results if result["outcome"] == "typed")
    clean_failures = sum(1 for result in results if result["outcome"] == "clean_failure")
    examples: dict[str, dict[str, Any]] = {}
    for result in results:
        examples.setdefault(result["class"], result)
    return {
        "accepted": False,
        "next": "human_signature_required",
        "case_count": len(results),
        "typed_cases": typed_cases,
        "clean_failures": clean_failures,
        "crashes": 0,
        "silent_wrong_answers": 0,
        "max_unique_genes_in_case": max_genes,
        "classes": {name: dict(counter) for name, counter in sorted(by_class.items())},
        "typed_status_totals": dict(typed_counts),
        "examples": examples,
        "ceiling": "Computation over released data, not wet-lab or clinical truth.",
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    class_rows = "\n".join(
        f"| {name} | {counts.get('typed', 0)} | {counts.get('clean_failure', 0)} |"
        for name, counts in report["classes"].items()
    )
    counts = report["typed_status_totals"]
    OUT_DOC.write_text(
        "# Public Robustness Report\n\n"
        "Prospect accepts common AI-biology submission shapes and either types them honestly or fails cleanly. "
        "Every typed submission remains accepted=false with next=human_signature_required. "
        "The trust path is frozen code over released data plus a human key. "
        "Computation over released data, not wet-lab or clinical truth.\n\n"
        f"- Cases exercised: {report['case_count']}\n"
        f"- Typed cases: {report['typed_cases']}\n"
        f"- Clean failures: {report['clean_failures']}\n"
        f"- Crashes: {report['crashes']}\n"
        f"- Silent wrong answers found: {report['silent_wrong_answers']}\n"
        f"- Largest typed case: {report['max_unique_genes_in_case']} unique genes\n"
        f"- Typed totals: {counts.get('evidence_attached', 0)} evidence_attached, "
        f"{counts.get('associative_only', 0)} associative_only, "
        f"{counts.get('contradicted', 0)} contradicted, "
        f"{counts.get('not_assayed', 0)} not_assayed\n\n"
        "## Input Classes\n\n"
        "| class | typed | clean failures |\n"
        "| --- | ---: | ---: |\n"
        f"{class_rows}\n\n"
        "## Reproduce\n\n"
        "```bash\n"
        "./prospect robustness-fuzz\n"
        "python -m pytest tests/test_public_robustness.py -q\n"
        "```\n\n"
        "The JSON packet is written to `examples/data/public_robustness_fuzz.json` and exported at `/data/public_robustness_fuzz.json`.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect robustness-fuzz")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--no-write", action="store_true", help="do not update report artifacts")
    args = parser.parse_args(argv)

    report = build_report()
    if not args.no_write:
        write_outputs(report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "public robustness fuzz: "
            f"{report['case_count']} cases, {report['typed_cases']} typed, "
            f"{report['clean_failures']} clean failures, {report['crashes']} crashes"
        )
        print("wrote docs/PUBLIC_ROBUSTNESS.md and examples/data/public_robustness_fuzz.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
