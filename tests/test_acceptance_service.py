"""Generic Prospect acceptance service tests."""
import json
from pathlib import Path

import pytest

from receipt.acceptance_service import build_submission_result
from receipt.input_normalizer import parse_submission_text


def test_parse_signature_json_deduplicates_aliases_and_ensembl_ids():
    payload = json.dumps({
        "responder_up": ["IL7R", "PD-1", "ENSG00000121410", "IL7R"],
        "AUC": {"loo": 0.8},
    })

    parsed = parse_submission_text(payload, filename="signature_genes.json")

    assert parsed["input_kind"] == "signature_json"
    assert [row["gene"] for row in parsed["genes"]] == ["IL7R", "PDCD1", "A1BG"]
    assert parsed["genes"][1]["identifier_kind"] == "alias"
    assert parsed["genes"][2]["identifier_kind"] == "ensembl"
    assert any("duplicate" in warning for warning in parsed["warnings"])


def test_parse_de_csv_accepts_varied_columns_and_ranked_markers():
    text = "marker,logFC,adj.P.Val\nTIM3,-1.2,0.01\nCCR7,0.7,0.02\n"

    parsed = parse_submission_text(text, filename="markers.csv")

    assert parsed["input_kind"] == "table"
    assert [row["gene"] for row in parsed["genes"]] == ["HAVCR2", "CCR7"]
    assert parsed["genes"][0]["source_column"] == "marker"


def test_parse_plain_gene_list_handles_unknowns_without_crashing():
    parsed = parse_submission_text("IL7R\nmouse_gene\nENSMUSG00000000001\n", filename="genes.txt")

    assert parsed["input_kind"] == "gene_list"
    assert [row["gene"] for row in parsed["genes"]] == ["IL7R", "MOUSE_GENE", "ENSMUSG00000000001"]
    assert parsed["genes"][1]["identifier_kind"] == "unknown"
    assert parsed["genes"][2]["identifier_kind"] == "unknown"


@pytest.mark.parametrize("text", ["", "score,padj\n1,0.1\n", "[]"])
def test_parse_bad_inputs_fail_clearly(text):
    with pytest.raises(ValueError) as exc:
        parse_submission_text(text, filename="bad.txt")
    assert str(exc.value)
    assert "Traceback" not in str(exc.value)


def test_build_submission_result_returns_receipt_state_url_and_typed_counts():
    result = build_submission_result("IL7R\nCCR7\nPD-1\nNOTGENE", filename="genes.txt", source_name="hackathon_team")

    assert result["accepted"] is False
    assert result["next"] == "human_signature_required"
    assert result["state_id"].startswith("state_")
    assert result["state_url"].startswith("/state/")
    assert result["receipt"]["receipt_id"].startswith("rcpt_")
    assert result["prospect"]["typed_status_counts"] == {
        "genes": 4,
        "drivers": 1,
        "evidence_attached": 1,
        "passengers": 1,
        "associative_only": 1,
        "contradicted": 1,
        "not_assayed": 1,
    }
    assert {row["typed_status"] for row in result["verdicts"]} == {
        "evidence_attached",
        "associative_only",
        "contradicted",
        "not_assayed",
    }
    assert "Computation over released data" in result["prospect"]["ceiling"]


def test_build_submission_result_handles_huge_duplicate_input():
    text = "\n".join(["IL7R"] * 1000 + ["CCR7"] * 1000)
    result = build_submission_result(text, filename="huge.txt", source_name="stress")

    assert result["normalized_input"]["submitted_items"] == 2000
    assert result["normalized_input"]["unique_genes"] == 2
    assert result["prospect"]["typed_status_counts"]["genes"] == 2
    assert result["prospect"]["typed_status_counts"]["drivers"] == 1
    assert result["prospect"]["typed_status_counts"]["passengers"] == 1
