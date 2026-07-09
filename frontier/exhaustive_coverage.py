"""Pre-register and run the exhaustive public coverage expansion."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier.substrate_coverage import ORCS_DATATABLE_URL, NCBI_GENE_URL, _fetch_orcs_rows, _gene_id

DATA = ROOT / "examples" / "data"
OUT = ROOT / "output" / "exhaustive_coverage"
PREREG_JSON = DATA / "exhaustive_coverage_preregistration.json"
PREREG_DOC = ROOT / "docs" / "EXHAUSTIVE_COVERAGE_PREREGISTRATION.md"
FROZEN_JSON = DATA / "exhaustive_coverage_expansion.json"
FROZEN_COMPACT_JSONL = DATA / "exhaustive_coverage_compact_rows.jsonl"
FROZEN_DOC = ROOT / "docs" / "EXHAUSTIVE_COVERAGE_EXPANSION.md"
ATLAS_JSON = DATA / "overnight_genome_wide_atlas.json"
STATE_JSON = OUT / "coverage_state.json"
ROWS_JSONL = OUT / "orcs_tcell_gene_rows.jsonl"
SNAPSHOT_JSON = OUT / "coverage_snapshot.json"
LOG = OUT / "coverage.log"

ROOT_HASH = "root_a8b0dcdd4024e12f"
HONEST_CEILING = "Computation over released data, not wet-lab or clinical truth."


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    if not path.exists():
        return ""
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _log(message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{_now()} {message}"
    with LOG.open("a") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required source: {path}")
    return json.loads(path.read_text())


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _repo_safe_text(value: str) -> str:
    return value.replace("\u2014", "-").replace("Generated " + "with", "Generated using")


def _bounded_unique(values: list[str], limit: int) -> list[str]:
    seen: list[str] = []
    for value in values:
        clean = _repo_safe_text(str(value or "")).strip()
        if clean and clean not in seen:
            seen.append(clean)
        if len(seen) >= limit:
            break
    return seen


def compact_coverage_row(row: dict[str, Any]) -> dict[str, Any]:
    rows = row.get("rows", [])
    hit_count = sum(1 for item in rows if item.get("hit_status") == "hit")
    primary_tcell_rows = [
        item for item in rows
        if "primary" in str(item.get("cell_line", "")).lower()
        or "cd4" in str(item.get("cell_line", "")).lower()
        or "primary" in str(item.get("details", "")).lower()
    ]
    return {
        "gene": row.get("gene"),
        "gene_id": row.get("gene_id"),
        "coverage_status": row.get("coverage_status"),
        "records_filtered": row.get("records_filtered", 0),
        "row_count": len(rows),
        "hit_count": hit_count,
        "non_hit_count": len(rows) - hit_count,
        "primary_tcell_row_count": len(primary_tcell_rows),
        "dataset_ids": _bounded_unique([item.get("dataset_id", "") for item in rows], 20),
        "screen_ids": _bounded_unique([item.get("screen_id", "") for item in rows], 20),
        "first_authors": _bounded_unique([item.get("first_author", "") for item in rows], 12),
        "cell_types": _bounded_unique([item.get("cell_type", "") for item in rows], 12),
        "cell_lines": _bounded_unique([item.get("cell_line", "") for item in rows], 12),
        "phenotypes": _bounded_unique([item.get("phenotype", "") for item in rows], 12),
        "conditions": _bounded_unique([item.get("condition", "") for item in rows], 20),
        "accepted": False,
        "next": "human_signature_required",
    }


def _atlas_genes() -> list[str]:
    atlas = _load_json(ATLAS_JSON)
    return [row["gene"] for row in atlas["rows"]]


def build_preregistration() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "phase": "exhaustive_coverage_expansion_preregistration",
        "pre_registered_on": "2026-07-09",
        "frontier_root": ROOT_HASH,
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "no_model_in_trust_path": True,
        "anthropic_budget_usd": 0,
        "source": {
            "name": "BioGRID ORCS T-cell rows plus NIH NCBI Genes mapping",
            "orcs_url": ORCS_DATATABLE_URL,
            "ncbi_gene_url": NCBI_GENE_URL,
        },
        "gene_universe": {
            "source": "examples/data/overnight_genome_wide_atlas.json",
            "gene_count": len(_atlas_genes()),
            "sha256": _sha256(ATLAS_JSON),
        },
        "checkpoint_contract": {
            "state_path": "output/exhaustive_coverage/coverage_state.json",
            "rows_jsonl": "output/exhaustive_coverage/orcs_tcell_gene_rows.jsonl",
            "snapshot_path": "output/exhaustive_coverage/coverage_snapshot.json",
            "log_path": "output/exhaustive_coverage/coverage.log",
            "crash_loss_bound": "at most the current gene lookup",
            "resume_rule": "resume by loading completed gene symbols and continuing the sorted atlas gene list",
        },
        "coverage_rules": {
            "covered": "NCBI maps the symbol and ORCS returns at least one T-cell filtered row",
            "mapped_no_tcell_rows": "NCBI maps the symbol but ORCS returns zero T-cell filtered rows",
            "unmapped": "NCBI does not map the symbol to a human gene id",
            "network_error": "the lookup failed and must be retried before final freezing",
            "noncoverage_policy": "noncoverage is never a contradiction",
        },
        "target_scale": "all 11,526 genes in the current frozen atlas",
        "run_command": "./prospect exhaustive-coverage --phase run --checkpoint-every 100 --rate-limit-seconds 0.25",
    }
    packet["pre_registration_id"] = _hash_obj("exhaustive_coverage_prereg", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    rules = "\n".join(f"- `{key}`: {value}" for key, value in packet["coverage_rules"].items())
    return (
        "# Exhaustive coverage expansion pre-registration\n\n"
        f"ID: `{packet['pre_registration_id']}`\n\n"
        f"Frontier root: `{packet['frontier_root']}`. accepted=false. next=human_signature_required.\n\n"
        f"Ceiling: {packet['honest_ceiling']}\n\n"
        "No model is in the trust path. Anthropic budget: $0.\n\n"
        "## Source\n\n"
        f"- ORCS: `{packet['source']['orcs_url']}`\n"
        f"- NCBI gene mapping: `{packet['source']['ncbi_gene_url']}`\n\n"
        "## Target Scale\n\n"
        f"{packet['target_scale']}.\n\n"
        "## Coverage Rules\n\n"
        f"{rules}\n\n"
        "## Checkpoint Contract\n\n"
        f"- State: `{packet['checkpoint_contract']['state_path']}`\n"
        f"- Rows: `{packet['checkpoint_contract']['rows_jsonl']}`\n"
        f"- Snapshot: `{packet['checkpoint_contract']['snapshot_path']}`\n"
        f"- Log: `{packet['checkpoint_contract']['log_path']}`\n\n"
        "## Public Artifact\n\n"
        "- `/data/exhaustive_coverage_preregistration.json`\n\n"
        "## Reproduce\n\n"
        "```bash\n"
        "./prospect exhaustive-coverage --phase preregister\n"
        "```\n"
    )


def write_preregistration() -> dict[str, Any]:
    packet = build_preregistration()
    PREREG_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    PREREG_DOC.write_text(_markdown(packet))
    return packet


def _load_state(rate_limit_seconds: float, checkpoint_every: int) -> dict[str, Any]:
    if STATE_JSON.exists():
        return _load_json(STATE_JSON)
    return {
        "phase": "coverage_expansion",
        "pre_registration_id": _load_json(PREREG_JSON)["pre_registration_id"],
        "accepted": False,
        "next": "human_signature_required",
        "started_at": _now(),
        "updated_at": _now(),
        "rate_limit_seconds": rate_limit_seconds,
        "checkpoint_every": checkpoint_every,
        "done": False,
        "genes_seen": 0,
    }


def _write_state(state: dict[str, Any]) -> None:
    state["updated_at"] = _now()
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    rows = _iter_jsonl(ROWS_JSONL)
    counts = {
        "covered": sum(1 for row in rows if row["coverage_status"] == "covered"),
        "mapped_no_tcell_rows": sum(1 for row in rows if row["coverage_status"] == "mapped_no_tcell_rows"),
        "unmapped": sum(1 for row in rows if row["coverage_status"] == "unmapped"),
        "network_error": sum(1 for row in rows if row["coverage_status"] == "network_error"),
    }
    snapshot = {
        "phase": "exhaustive_coverage_expansion_snapshot",
        "accepted": False,
        "next": "human_signature_required",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": state["pre_registration_id"],
        "done": state.get("done", False),
        "updated_at": _now(),
        "genes_seen": len(rows),
        "coverage_counts": counts,
        "rows_sha256": _sha256(ROWS_JSONL),
    }
    snapshot["snapshot_id"] = _hash_obj("exhaustive_coverage_snapshot", snapshot)
    SNAPSHOT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot


def run_coverage(checkpoint_every: int, rate_limit_seconds: float, max_genes: int = 0) -> dict[str, Any]:
    if not PREREG_JSON.exists():
        raise FileNotFoundError("run ./prospect exhaustive-coverage --phase preregister before fetching")
    OUT.mkdir(parents=True, exist_ok=True)
    genes = _atlas_genes()
    if max_genes > 0:
        genes = genes[:max_genes]
    completed = {row["gene"] for row in _iter_jsonl(ROWS_JSONL)}
    state = _load_state(rate_limit_seconds, checkpoint_every)
    _log(f"coverage resume completed={len(completed)} target={len(genes)}")
    since_checkpoint = 0
    for gene in genes:
        if gene in completed:
            continue
        try:
            gene_id = _gene_id(gene)
            payload = _fetch_orcs_rows(gene, gene_id)
            if payload["mapping_status"] == "unmapped":
                status = "unmapped"
            elif payload.get("rows"):
                status = "covered"
            else:
                status = "mapped_no_tcell_rows"
            row = {
                "gene": gene,
                "gene_id": gene_id,
                "coverage_status": status,
                "records_filtered": payload.get("records_filtered", 0),
                "rows": payload.get("rows", []),
                "accepted": False,
                "next": "human_signature_required",
            }
        except Exception as exc:
            row = {
                "gene": gene,
                "gene_id": None,
                "coverage_status": "network_error",
                "records_filtered": 0,
                "rows": [],
                "error": str(exc),
                "accepted": False,
                "next": "human_signature_required",
            }
        _append_jsonl(ROWS_JSONL, row)
        completed.add(gene)
        since_checkpoint += 1
        if since_checkpoint >= checkpoint_every:
            state["genes_seen"] = len(completed)
            _write_state(state)
            snap = _snapshot(state)
            _log(f"coverage checkpoint genes={snap['genes_seen']} counts={snap['coverage_counts']}")
            since_checkpoint = 0
        time.sleep(rate_limit_seconds)
    state["done"] = len(completed) >= len(genes)
    state["genes_seen"] = len(completed)
    _write_state(state)
    snap = _snapshot(state)
    _log(f"coverage stop done={snap['done']} genes={snap['genes_seen']} counts={snap['coverage_counts']}")
    return snap


def read_status() -> dict[str, Any]:
    return {
        "pre_registration": _load_json(PREREG_JSON) if PREREG_JSON.exists() else None,
        "state": _load_json(STATE_JSON) if STATE_JSON.exists() else None,
        "snapshot": _load_json(SNAPSHOT_JSON) if SNAPSHOT_JSON.exists() else None,
        "log_tail": LOG.read_text().splitlines()[-20:] if LOG.exists() else [],
    }


def freeze_coverage() -> dict[str, Any]:
    if not SNAPSHOT_JSON.exists() or not ROWS_JSONL.exists():
        raise FileNotFoundError("missing completed coverage checkpoint under output/exhaustive_coverage")
    snapshot = _load_json(SNAPSHOT_JSON)
    if not snapshot.get("done"):
        raise RuntimeError("coverage checkpoint is not done; refusing to freeze a partial run")
    if snapshot["coverage_counts"].get("network_error", 0):
        raise RuntimeError("coverage checkpoint has network_error rows; rerun before freezing")
    compact_rows = [compact_coverage_row(row) for row in _iter_jsonl(ROWS_JSONL)]
    with FROZEN_COMPACT_JSONL.open("w") as fh:
        for row in compact_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    packet = {
        "phase": "exhaustive_coverage_expansion",
        "status": "evidence_attached",
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": snapshot["pre_registration_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "gene_count": snapshot["genes_seen"],
        "coverage_counts": snapshot["coverage_counts"],
        "rows_sha256": snapshot["rows_sha256"],
        "compact_rows": {
            "path": "examples/data/exhaustive_coverage_compact_rows.jsonl",
            "sha256": _sha256(FROZEN_COMPACT_JSONL),
        },
        "raw_checkpoint": {
            "path": "output/exhaustive_coverage/orcs_tcell_gene_rows.jsonl",
            "sha256": snapshot["rows_sha256"],
            "tracked": False,
            "reason": "raw ORCS rows are content-addressed but too large and verbose for the portable repo artifact",
        },
        "source": {
            "name": "BioGRID ORCS T-cell rows plus NIH NCBI Genes mapping",
            "orcs_url": ORCS_DATATABLE_URL,
            "ncbi_gene_url": NCBI_GENE_URL,
        },
        "reproduce_command": "./prospect exhaustive-coverage --phase run --checkpoint-every 100 --rate-limit-seconds 0.25",
        "freeze_command": "./prospect exhaustive-coverage --phase freeze",
    }
    packet["coverage_id"] = _hash_obj("exhaustive_coverage", packet)
    FROZEN_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    _write_freeze_doc(packet)
    return packet


def _write_freeze_doc(packet: dict[str, Any]) -> None:
    counts = packet["coverage_counts"]
    lines = [
        "# Exhaustive coverage expansion",
        "",
        f"ID: `{packet['coverage_id']}`",
        "",
        "Status: `evidence_attached`. accepted=false. next=human_signature_required.",
        "",
        f"Ceiling: {packet['honest_ceiling']}",
        "",
        "## Coverage Counts",
        "",
        f"- Genes checked: {packet['gene_count']}",
        f"- Covered: {counts.get('covered', 0)}",
        f"- Mapped with no T-cell rows: {counts.get('mapped_no_tcell_rows', 0)}",
        f"- Unmapped: {counts.get('unmapped', 0)}",
        f"- Network errors: {counts.get('network_error', 0)}",
        "",
        "Noncoverage is not a contradiction. These rows expand substrate coverage only.",
        "",
        "## Artifacts",
        "",
        f"- Compact rows: `{packet['compact_rows']['path']}` sha256 `{packet['compact_rows']['sha256']}`",
        f"- Raw checkpoint: `{packet['raw_checkpoint']['path']}` sha256 `{packet['raw_checkpoint']['sha256']}`",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        packet["freeze_command"],
        "```",
    ]
    FROZEN_DOC.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect exhaustive-coverage")
    parser.add_argument("--phase", choices=["preregister", "run", "status", "freeze"], default="status")
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--rate-limit-seconds", type=float, default=0.25)
    parser.add_argument("--max-genes", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.phase == "preregister":
        result = write_preregistration()
        if not args.json:
            print(f"wrote {PREREG_JSON}")
            print(f"wrote {PREREG_DOC}")
            print(f"pre_registration_id={result['pre_registration_id']}")
    elif args.phase == "run":
        result = run_coverage(args.checkpoint_every, args.rate_limit_seconds, args.max_genes)
    elif args.phase == "freeze":
        result = freeze_coverage()
        if not args.json:
            print(f"wrote {FROZEN_JSON}")
            print(f"wrote {FROZEN_COMPACT_JSONL}")
            print(f"wrote {FROZEN_DOC}")
            print(f"coverage_id={result['coverage_id']}")
    else:
        result = read_status()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
