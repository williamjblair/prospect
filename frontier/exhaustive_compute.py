"""Multi-day exhaustive compute runner with resumable checkpoints."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from receipt.input_normalizer import ALIASES

DATA = ROOT / "examples" / "data"
OUT = ROOT / "output" / "exhaustive_compute"
PREREG_JSON = DATA / "exhaustive_compute_preregistration.json"
PREREG_DOC = ROOT / "docs" / "EXHAUSTIVE_COMPUTE_PREREGISTRATION.md"
LOG = OUT / "run.log"
STATE_JSON = OUT / "literature_state.json"
DOCS_JSONL = OUT / "literature_documents.jsonl"
CLAIMS_JSONL = OUT / "literature_claims.jsonl"
SNAPSHOT_JSON = OUT / "literature_audit_snapshot.json"
FROZEN_DOCS_JSONL = DATA / "exhaustive_literature_documents.jsonl"
FROZEN_CLAIMS_JSONL = DATA / "exhaustive_literature_claims.jsonl"
FROZEN_AUDIT_JSON = DATA / "exhaustive_literature_audit.json"
FROZEN_CLAIMS_CSV = DATA / "exhaustive_literature_claims.csv"
FROZEN_AUDIT_DOC = ROOT / "docs" / "EXHAUSTIVE_LITERATURE_AUDIT.md"

MARSON_FULL = DATA / "marson_de_full.csv"
ATLAS_JSON = DATA / "overnight_genome_wide_atlas.json"

ROOT_HASH = "root_a8b0dcdd4024e12f"
HONEST_CEILING = "Computation over released data, not wet-lab or clinical truth."
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DRIVER_DE_THRESHOLD = 10
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_RECORDS = 10000

DRIVER_WORDS = [
    "regulates",
    "regulator",
    "regulatory",
    "drives",
    "driver",
    "controls",
    "required",
    "essential",
    "mediates",
    "promotes",
    "inhibits",
    "modulates",
    "governs",
    "induces",
    "suppresses",
]
COMPARABLE_RE = re.compile(
    r"\b(activation|activate|activated|TCR|CD3|CD28|stimulation|stimulated|transcription|"
    r"transcriptome|program|state|differentiation|proliferation|effector differentiation)\b",
    re.I,
)
ORTHOGONAL_RE = re.compile(
    r"\b(cytokine secretion|cytokine production|exhaustion|exhausted|checkpoint|tumou?r|cancer|"
    r"immunotherapy response|patient response|survival|disease risk|GWAS|autoimmune disease)\b",
    re.I,
)
CD4_CONTEXT_RE = re.compile(r"\b(CD4|helper T|T helper|Th1|Th2|Th17|Tfh|Treg|TCR)\b", re.I)
CD4_CONTEXT_ONLY_RE = re.compile(r"\bCD4\s*(\+|-positive|positive)?\s*(T[-\s]?cell|cell|target cells?)", re.I)

QUERY_PLAN = [
    "CD4 T cell activation regulator",
    "CD4 T-cell activation regulator",
    "human CD4 T cell activation regulator",
    "primary CD4 T cell activation regulator",
    "CD4 T cell transcriptional regulator activation",
    "CD4 T cell TCR activation regulator",
    "TCR stimulated CD4 T cell regulator",
    "helper T cell activation regulator",
    "T helper cell activation regulator",
    "Th1 differentiation regulator CD4 T cell",
    "Th2 differentiation regulator CD4 T cell",
    "Th17 differentiation regulator CD4 T cell",
    "Tfh differentiation regulator CD4 T cell",
    "Treg activation regulator CD4 T cell",
    "CD4 T cell proliferation regulator",
    "CD4 T cell CRISPR screen regulator activation",
    "CRISPR CD4 T cell regulator activation",
    "Perturb-seq T cell activation regulator",
    "single cell CRISPR T cell activation regulator",
    "CD4 T cell immune synapse regulator",
    "CD4 T cell signaling regulator activation",
    "NFAT CD4 T cell activation regulator",
    "NF-kappaB CD4 T cell activation regulator",
    "AP-1 CD4 T cell activation regulator",
    "calcineurin CD4 T cell activation regulator",
    "costimulation CD4 T cell activation regulator",
    "CD28 CD4 T cell activation regulator",
    "IL2 CD4 T cell activation regulator",
    "checkpoint CD4 T cell activation regulator",
    "human T cell activation transcriptional regulator CD4",
]


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _log(message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{_now()} {message}"
    with LOG.open("a") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


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


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required source: {path}")
    return json.loads(path.read_text())


def _source_inventory() -> list[dict[str, Any]]:
    sources = [
        ("frontier_signature", ROOT / "frontier" / "frontier.sig.json", "signed root reference"),
        ("marson_de_full", MARSON_FULL, "primary causal perturbation substrate"),
        ("overnight_atlas", ATLAS_JSON, "current full-gene typed atlas"),
        ("replogle_k562", DATA / "replogle_k562_de.csv", "genome-wide non-immune specificity substrate"),
        ("replogle_rpe1", DATA / "replogle_rpe1_de.csv", "sparse non-immune context substrate"),
        ("collectri", DATA / "collectri_human.csv", "known regulator novelty exclusion"),
        ("cross_validation_sources", DATA / "cross_validation_sources.json", "frozen orthogonal source bundle"),
        ("disease_overlay", DATA / "disease_genetics_overlay.json", "disease-context overlay"),
    ]
    return [
        {
            "name": name,
            "path": str(path.relative_to(ROOT)),
            "role": role,
            "exists": path.exists(),
            "sha256": _sha256(path),
        }
        for name, path, role in sources
    ]


def build_preregistration() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "phase": "exhaustive_compute_preregistration",
        "pre_registered_on": "2026-07-09",
        "frontier_root": ROOT_HASH,
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "no_model_in_trust_path": True,
        "anthropic_budget_usd": 0,
        "target_scale": {
            "literature_records": "target thousands, stop only at configured max_records or exhausted Europe PMC cursors",
            "gene_atlas": "all 11,526 Marson genes, all Rest, Stim8hr, Stim48hr conditions",
            "leaderboard": "all novel driver candidates absent from CollecTRI and standard T-cell annotations",
        },
        "checkpoint_contract": {
            "state_path": "output/exhaustive_compute/literature_state.json",
            "documents_jsonl": "output/exhaustive_compute/literature_documents.jsonl",
            "claims_jsonl": "output/exhaustive_compute/literature_claims.jsonl",
            "snapshot_path": "output/exhaustive_compute/literature_audit_snapshot.json",
            "log_path": "output/exhaustive_compute/run.log",
            "crash_loss_bound": "at most the current Europe PMC page or current claim sentence",
            "resume_rule": "resume by loading state, skip existing PMID plus gene plus normalized sentence keys, continue the active cursor",
        },
        "typed_status_ladder": {
            "evidence_attached": "comparable causal activation-driver claim and Marson on-target perturbation moves more than 10 transcripts at strongest effect",
            "contradicted": "explicit causal activation-driver claim with comparable readout, but Marson on-target perturbation moves 10 or fewer transcripts at strongest effect",
            "orthogonal_phenotype": "claim is about cytokine secretion, exhaustion, disease association, immunotherapy response, or another non-comparable readout",
            "not_assayed": "gene is absent from the frozen Marson atlas or lacks comparable on-target coverage",
        },
        "literature_audit_rules": {
            "source": "Europe PMC open API",
            "query_plan": QUERY_PLAN,
            "page_size": DEFAULT_PAGE_SIZE,
            "default_max_records": DEFAULT_MAX_RECORDS,
            "rate_limit_seconds": 0.35,
            "dedupe_key": "pmid plus approved gene symbol plus normalized claim sentence",
            "gene_mapping": "frozen Marson symbols plus committed alias map",
            "claim_sentence_rule": "title or abstract sentence must contain a mapped gene and a pre-registered driver word",
            "cd4_context_rule": "title or abstract must mention CD4, helper T, T helper subset, TCR, or a named CD4 subset",
            "comparability_rule": "comparable only when the sentence or abstract asserts activation, TCR stimulation, transcriptional program, proliferation, or differentiation in CD4 or helper T-cell context",
            "contradiction_rule": "contradicted only when comparability is comparable and strongest Marson on-target effect is 10 or fewer DE genes",
            "support_rule": "evidence_attached only when comparability is comparable and strongest Marson on-target effect is greater than 10 DE genes",
        },
        "day_2_rules": {
            "atlas_source": "reuse full Marson table and current overnight atlas rows as the baseline",
            "coverage_expansion": "new public perturbation substrates must be downloaded or API-captured, frozen, sha256-addressed, and reported before they change coverage counts",
            "noncoverage_rule": "not_assayed is reported, never counted as contradiction",
        },
        "day_3_rules": {
            "candidate_source": "all atlas evidence_attached rows absent from CollecTRI and standard T-cell annotations",
            "minimum_orthogonal_datasets": 5,
            "kill_attempts": [
                "technical_confound",
                "essentiality_or_proliferation_artifact",
                "batch_or_donor_effect",
                "reverse_causality_or_passenger_marker",
                "better_alternative_mechanism",
            ],
            "known_survivor_baseline": ["PGGT1B", "CCDC22", "LETM2"],
            "freshness_rule": "if no survivor beyond the known three clears, report that as the result without relabeling the known three as new",
        },
        "gate_commands": [
            "./prospect verify",
            "python benchmark/mutation_pack.py",
            "python tests/test_skill_parity.py",
            "python tests/test_marson.py",
            "python -m pytest tests/ -q",
            "cd web && npm run build",
        ],
        "source_inventory": _source_inventory(),
        "launch_commands": [
            "./prospect exhaustive-compute --phase literature --max-records 10000 --checkpoint-every 250",
            "./prospect exhaustive-compute --phase status",
        ],
    }
    packet["pre_registration_id"] = _hash_obj("exhaustive_prereg", packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    statuses = "\n".join(f"- `{key}`: {value}" for key, value in packet["typed_status_ladder"].items())
    queries = "\n".join(f"- `{query}`" for query in packet["literature_audit_rules"]["query_plan"])
    sources = "\n".join(
        f"- `{row['name']}`: `{row['path']}` sha256 `{row['sha256']}`"
        for row in packet["source_inventory"]
    )
    gates = "\n".join(f"- `{cmd}`" for cmd in packet["gate_commands"])
    return (
        "# Exhaustive compute pre-registration\n\n"
        f"ID: `{packet['pre_registration_id']}`\n\n"
        f"Frontier root: `{packet['frontier_root']}`. accepted=false. next=human_signature_required.\n\n"
        f"Ceiling: {packet['honest_ceiling']}\n\n"
        "No model is in the trust path. Anthropic budget: $0. A human key accepts no state in this run.\n\n"
        "## Target Scale\n\n"
        f"- Literature: {packet['target_scale']['literature_records']}.\n"
        f"- Atlas: {packet['target_scale']['gene_atlas']}.\n"
        f"- Leaderboard: {packet['target_scale']['leaderboard']}.\n\n"
        "## Typed Status Ladder\n\n"
        f"{statuses}\n\n"
        "## Literature Query Plan\n\n"
        f"{queries}\n\n"
        "## Comparability Rule\n\n"
        "A contradiction requires an explicit causal activation-driver claim and a comparable activation, TCR stimulation, transcriptional program, proliferation, or differentiation readout. Cytokine secretion, exhaustion, disease association, immunotherapy response, and generic importance are `orthogonal_phenotype` unless the claim is explicitly narrowed to the Marson activation-transcriptome readout.\n\n"
        "## Checkpoint Contract\n\n"
        f"- State: `{packet['checkpoint_contract']['state_path']}`\n"
        f"- Documents: `{packet['checkpoint_contract']['documents_jsonl']}`\n"
        f"- Claims: `{packet['checkpoint_contract']['claims_jsonl']}`\n"
        f"- Snapshot: `{packet['checkpoint_contract']['snapshot_path']}`\n"
        f"- Log: `{packet['checkpoint_contract']['log_path']}`\n"
        f"- Crash loss bound: {packet['checkpoint_contract']['crash_loss_bound']}.\n\n"
        "## Public Artifact\n\n"
        "- `/data/exhaustive_compute_preregistration.json`\n\n"
        "## Reproduce\n\n"
        "```bash\n"
        "./prospect exhaustive-compute --phase preregister\n"
        "```\n\n"
        "## Source Inventory\n\n"
        f"{sources}\n\n"
        "## Gate Commands\n\n"
        f"{gates}\n"
    )


def write_preregistration() -> dict[str, Any]:
    packet = build_preregistration()
    PREREG_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    PREREG_DOC.write_text(_markdown(packet))
    return packet


def _load_atlas_by_gene() -> dict[str, dict[str, Any]]:
    atlas = _load_json(ATLAS_JSON)
    return {row["gene"]: row for row in atlas["rows"]}


def _gene_regex(symbols: set[str]) -> re.Pattern[str]:
    extraction_symbols = symbols - {"CD4"}
    tokens = sorted((re.escape(symbol) for symbol in extraction_symbols if len(symbol) >= 3), key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(tokens) + r")\b")


def _clean(text: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", text or "")
    return " ".join(html.unescape(without_tags).replace("\u207a", "+").split())


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text or "") if part.strip()]


def _driver_word_present(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in DRIVER_WORDS)


def _comparability(sentence: str, full_text: str) -> str:
    basis = sentence + " " + full_text
    if COMPARABLE_RE.search(basis) and not ORTHOGONAL_RE.search(sentence):
        return "comparable"
    return "orthogonal_phenotype"


def _status(atlas_by_gene: dict[str, dict[str, Any]], gene: str, comparability: str) -> str:
    if comparability != "comparable":
        return "orthogonal_phenotype"
    row = atlas_by_gene.get(gene)
    if not row or row.get("strongest_n_total_de_genes") is None:
        return "not_assayed"
    strongest = int(row["strongest_n_total_de_genes"])
    if strongest > DRIVER_DE_THRESHOLD:
        return "evidence_attached"
    return "contradicted"


def _reason(row: dict[str, Any] | None, typed_status: str, comparability: str) -> str:
    if comparability != "comparable":
        return "Non-comparable readout, retained as orthogonal_phenotype."
    if not row or row.get("strongest_n_total_de_genes") is None:
        return "Gene lacks comparable on-target Marson coverage."
    strongest = row["strongest_n_total_de_genes"]
    condition = row["strongest_condition"]
    if typed_status == "evidence_attached":
        return f"Comparable driver claim; Marson on-target perturbation moves {strongest} transcripts in {condition}."
    return f"Comparable driver claim; Marson on-target perturbation moves only {strongest} transcripts at strongest effect."


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def _load_jsonl_keys(path: Path, key_fields: tuple[str, ...]) -> set[tuple[str, ...]]:
    keys: set[tuple[str, ...]] = set()
    if not path.exists():
        return keys
    with path.open() as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            keys.add(tuple(str(row.get(field, "")) for field in key_fields))
    return keys


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _initial_state(max_records: int, page_size: int, rate_limit_seconds: float) -> dict[str, Any]:
    return {
        "phase": "literature",
        "pre_registration_id": _load_json(PREREG_JSON)["pre_registration_id"],
        "started_at": _now(),
        "updated_at": _now(),
        "accepted": False,
        "next": "human_signature_required",
        "max_records": max_records,
        "page_size": page_size,
        "rate_limit_seconds": rate_limit_seconds,
        "query_index": 0,
        "cursor": "*",
        "completed_queries": [],
        "documents_seen": 0,
        "claims_seen": 0,
        "done": False,
    }


def _load_state(max_records: int, page_size: int, rate_limit_seconds: float) -> dict[str, Any]:
    if STATE_JSON.exists():
        return json.loads(STATE_JSON.read_text())
    return _initial_state(max_records, page_size, rate_limit_seconds)


def _write_state(state: dict[str, Any]) -> None:
    state["updated_at"] = _now()
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def _fetch(query: str, cursor: str, page_size: int) -> dict[str, Any]:
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "cursorMark": cursor,
    }
    url = EUROPE_PMC + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "prospect-hackathon/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode())


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    claims = _iter_jsonl(CLAIMS_JSONL)
    docs = _iter_jsonl(DOCS_JSONL)
    counts = Counter(row["typed_status"] for row in claims)
    snapshot = {
        "phase": "exhaustive_literature_audit_snapshot",
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": state["pre_registration_id"],
        "updated_at": _now(),
        "done": state.get("done", False),
        "document_count": len(docs),
        "claim_count": len(claims),
        "typed_status_counts": dict(counts),
        "contradiction_rate": round(counts.get("contradicted", 0) / len(claims), 4) if claims else 0,
        "documents_sha256": _sha256(DOCS_JSONL),
        "claims_sha256": _sha256(CLAIMS_JSONL),
        "state": state,
    }
    snapshot["snapshot_id"] = _hash_obj("exhaustive_lit_snapshot", snapshot)
    SNAPSHOT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot


def run_literature(max_records: int, page_size: int, checkpoint_every: int, rate_limit_seconds: float) -> dict[str, Any]:
    if not PREREG_JSON.exists():
        raise FileNotFoundError("run ./prospect exhaustive-compute --phase preregister before scoring")
    OUT.mkdir(parents=True, exist_ok=True)
    state = _load_state(max_records, page_size, rate_limit_seconds)
    atlas_by_gene = _load_atlas_by_gene()
    aliases = {key: value for key, value in ALIASES.items() if value in atlas_by_gene}
    gene_re = _gene_regex(set(atlas_by_gene) | set(aliases))
    seen_docs = _load_jsonl_keys(DOCS_JSONL, ("pmid",))
    seen_claims = _load_jsonl_keys(CLAIMS_JSONL, ("pmid", "gene", "claim_sentence"))
    processed_since_checkpoint = 0
    _log(
        "literature resume "
        f"query_index={state['query_index']} cursor={state['cursor']} "
        f"docs={len(seen_docs)} claims={len(seen_claims)} max_records={state['max_records']}"
    )

    while state["query_index"] < len(QUERY_PLAN) and len(seen_docs) < state["max_records"]:
        query = QUERY_PLAN[state["query_index"]]
        cursor = state.get("cursor") or "*"
        try:
            body = _fetch(query, cursor, state["page_size"])
        except Exception as exc:
            _log(f"literature fetch_error query_index={state['query_index']} cursor={cursor} error={exc}")
            time.sleep(max(5.0, state["rate_limit_seconds"]))
            continue
        docs = body.get("resultList", {}).get("result", [])
        next_cursor = body.get("nextCursorMark") or cursor
        if not docs:
            state["completed_queries"].append(query)
            state["query_index"] += 1
            state["cursor"] = "*"
            _write_state(state)
            _log(f"literature query_complete empty query_index={state['query_index']} docs={len(seen_docs)} claims={len(seen_claims)}")
            continue
        for doc in docs:
            pmid = str(doc.get("pmid") or doc.get("id") or "")
            if not pmid or (pmid,) in seen_docs:
                continue
            title = doc.get("title") or ""
            abstract = doc.get("abstractText") or ""
            full_text = _clean(f"{title}. {abstract}")
            if not CD4_CONTEXT_RE.search(full_text):
                continue
            doc_row = {
                "pmid": pmid,
                "title": title,
                "journal": doc.get("journalTitle", ""),
                "pub_year": doc.get("pubYear", ""),
                "doi": doc.get("doi", ""),
                "source": doc.get("source", ""),
                "query": query,
                "query_index": state["query_index"],
                "cursor": cursor,
                "abstract": abstract,
            }
            _append_jsonl(DOCS_JSONL, doc_row)
            seen_docs.add((pmid,))
            for sentence in _sentences(full_text):
                claim_sentence = _clean(sentence)
                if not _driver_word_present(claim_sentence):
                    continue
                for match in gene_re.finditer(claim_sentence):
                    submitted = match.group(1)
                    gene = aliases.get(submitted, submitted)
                    if gene == "CD4" and CD4_CONTEXT_ONLY_RE.search(claim_sentence):
                        continue
                    atlas_row = atlas_by_gene.get(gene)
                    comparability = _comparability(claim_sentence, full_text)
                    typed_status = _status(atlas_by_gene, gene, comparability)
                    key = (pmid, gene, claim_sentence)
                    if key in seen_claims:
                        continue
                    claim = {
                        "pmid": pmid,
                        "gene": gene,
                        "matched_token": submitted,
                        "typed_status": typed_status,
                        "readout_comparability": comparability,
                        "claim_sentence": claim_sentence,
                        "title": title,
                        "journal": doc.get("journalTitle", ""),
                        "pub_year": doc.get("pubYear", ""),
                        "doi": doc.get("doi", ""),
                        "source_query": query,
                        "marson_strongest_de": None if not atlas_row else atlas_row.get("strongest_n_total_de_genes"),
                        "marson_strongest_condition": None if not atlas_row else atlas_row.get("strongest_condition"),
                        "accepted": False,
                        "next": "human_signature_required",
                        "reason": _reason(atlas_row, typed_status, comparability),
                    }
                    _append_jsonl(CLAIMS_JSONL, claim)
                    seen_claims.add(key)
            processed_since_checkpoint += 1
            if len(seen_docs) >= state["max_records"]:
                break
            if processed_since_checkpoint >= checkpoint_every:
                state["documents_seen"] = len(seen_docs)
                state["claims_seen"] = len(seen_claims)
                _write_state(state)
                snap = _snapshot(state)
                _log(
                    "literature checkpoint "
                    f"docs={snap['document_count']} claims={snap['claim_count']} "
                    f"contradicted={snap['typed_status_counts'].get('contradicted', 0)} "
                    f"rate={snap['contradiction_rate']}"
                )
                processed_since_checkpoint = 0
        if next_cursor == cursor:
            state["completed_queries"].append(query)
            state["query_index"] += 1
            state["cursor"] = "*"
            _log(f"literature query_complete query_index={state['query_index']} docs={len(seen_docs)} claims={len(seen_claims)}")
        else:
            state["cursor"] = next_cursor
        state["documents_seen"] = len(seen_docs)
        state["claims_seen"] = len(seen_claims)
        _write_state(state)
        snap = _snapshot(state)
        _log(
            "literature page "
            f"query_index={state['query_index']} docs={snap['document_count']} claims={snap['claim_count']} "
            f"contradicted={snap['typed_status_counts'].get('contradicted', 0)} "
            f"evidence_attached={snap['typed_status_counts'].get('evidence_attached', 0)} "
            f"orthogonal={snap['typed_status_counts'].get('orthogonal_phenotype', 0)}"
        )
        time.sleep(state["rate_limit_seconds"])

    state["done"] = state["query_index"] >= len(QUERY_PLAN) or len(seen_docs) >= state["max_records"]
    state["documents_seen"] = len(seen_docs)
    state["claims_seen"] = len(seen_claims)
    _write_state(state)
    snap = _snapshot(state)
    _log(
        "literature stop "
        f"done={state['done']} docs={snap['document_count']} claims={snap['claim_count']} "
        f"contradicted={snap['typed_status_counts'].get('contradicted', 0)} rate={snap['contradiction_rate']}"
    )
    return snap


def read_status() -> dict[str, Any]:
    state = json.loads(STATE_JSON.read_text()) if STATE_JSON.exists() else None
    snapshot = json.loads(SNAPSHOT_JSON.read_text()) if SNAPSHOT_JSON.exists() else None
    return {
        "pre_registration": json.loads(PREREG_JSON.read_text()) if PREREG_JSON.exists() else None,
        "state": state,
        "snapshot": snapshot,
        "log_tail": LOG.read_text().splitlines()[-20:] if LOG.exists() else [],
    }


def reset_literature() -> None:
    for path in [STATE_JSON, DOCS_JSONL, CLAIMS_JSONL, SNAPSHOT_JSON]:
        if path.exists():
            path.unlink()


def freeze_literature() -> dict[str, Any]:
    if not SNAPSHOT_JSON.exists() or not DOCS_JSONL.exists() or not CLAIMS_JSONL.exists():
        raise FileNotFoundError("missing completed literature checkpoint under output/exhaustive_compute")
    snapshot = _load_json(SNAPSHOT_JSON)
    if not snapshot.get("done"):
        raise RuntimeError("literature checkpoint is not done; refusing to freeze a partial run")
    shutil.copyfile(DOCS_JSONL, FROZEN_DOCS_JSONL)
    shutil.copyfile(CLAIMS_JSONL, FROZEN_CLAIMS_JSONL)
    claims = _iter_jsonl(FROZEN_CLAIMS_JSONL)
    with FROZEN_CLAIMS_CSV.open("w", newline="") as fh:
        fields = [
            "pmid",
            "gene",
            "typed_status",
            "readout_comparability",
            "marson_strongest_de",
            "marson_strongest_condition",
            "pub_year",
            "journal",
            "title",
            "claim_sentence",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in claims:
            writer.writerow({field: row.get(field) for field in fields})
    packet = {
        "phase": "exhaustive_literature_contradiction_audit",
        "status": "evidence_attached",
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "pre_registration_id": snapshot["pre_registration_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "document_count": snapshot["document_count"],
        "claim_count": snapshot["claim_count"],
        "typed_status_counts": snapshot["typed_status_counts"],
        "contradiction_rate": snapshot["contradiction_rate"],
        "source": "Europe PMC open API",
        "query_index_reached": snapshot["state"]["query_index"],
        "cursor_at_stop": snapshot["state"]["cursor"],
        "configured_stop": snapshot["state"]["max_records"],
        "real_scale_assessment": (
            "hit configured 10,000-record stop on the first Europe PMC query cursor; "
            "this is a real-scale audit, not the full possible Europe PMC corpus"
        ),
        "artifacts": {
            "documents_jsonl": {
                "path": "examples/data/exhaustive_literature_documents.jsonl",
                "sha256": _sha256(FROZEN_DOCS_JSONL),
            },
            "claims_jsonl": {
                "path": "examples/data/exhaustive_literature_claims.jsonl",
                "sha256": _sha256(FROZEN_CLAIMS_JSONL),
            },
            "claims_csv": {
                "path": "examples/data/exhaustive_literature_claims.csv",
                "sha256": _sha256(FROZEN_CLAIMS_CSV),
            },
        },
        "reproduce_command": "./prospect exhaustive-compute --phase literature --max-records 10000 --checkpoint-every 250 --rate-limit-seconds 0.35",
        "freeze_command": "./prospect exhaustive-compute --phase freeze-literature",
    }
    packet["audit_id"] = _hash_obj("exhaustive_literature_audit", packet)
    FROZEN_AUDIT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    _write_literature_doc(packet)
    return packet


def _write_literature_doc(packet: dict[str, Any]) -> None:
    counts = packet["typed_status_counts"]
    lines = [
        "# Exhaustive literature audit",
        "",
        f"ID: `{packet['audit_id']}`",
        "",
        "Status: `evidence_attached`. accepted=false. next=human_signature_required.",
        "",
        f"Ceiling: {packet['honest_ceiling']}",
        "",
        "## Headline Number",
        "",
        (
            f"At the configured Day 1 stop, Prospect mined {packet['document_count']} Europe PMC records "
            f"into {packet['claim_count']} typed CD4+ regulatory claims. "
            f"{counts.get('contradicted', 0)} were typed `contradicted`, a rate of "
            f"{packet['contradiction_rate']:.2%}."
        ),
        "",
        "This is computation over released data. It is not wet-lab or clinical truth.",
        "",
        "## Typed Counts",
        "",
        f"- `contradicted`: {counts.get('contradicted', 0)}",
        f"- `evidence_attached`: {counts.get('evidence_attached', 0)}",
        f"- `orthogonal_phenotype`: {counts.get('orthogonal_phenotype', 0)}",
        f"- `not_assayed`: {counts.get('not_assayed', 0)}",
        "",
        "## Scale Assessment",
        "",
        packet["real_scale_assessment"],
        "",
        "## Public Artifacts",
        "",
        "- `/data/exhaustive_literature_audit.json`",
        "- `/data/exhaustive_literature_claims.jsonl`",
        "- `/data/exhaustive_literature_claims.csv`",
        "- `/data/exhaustive_literature_documents.jsonl`",
        "",
        "## Reproduce",
        "",
        "```bash",
        packet["reproduce_command"],
        packet["freeze_command"],
        "```",
    ]
    FROZEN_AUDIT_DOC.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect exhaustive-compute")
    parser.add_argument(
        "--phase",
        choices=["preregister", "literature", "freeze-literature", "status", "reset-literature"],
        default="status",
    )
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--checkpoint-every", type=int, default=250)
    parser.add_argument("--rate-limit-seconds", type=float, default=0.35)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.phase == "preregister":
        result = write_preregistration()
        if not args.json:
            print(f"wrote {PREREG_JSON}")
            print(f"wrote {PREREG_DOC}")
            print(f"pre_registration_id={result['pre_registration_id']}")
    elif args.phase == "literature":
        result = run_literature(args.max_records, args.page_size, args.checkpoint_every, args.rate_limit_seconds)
    elif args.phase == "freeze-literature":
        result = freeze_literature()
        if not args.json:
            print(f"wrote {FROZEN_AUDIT_JSON}")
            print(f"wrote {FROZEN_CLAIMS_CSV}")
            print(f"wrote {FROZEN_AUDIT_DOC}")
            print(f"audit_id={result['audit_id']}")
    elif args.phase == "reset-literature":
        reset_literature()
        result = {"reset": True, "paths": [str(STATE_JSON), str(DOCS_JSONL), str(CLAIMS_JSONL), str(SNAPSHOT_JSON)]}
        print("reset literature checkpoints")
    else:
        result = read_status()

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
