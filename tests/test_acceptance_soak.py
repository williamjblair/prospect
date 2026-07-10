"""Deterministic tests for the exhaustive acceptance-service soak harness."""
from __future__ import annotations

import json
from pathlib import Path

from cli.acceptance_soak import (
    OUT_JSON,
    QUICK_SCALE,
    run_parser_fuzz,
    run_receipt_mutations,
    run_soak,
)
from receipt.frozen_io import sha256_file
from receipt.input_normalizer import parse_submission_text


def test_bom_prefixed_table_is_typed_instead_of_rejected():
    parsed = parse_submission_text("\ufeffgene,score\nIL7R,1\n", filename="bom.csv")

    assert parsed["input_kind"] == "table"
    assert parsed["unique_genes"] == 1
    assert parsed["genes"][0]["gene"] == "IL7R"


def test_frozen_hash_cache_invalidates_when_file_version_changes(tmp_path):
    path = tmp_path / "frozen.txt"
    path.write_text("alpha\n")
    first = sha256_file(path)
    assert sha256_file(path) == first

    path.write_text("bravo\n")
    second = sha256_file(path)

    assert second != first
    assert sha256_file(path) == second


def test_parser_fuzz_has_only_typed_or_clear_failure_outcomes():
    report = run_parser_fuzz(1_600)

    assert report["cases"] == 1_600
    assert report["typed"] + report["clean_failures"] == report["cases"]
    assert report["unexpected_exceptions"] == 0
    assert set(report["families"]) == {
        "bom_header",
        "de_csv",
        "duplicates",
        "empty",
        "ensembl_and_alias",
        "injection_like",
        "large_parser_list",
        "malformed_json",
        "nested_json",
        "plain_symbols",
        "quoted_csv",
        "ranked_tsv",
        "signature_json",
        "unicode_confusable",
        "unknown_and_nonhuman",
        "wrong_columns",
    }


def test_every_receipt_v1_bound_field_changes_identity():
    report = run_receipt_mutations()

    assert report["bound_fields"] == 17
    assert report["mutations"] == 17
    assert report["unchanged_receipt_ids"] == 0


def test_quick_soak_exercises_transports_storage_and_restarts(tmp_path):
    report = run_soak(
        scale=QUICK_SCALE,
        data_dir=tmp_path / "service",
        checkpoint_dir=tmp_path / "checkpoint",
    )

    assert report["accepted"] is False
    assert report["next"] == "human_signature_required"
    assert report["genome_parity"]["frontier_genes"] == 20
    assert report["genome_parity"]["parity_batches"] == 4
    assert report["genome_parity"]["transport_count"] == 4
    assert report["genome_parity"]["identity_mismatches"] == 0
    assert report["http_fuzz"]["submissions"] == 40
    assert report["concurrency"]["requests"] == 40
    assert report["restart_persistence"]["forced_restarts"] == 2
    assert report["storage"]["acceptance_events"] == 0
    assert report["storage"]["published_events"] == 0
    assert report["failures"] == {
        "transport_identity_mismatches": 0,
        "unexpected_parser_exceptions": 0,
        "silent_wrong_answers": 0,
        "accepted_responses": 0,
        "acceptance_events": 0,
    }


def test_committed_full_report_records_required_scale():
    report = json.loads(OUT_JSON.read_text())

    assert report["genome_parity"]["frontier_genes"] == 11_526
    assert report["genome_parity"]["gene_mode_evidence_evaluations"] == 46_104
    assert report["genome_parity"]["parity_batches"] == 12
    assert report["parser_fuzz"]["cases"] == 100_000
    assert report["http_fuzz"]["submissions"] == 10_000
    assert report["concurrency"]["requests"] == 1_000
    assert report["restart_persistence"]["forced_restarts"] == 100
    assert report["limit_probes"]["over_gene_limit"]["status_code"] == 413
    assert report["limit_probes"]["over_byte_limit"]["status_code"] == 413
    assert report["receipt_mutations"]["unchanged_receipt_ids"] == 0
    assert report["storage"]["acceptance_events"] == 0
    assert report["failures"] == {
        "transport_identity_mismatches": 0,
        "unexpected_parser_exceptions": 0,
        "silent_wrong_answers": 0,
        "accepted_responses": 0,
        "acceptance_events": 0,
    }


def test_soak_artifacts_keep_copy_discipline():
    paths = [
        Path(__file__),
        Path(__file__).resolve().parents[1] / "cli" / "acceptance_soak.py",
        Path(__file__).resolve().parents[1] / "receipt" / "frozen_io.py",
        Path(__file__).resolve().parents[1] / "docs" / "ACCEPTANCE_SOAK.md",
        OUT_JSON,
    ]
    combined = "\n".join(path.read_text(errors="ignore") for path in paths)
    assert "\N{EM DASH}" not in combined
    lowered = combined.lower()
    forbidden = ("ve" + "la", "constel" + "late", "car" + "ina")
    assert not any(term in lowered for term in forbidden)
