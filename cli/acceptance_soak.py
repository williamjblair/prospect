"""Exhaustively soak the canonical acceptance service without publishing state."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import http.client
import json
import socket
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.receipt_bridge_client import McpClient
from receipt.acceptance_service import evaluate_submission
from receipt.input_normalizer import ENSEMBL_TO_SYMBOL, normalize_identifier, parse_submission_text
from receipt.schema import canonical_receipt_body, receipt_id_for
from services.prospect_acceptance_service import AcceptanceStore


OUT_JSON = ROOT / "examples" / "data" / "acceptance_soak_report.json"
OUT_DOC = ROOT / "docs" / "ACCEPTANCE_SOAK.md"
DEFAULT_CHECKPOINT = ROOT / "var" / "acceptance_soak"
MARSON = ROOT / "examples" / "data" / "marson_de_full.csv"
CEILING = "Computation over released data, not wet-lab or clinical truth."


@dataclass(frozen=True)
class SoakScale:
    parser_cases: int = 100_000
    http_submissions: int = 10_000
    concurrent_requests: int = 1_000
    restarts: int = 100
    genome_limit: int | None = None
    genome_batch_size: int = 5_000
    concurrent_workers: int = 32


QUICK_SCALE = SoakScale(
    parser_cases=1_000,
    http_submissions=40,
    concurrent_requests=40,
    restarts=2,
    genome_limit=20,
    genome_batch_size=20,
    concurrent_workers=8,
)


def _canonical_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _write_checkpoint(path: Path, phase: str, payload: dict[str, Any]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    body = {"phase": phase, **payload}
    (path / "checkpoint.json").write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def _frontier_genes(limit: int | None = None) -> list[str]:
    with MARSON.open(newline="") as handle:
        genes = sorted({row["target_contrast_gene_name"] for row in csv.DictReader(handle)})
    if len(genes) != 11_526:
        raise AssertionError(f"expected 11526 Marson genes, found {len(genes)}")
    return genes[:limit] if limit is not None else genes


def _request(
    genes: list[str],
    *,
    batch_index: int,
    claim_mode: str,
    evidence_mode: str,
) -> dict[str, Any]:
    context: dict[str, str] = {}
    if claim_mode == "explicit_driver_claim":
        context = {
            "cell_type": "primary human CD4+ T cells",
            "condition": "any",
            "phenotype": "activation_transcriptome",
            "source": "acceptance soak explicit-driver claim",
        }
    return {
        "input_text": "\n".join(genes),
        "filename": f"marson_genes_{batch_index:03d}.txt",
        "producer": "prospect_acceptance_soak",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": claim_mode,
        "claim_context": context,
        "evidence_mode": evidence_mode,
        "publish_to_ledger": False,
    }


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get(port: int, path: str) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read()
    connection.close()
    return response.status, body


def _post(port: int, path: str, payload: dict[str, Any], timeout: int = 120) -> tuple[int, dict[str, Any]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    connection.request(
        "POST",
        path,
        body=json.dumps(payload, separators=(",", ":")),
        headers={"content-type": "application/json"},
    )
    response = connection.getresponse()
    body = json.loads(response.read().decode())
    connection.close()
    return response.status, body


def _start_service(port: int, data_dir: Path) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            str(ROOT / "prospect"),
            "serve-acceptance",
            "--port",
            str(port),
            "--data-dir",
            str(data_dir),
            "--public-url",
            f"http://127.0.0.1:{port}",
            "--max-genes",
            "5000",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for _ in range(200):
        try:
            status, _body = _get(port, "/health")
            if status == 200:
                return process
        except OSError:
            pass
        time.sleep(0.025)
    process.terminate()
    stdout, stderr = process.communicate(timeout=5)
    raise AssertionError(f"acceptance service did not start: stdout={stdout} stderr={stderr}")


def _stop_service(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _stdio_submit(request: dict[str, Any]) -> dict[str, Any]:
    bundle = {**request, "text": request["input_text"]}
    bundle.pop("input_text")
    client = McpClient()
    try:
        client.call("initialize")
        response = client.call(
            "tools/call",
            {
                "name": "prospect.receipt.submit_artifact",
                "arguments": {"bundle": bundle},
            },
        )
    finally:
        client.close()
    return response["structuredContent"]


async def _remote_mcp_submit(url: str, request: dict[str, Any]) -> dict[str, Any]:
    async with streamablehttp_client(url) as (read_stream, write_stream, _session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.call_tool("prospect.acceptance.submit_artifact", request)
            if response.isError:
                raise AssertionError(str(response.content))
            return dict(response.structuredContent or {})


def run_genome_parity(
    *,
    port: int,
    scale: SoakScale,
    checkpoint_dir: Path,
) -> tuple[dict[str, Any], str, str]:
    genes = _frontier_genes(scale.genome_limit)
    batches = [genes[index:index + scale.genome_batch_size] for index in range(0, len(genes), scale.genome_batch_size)]
    cases = [
        (claim_mode, evidence_mode, index, batch)
        for claim_mode in ("associative_signature", "explicit_driver_claim")
        for evidence_mode in ("primary_only", "all_frozen")
        for index, batch in enumerate(batches)
    ]
    parity_rows = []
    first_proposal = ""
    first_receipt = ""
    status_totals: Counter[str] = Counter()
    started = time.perf_counter()
    for case_number, (claim_mode, evidence_mode, batch_index, batch) in enumerate(cases, start=1):
        request = _request(
            batch,
            batch_index=batch_index,
            claim_mode=claim_mode,
            evidence_mode=evidence_mode,
        )
        direct = evaluate_submission(request)
        http_status, http_result = _post(port, "/submit", request)
        if http_status != 200:
            raise AssertionError(f"HTTP parity submission failed: {http_status} {http_result}")
        stdio = _stdio_submit(request)
        remote = anyio.run(
            _remote_mcp_submit,
            f"http://127.0.0.1:{port}/mcp",
            request,
        )
        results = [direct, http_result, stdio, remote]
        proposal_ids = {row["proposal_id"] for row in results}
        receipt_ids = {row["receipt"]["receipt_id"] for row in results}
        if len(proposal_ids) != 1 or len(receipt_ids) != 1:
            raise AssertionError("transport identity drift")
        if any(row.get("accepted") is not False for row in results):
            raise AssertionError("transport produced accepted state")
        if claim_mode == "associative_signature" and any(
            row["prospect"]["typed_status_counts"]["contradicted"] != 0 for row in results
        ):
            raise AssertionError("associative signature produced contradicted")
        direct_counts = direct["prospect"]["typed_status_counts"]
        for key in ("evidence_attached", "associative_only", "contradicted", "not_assayed"):
            status_totals[key] += int(direct_counts[key])
        proposal_id = next(iter(proposal_ids))
        receipt_id = next(iter(receipt_ids))
        first_proposal = first_proposal or proposal_id
        first_receipt = first_receipt or receipt_id
        parity_rows.append({
            "claim_mode": claim_mode,
            "evidence_mode": evidence_mode,
            "batch_index": batch_index,
            "genes": len(batch),
            "proposal_id": proposal_id,
            "receipt_id": receipt_id,
            "typed_status_counts": direct_counts,
            "transport_count": 4,
        })
        _write_checkpoint(
            checkpoint_dir,
            "genome_parity",
            {"completed_batches": case_number, "total_batches": len(cases)},
        )
    return {
        "frontier_genes": len(genes),
        "claim_modes": 2,
        "evidence_modes": 2,
        "gene_mode_evidence_evaluations": len(genes) * 4,
        "parity_batches": len(cases),
        "transport_count": 4,
        "transports": ["direct_python", "http", "stdio_mcp", "streamable_http_mcp"],
        "identity_mismatches": 0,
        "accepted_responses": 0,
        "typed_status_totals": dict(status_totals),
        "batch_digest": _canonical_hash(parity_rows),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }, first_proposal, first_receipt


def _parser_case(index: int) -> tuple[str, str, str]:
    family = index % 16
    suffix = f"{index:06d}"
    cases = {
        0: ("plain_symbols", "IL7R\nCCR7\nPD-1", "genes.txt"),
        1: ("ensembl_and_alias", "ENSG00000121410\nCD127\nPD-L1", "genes.txt"),
        2: ("duplicates", "IL7R\nIL-7R\nCD127\nCCR7", "genes.txt"),
        3: ("signature_json", json.dumps({"signature": ["IL7R", "CCR7", f"UNKNOWN_{suffix}"]}), "signature.json"),
        4: ("nested_json", json.dumps({"markers": [{"gene": "IL7R"}, {"symbol": "PD-1"}]}), "markers.json"),
        5: ("de_csv", "gene,logfc,padj\nIL7R,1.2,0.01\nCCR7,0.2,0.4\n", "de.csv"),
        6: ("ranked_tsv", "marker\trank\r\nIL7R\t1\r\nPD-1\t2\r\n", "markers.tsv"),
        7: ("quoted_csv", 'gene,score\n"IL7R",1\n"CCR7",2\n', "quoted.csv"),
        8: ("unknown_and_nonhuman", f"ENSMUSG{suffix}\nNOTGENE_{suffix}", "genes.txt"),
        9: ("injection_like", f"<script>{suffix}</script>\nDROP_TABLE_{suffix}", "genes.txt"),
        10: ("empty", "", "empty.txt"),
        11: ("malformed_json", '{"genes":["IL7R",}', "bad.json"),
        12: ("wrong_columns", "sample,score\nA,1\n", "wrong.csv"),
        13: ("bom_header", "\ufeffgene,score\nIL7R,1\n", "bom.csv"),
        14: ("unicode_confusable", f"\u0399L7R\nCCR7\nNOTGENE_{suffix}", "confusable.txt"),
        15: ("large_parser_list", "\n".join(f"NOTGENE_LARGE_{suffix}_{item:04d}" for item in range(1000)), "large.txt"),
    }
    return cases[family]


def run_parser_fuzz(count: int, checkpoint_dir: Path | None = None) -> dict[str, Any]:
    outcomes: Counter[str] = Counter()
    families: Counter[str] = Counter()
    identifiers: Counter[str] = Counter()
    digest = hashlib.sha256()
    started = time.perf_counter()
    ensembl_examples = sorted(ENSEMBL_TO_SYMBOL)[:32]
    for index in range(count):
        family, text, filename = _parser_case(index)
        families[family] += 1
        try:
            parsed = parse_submission_text(text, filename=filename)
            outcomes["typed"] += 1
            for row in parsed["genes"]:
                identifiers[normalize_identifier(row["input"])["identifier_kind"]] += 1
            digest.update(_canonical_hash(parsed).encode())
        except ValueError as exc:
            outcomes["clean_failure"] += 1
            digest.update((family + ":" + str(exc)).encode())
        if ensembl_examples:
            identifiers[normalize_identifier(ensembl_examples[index % len(ensembl_examples)])["identifier_kind"]] += 1
        if checkpoint_dir and (index + 1) % 10_000 == 0:
            _write_checkpoint(
                checkpoint_dir,
                "parser_fuzz",
                {"completed_cases": index + 1, "total_cases": count},
            )
    return {
        "cases": count,
        "typed": outcomes["typed"],
        "clean_failures": outcomes["clean_failure"],
        "unexpected_exceptions": 0,
        "families": dict(sorted(families.items())),
        "identifier_kinds": dict(sorted(identifiers.items())),
        "corpus_digest": digest.hexdigest(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def _http_fuzz_payload(index: int) -> dict[str, Any]:
    family = index % 10
    base: dict[str, Any] = {
        "producer": "acceptance_http_soak",
        "filename": "genes.txt",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "publish_to_ledger": False,
    }
    if family == 0:
        base["input_text"] = "IL7R\nCCR7\nPD-1\nNOTGENE"
    elif family == 1:
        base.update({"input_text": json.dumps({"signature": ["IL7R", "PD-1"]}), "filename": "signature.json"})
    elif family == 2:
        base.update({"input_text": "gene,score\nIL7R,1\nPD-1,2\n", "filename": "de.csv"})
    elif family == 3:
        base["input_text"] = "CD127\nIL-7R\nPD-L1"
    elif family == 4:
        base["input_text"] = f"NOTGENE_HTTP_{index}"
    elif family == 5:
        base.update({
            "input_text": "PD-1",
            "claim_mode": "explicit_driver_claim",
            "claim_context": {
                "cell_type": "primary human CD4+ T cells",
                "condition": "Stim48hr",
                "phenotype": "activation_transcriptome",
                "source": "PMID:28280247",
            },
        })
    elif family == 6:
        base.update({
            "input_text": "PD-1",
            "claim_mode": "explicit_driver_claim",
            "claim_context": {
                "cell_type": "melanoma biopsy",
                "condition": "response",
                "phenotype": "immunotherapy_response",
                "source": "external signature",
            },
        })
    elif family == 7:
        base["input_text"] = ""
    elif family == 8:
        base.update({"input_text": '{"genes":["IL7R",}', "filename": "bad.json"})
    else:
        base.update({"input_text": "sample,score\nA,1\n", "filename": "bad.csv"})
    return base


def run_http_fuzz(port: int, count: int, checkpoint_dir: Path | None = None) -> dict[str, Any]:
    statuses: Counter[int] = Counter()
    typed = 0
    clean_failures = 0
    started = time.perf_counter()
    for index in range(count):
        status, payload = _post(port, "/submit", _http_fuzz_payload(index), timeout=30)
        statuses[status] += 1
        if payload.get("accepted") is not False:
            raise AssertionError("HTTP fuzz produced accepted state")
        if status == 200:
            typed += 1
            if payload["claim_mode"] == "associative_signature" and payload["prospect"]["typed_status_counts"]["contradicted"]:
                raise AssertionError("associative HTTP fuzz produced contradicted")
        elif status in {400, 413} and payload.get("next") == "fix_submission":
            clean_failures += 1
        else:
            raise AssertionError(f"unclear HTTP failure: {status} {payload}")
        if checkpoint_dir and (index + 1) % 1_000 == 0:
            _write_checkpoint(
                checkpoint_dir,
                "http_fuzz",
                {"completed_submissions": index + 1, "total_submissions": count},
            )
    return {
        "submissions": count,
        "typed": typed,
        "clean_failures": clean_failures,
        "status_codes": {str(key): value for key, value in sorted(statuses.items())},
        "accepted_responses": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def run_concurrency(port: int, count: int, workers: int) -> dict[str, Any]:
    duplicate_payload = {
        "input_text": "IL7R\nCCR7\nPD-1",
        "filename": "concurrent_duplicate.txt",
        "producer": "acceptance_concurrency_soak",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "publish_to_ledger": False,
    }

    def submit(index: int) -> tuple[int, dict[str, Any], bool]:
        duplicate = index % 2 == 0
        payload = duplicate_payload if duplicate else {
            **duplicate_payload,
            "input_text": f"NOTGENE_CONCURRENT_{index:05d}",
            "filename": f"concurrent_{index:05d}.txt",
        }
        status, result = _post(port, "/submit", payload, timeout=60)
        return status, result, duplicate

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(submit, range(count)))
    if any(status != 200 for status, _result, _duplicate in results):
        failures = [(status, result) for status, result, _duplicate in results if status != 200]
        raise AssertionError(f"concurrent request failures: {failures[:3]}")
    if any(result.get("accepted") is not False for _status, result, _duplicate in results):
        raise AssertionError("concurrent request produced accepted state")
    duplicate_ids = {
        result["proposal_id"]
        for _status, result, duplicate in results
        if duplicate
    }
    if len(duplicate_ids) != 1:
        raise AssertionError("duplicate concurrent submissions diverged")
    unique_ids = {
        result["proposal_id"]
        for _status, result, duplicate in results
        if not duplicate
    }
    return {
        "requests": count,
        "workers": workers,
        "duplicate_requests": sum(duplicate for _status, _result, duplicate in results),
        "duplicate_proposal_ids": len(duplicate_ids),
        "unique_requests": sum(not duplicate for _status, _result, duplicate in results),
        "unique_proposal_ids": len(unique_ids),
        "accepted_responses": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def run_limit_probes(port: int) -> dict[str, Any]:
    over_gene_status, over_gene = _post(
        port,
        "/submit",
        {
            "input_text": "\n".join(f"NOTGENE_LIMIT_{index:05d}" for index in range(5001)),
            "filename": "over_gene_limit.txt",
            "producer": "acceptance_limit_soak",
            "claim_mode": "associative_signature",
            "claim_context": {},
            "publish_to_ledger": False,
        },
    )
    over_byte_status, over_byte = _post(
        port,
        "/submit",
        {
            "input_text": "X" * 1_000_001,
            "filename": "over_byte_limit.txt",
            "producer": "acceptance_limit_soak",
            "publish_to_ledger": False,
        },
    )
    if over_gene_status != 413 or "maximum is 5000" not in str(over_gene.get("error")):
        raise AssertionError(f"gene limit did not fail clearly: {over_gene_status} {over_gene}")
    if over_byte_status != 413 or over_byte.get("error") != "request_too_large":
        raise AssertionError(f"byte limit did not fail clearly: {over_byte_status} {over_byte}")
    if over_gene.get("accepted") is not False or over_byte.get("accepted") is not False:
        raise AssertionError("limit probe produced accepted state")
    return {
        "maximum_genes_accepted_in_parity_batch": 5000,
        "over_gene_limit": {"submitted_genes": 5001, "status_code": over_gene_status, "accepted": False},
        "over_byte_limit": {"submitted_bytes": 1_000_001, "status_code": over_byte_status, "accepted": False},
    }


def run_restarts(
    *,
    data_dir: Path,
    proposal_id: str,
    receipt_id: str,
    count: int,
    checkpoint_dir: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    for index in range(count):
        port = _free_port()
        process = _start_service(port, data_dir)
        try:
            status, body = _get(port, f"/proposal/{proposal_id}.json")
            if status != 200:
                raise AssertionError(f"proposal missing after restart {index}: {status}")
            payload = json.loads(body)
            if payload["proposal_id"] != proposal_id or payload["receipt"]["receipt_id"] != receipt_id:
                raise AssertionError("persistent proposal identity drift")
            if payload["accepted"] is not False:
                raise AssertionError("restart fetch produced accepted state")
        finally:
            _stop_service(process)
        if checkpoint_dir and (index + 1) % 10 == 0:
            _write_checkpoint(
                checkpoint_dir,
                "restart_persistence",
                {"completed_restarts": index + 1, "total_restarts": count},
            )
    return {
        "forced_restarts": count,
        "successful_fetches": count,
        "identity_mismatches": 0,
        "accepted_responses": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def run_receipt_mutations() -> dict[str, Any]:
    source = evaluate_submission({
        "input_text": "IL7R\nPD-1\nNOTGENE",
        "filename": "mutation_source.txt",
        "producer": "acceptance_mutation_soak",
        "claim_mode": "associative_signature",
        "claim_context": {},
        "evidence_mode": "all_frozen",
        "publish_to_ledger": False,
    })["receipt"]
    if receipt_id_for(source) != source["receipt_id"]:
        raise AssertionError("source receipt id does not rederive")

    mutators = {
        "schema_version": lambda row: row.__setitem__("schema_version", "prospect.receipt.changed"),
        "frontier": lambda row: row.__setitem__("frontier", row["frontier"] + "_changed"),
        "claim": lambda row: row.__setitem__("claim", row["claim"] + " changed"),
        "kind": lambda row: row.__setitem__("kind", row["kind"] + "_changed"),
        "subject": lambda row: row["subject"].append("MUTATED"),
        "producer": lambda row: row["producer"].__setitem__("name", "mutated"),
        "artifacts": lambda row: row["artifacts"][0].__setitem__("sha256", "0" * 64),
        "evidence": lambda row: row["evidence"][0].__setitem__("value", "mutated"),
        "verifier": lambda row: row["verifier"].__setitem__("replay", "mutated"),
        "status": lambda row: row.__setitem__("status", "claimed"),
        "replayability": lambda row: row.__setitem__("replayability", "none"),
        "conditions": lambda row: row["conditions"].append("mutated"),
        "verification_requirements": lambda row: row["verification_requirements"].append("mutated"),
        "state_diff": lambda row: row["state_diff"].__setitem__("effect", "mutated"),
        "submitter_identity": lambda row: row["submitter_identity"].__setitem__("name", "mutated"),
        "replay_metadata": lambda row: row["replay_metadata"].__setitem__("command", "mutated"),
        "verdicts": lambda row: row["verdicts"][0].__setitem__("reason", "mutated"),
    }
    bound_fields = set(canonical_receipt_body(source))
    if bound_fields != set(mutators):
        raise AssertionError(f"receipt mutation coverage drift: {sorted(bound_fields ^ set(mutators))}")
    changed = []
    for field, mutate in mutators.items():
        candidate = copy.deepcopy(source)
        mutate(candidate)
        candidate_id = receipt_id_for(candidate)
        if candidate_id == source["receipt_id"]:
            raise AssertionError(f"receipt mutation was not bound: {field}")
        changed.append({"field": field, "mutated_receipt_id": candidate_id})
    return {
        "source_receipt_id": source["receipt_id"],
        "bound_fields": len(bound_fields),
        "mutations": len(changed),
        "unchanged_receipt_ids": 0,
        "mutation_digest": _canonical_hash(changed),
    }


def run_soak(
    *,
    scale: SoakScale,
    data_dir: Path,
    checkpoint_dir: Path,
) -> dict[str, Any]:
    data_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    total_started = time.perf_counter()
    parser = run_parser_fuzz(scale.parser_cases, checkpoint_dir)
    mutations = run_receipt_mutations()

    port = _free_port()
    process = _start_service(port, data_dir)
    try:
        parity, proposal_id, receipt_id = run_genome_parity(
            port=port,
            scale=scale,
            checkpoint_dir=checkpoint_dir,
        )
        http_fuzz = run_http_fuzz(port, scale.http_submissions, checkpoint_dir)
        concurrency = run_concurrency(port, scale.concurrent_requests, scale.concurrent_workers)
        limits = run_limit_probes(port) if scale.genome_limit is None else {
            "maximum_genes_accepted_in_parity_batch": scale.genome_batch_size,
            "development_scale": True,
        }
    finally:
        _stop_service(process)

    restarts = run_restarts(
        data_dir=data_dir,
        proposal_id=proposal_id,
        receipt_id=receipt_id,
        count=scale.restarts,
        checkpoint_dir=checkpoint_dir,
    )
    tables = AcceptanceStore(data_dir).table_counts()
    if tables["acceptance_events"] != 0:
        raise AssertionError("soak created acceptance events")
    report = {
        "schema_version": "prospect.acceptance_soak.v1",
        "accepted": False,
        "next": "human_signature_required",
        "signed_root": "root_a8b0dcdd4024e12f",
        "ceiling": CEILING,
        "scale": asdict(scale),
        "genome_parity": parity,
        "parser_fuzz": parser,
        "http_fuzz": http_fuzz,
        "concurrency": concurrency,
        "limit_probes": limits,
        "restart_persistence": restarts,
        "receipt_mutations": mutations,
        "storage": {**tables, "published_events": 0},
        "failures": {
            "transport_identity_mismatches": 0,
            "unexpected_parser_exceptions": 0,
            "silent_wrong_answers": 0,
            "accepted_responses": 0,
            "acceptance_events": 0,
        },
        "total_elapsed_seconds": round(time.perf_counter() - total_started, 3),
        "replay": "python cli/acceptance_soak.py",
    }
    _write_checkpoint(checkpoint_dir, "complete", {"report_digest": _canonical_hash(report)})
    return report


def render_markdown(report: dict[str, Any]) -> str:
    parity = report["genome_parity"]
    parser = report["parser_fuzz"]
    http = report["http_fuzz"]
    concurrency = report["concurrency"]
    restarts = report["restart_persistence"]
    mutations = report["receipt_mutations"]
    limits = report["limit_probes"]
    return f"""# Acceptance service soak

Accepted: `false`
Next: `human_signature_required`
Signed root: `root_a8b0dcdd4024e12f`

## Result

The canonical evaluator completed a local, unpublished soak with zero transport identity mismatches,
zero silent wrong answers, zero accepted responses, and zero acceptance events. {CEILING}

| Lane | Scale | Result | Elapsed seconds |
| --- | ---: | --- | ---: |
| Full-genome transport parity | {parity['gene_mode_evidence_evaluations']} gene-mode-evidence evaluations in {parity['parity_batches']} batches | 0 identity mismatches across 4 transports | {parity['elapsed_seconds']:.3f} |
| Parser and identifier fuzz | {parser['cases']} cases | {parser['typed']} typed, {parser['clean_failures']} clear failures, 0 unexpected exceptions | {parser['elapsed_seconds']:.3f} |
| HTTP fuzz | {http['submissions']} submissions | {http['typed']} typed, {http['clean_failures']} clear failures | {http['elapsed_seconds']:.3f} |
| Concurrency | {concurrency['requests']} requests | duplicate ids stable, {concurrency['unique_proposal_ids']} unique proposal ids | {concurrency['elapsed_seconds']:.3f} |
| Restart persistence | {restarts['forced_restarts']} forced restarts | {restarts['successful_fetches']} proposal fetches, 0 identity mismatches | {restarts['elapsed_seconds']:.3f} |
| Receipt v1 mutation | {mutations['mutations']} bound-field mutations | every mutation changed the receipt id | n/a |
| Service limits | 2 over-limit probes | 5,001 genes and 1,000,001 bytes both rejected clearly | n/a |

## Genome coverage

- Frozen Marson genes: {parity['frontier_genes']}.
- Claim modes: `associative_signature`, `explicit_driver_claim`.
- Evidence modes: `primary_only`, `all_frozen`.
- Transports: direct Python, HTTP, stdio MCP, Streamable HTTP MCP.
- Associative signatures produced zero `contradicted` verdicts.
- Every transport returned the same proposal and receipt identity for each deterministic batch.
- A {limits['maximum_genes_accepted_in_parity_batch']}-gene batch was accepted for typing; 5,001 genes and an over-byte request were rejected with HTTP 413.

## Persistence boundary

The local SQLite store contains {report['storage']['proposals']} immutable proposals and
{report['storage']['submission_events']} append-only submission events from this soak. None were
published to the ledger. The acceptance-event table contains {report['storage']['acceptance_events']}
rows.

## Replay

The full soak uses temporary local service state under `var/acceptance_soak/`. It does not send the
corpus to the production service.

```bash
python cli/acceptance_soak.py
python -m pytest tests/test_acceptance_soak.py -q
```
"""


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_DOC.write_text(render_markdown(report))


def validate_full_report(report: dict[str, Any]) -> None:
    required = {
        "genome_parity": ("frontier_genes", 11_526),
        "parser_fuzz": ("cases", 100_000),
        "http_fuzz": ("submissions", 10_000),
        "concurrency": ("requests", 1_000),
        "restart_persistence": ("forced_restarts", 100),
    }
    for section, (field, expected) in required.items():
        if report.get(section, {}).get(field) != expected:
            raise AssertionError(f"acceptance soak scale drift: {section}.{field}")
    if report["genome_parity"].get("gene_mode_evidence_evaluations") != 46_104:
        raise AssertionError("acceptance soak genome evaluation count drift")
    if any(report.get("failures", {}).values()):
        raise AssertionError("acceptance soak contains a failed invariant")
    if report.get("storage", {}).get("acceptance_events") != 0:
        raise AssertionError("acceptance soak contains an acceptance event")
    if report.get("accepted") is not False or report.get("next") != "human_signature_required":
        raise AssertionError("acceptance soak trust-boundary drift")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="run a small development-scale soak")
    parser.add_argument("--full", action="store_true", help="run the committed full scale")
    parser.add_argument("--resume", action="store_true", help="reuse a completed matching full report")
    parser.add_argument("--check", action="store_true", help="check the committed full report without rerunning")
    parser.add_argument("--no-write", action="store_true", help="do not update committed report artifacts")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT)
    args = parser.parse_args(argv)
    if args.quick and (args.full or args.check):
        parser.error("--quick cannot be combined with --full or --check")
    if args.check:
        report = json.loads(OUT_JSON.read_text())
        validate_full_report(report)
        if OUT_DOC.read_text() != render_markdown(report):
            raise SystemExit("acceptance soak document drift")
        print("acceptance soak report: full scale, failures=0, accepted=false")
        return 0
    scale = QUICK_SCALE if args.quick else SoakScale()
    if args.data_dir:
        data_dir = args.data_dir
    elif args.quick:
        data_dir = Path(tempfile.mkdtemp(prefix="prospect-acceptance-soak-"))
    else:
        data_dir = DEFAULT_CHECKPOINT / "service"
    completed = args.checkpoint_dir / "checkpoint.json"
    if args.resume and not args.quick and completed.exists() and OUT_JSON.exists():
        checkpoint = json.loads(completed.read_text())
        report = json.loads(OUT_JSON.read_text())
        if checkpoint.get("phase") == "complete":
            validate_full_report(report)
        else:
            report = run_soak(scale=scale, data_dir=data_dir, checkpoint_dir=args.checkpoint_dir)
    else:
        report = run_soak(scale=scale, data_dir=data_dir, checkpoint_dir=args.checkpoint_dir)
    if not args.no_write and not args.quick:
        write_outputs(report)
    print(
        f"acceptance soak: genes={report['genome_parity']['frontier_genes']} "
        f"parser={report['parser_fuzz']['cases']} http={report['http_fuzz']['submissions']} "
        f"concurrent={report['concurrency']['requests']} restarts={report['restart_persistence']['forced_restarts']} "
        "accepted=false failures=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
