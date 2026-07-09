"""Generic Prospect acceptance service tests."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from receipt.acceptance_service import build_submission_result, evaluate_submission
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


def test_build_submission_result_returns_proposal_url_and_typed_counts():
    result = build_submission_result("IL7R\nCCR7\nPD-1\nNOTGENE", filename="genes.txt", source_name="hackathon_team")

    assert result["accepted"] is False
    assert result["next"] == "human_signature_required"
    assert result["proposal_id"].startswith("proposal_")
    assert result["proposal_url"].startswith("/proposal/")
    assert result["receipt"]["receipt_id"].startswith("rcpt_")
    assert result["prospect"]["typed_status_counts"] == {
        "genes": 4,
        "drivers": 1,
        "evidence_attached": 1,
        "passengers": 2,
        "associative_only": 2,
        "contradicted": 0,
        "not_assayed": 1,
    }
    assert {row["typed_status"] for row in result["verdicts"]} == {
        "evidence_attached",
        "associative_only",
        "not_assayed",
    }
    assert "Computation over released data" in result["prospect"]["ceiling"]


def test_contradicted_requires_explicit_comparable_driver_claim():
    associative = build_submission_result("PD-1", filename="genes.txt")
    explicit = evaluate_submission({
        "input_text": "PD-1",
        "filename": "driver.txt",
        "producer": "review_team",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "explicit_driver_claim",
        "claim_context": {
            "cell_type": "primary human CD4+ T cells",
            "condition": "strongest",
            "phenotype": "activation_transcriptome",
            "source": "submitted causal claim",
        },
    })
    orthogonal = evaluate_submission({
        "input_text": "PD-1",
        "filename": "driver.txt",
        "producer": "review_team",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "explicit_driver_claim",
        "claim_context": {
            "cell_type": "primary human CD4+ T cells",
            "condition": "strongest",
            "phenotype": "cytokine_production",
            "source": "submitted causal claim",
        },
    })

    assert associative["verdicts"][0]["typed_status"] == "associative_only"
    assert explicit["verdicts"][0]["typed_status"] == "contradicted"
    assert explicit["comparability"]["status"] == "comparable"
    assert orthogonal["verdicts"][0]["typed_status"] == "associative_only"
    assert orthogonal["comparability"]["status"] == "orthogonal_phenotype"


def test_receipt_binds_claim_context_and_citations():
    base = {
        "input_text": "PD-1",
        "filename": "driver.txt",
        "producer": "review_team",
        "substrate_id": "marson_cd4_activation",
        "claim_mode": "explicit_driver_claim",
        "claim_context": {
            "cell_type": "primary human CD4+ T cells",
            "condition": "Stim48hr",
            "phenotype": "activation_transcriptome",
            "source": "PMID:28280247",
        },
        "citations": ["PMID:28280247"],
    }
    first = evaluate_submission(base)
    changed_context = evaluate_submission({
        **base,
        "claim_context": {**base["claim_context"], "condition": "Stim8hr"},
    })
    changed_citation = evaluate_submission({**base, "citations": ["PMID:12345678"]})

    receipt_ids = {
        first["receipt"]["receipt_id"],
        changed_context["receipt"]["receipt_id"],
        changed_citation["receipt"]["receipt_id"],
    }
    assert len(receipt_ids) == 3
    assert first["receipt"]["replay_metadata"]["request"] == {
        "claim_mode": "explicit_driver_claim",
        "claim_context": base["claim_context"],
        "citations": ["PMID:28280247"],
        "substrate_id": "marson_cd4_activation",
    }


def test_canonical_evaluator_emits_receipt_v1_and_binds_artifact_manifest():
    schema = json.loads((Path(__file__).resolve().parents[1] / "receipt" / "receipt_schema_v1.json").read_text())
    input_text = "IL7R\nCCR7"
    input_sha = __import__("hashlib").sha256(input_text.encode()).hexdigest()
    base = {
        "input_text": input_text,
        "filename": "genes.txt",
        "producer": "external_team",
        "artifacts": [
            {"name": "genes.txt", "sha256": input_sha, "locator": "artifact://genes"},
            {"name": "analysis.json", "sha256": "a" * 64, "locator": "artifact://analysis"},
        ],
    }

    first = evaluate_submission(base)
    changed = evaluate_submission({
        **base,
        "artifacts": [
            base["artifacts"][0],
            {"name": "analysis.json", "sha256": "b" * 64, "locator": "artifact://analysis"},
        ],
    })

    errors = list(Draft202012Validator(schema).iter_errors(first["receipt"]))
    assert errors == []
    assert first["receipt"]["schema_version"] == "prospect.receipt.v1"
    assert first["receipt"]["receipt_id"] != changed["receipt"]["receipt_id"]
    assert first["receipt"]["replay_metadata"]["verifier"] == "ProspectCausalReceiptBridge"
    assert first["receipt"]["replay_metadata"]["replayability"] == "exact"
    assert first["receipt"]["replay_metadata"]["frontier"] == "prospect_marson_cd4_perturbseq"


def test_artifact_manifest_rejects_a_mismatched_input_hash():
    with pytest.raises(ValueError, match="does not match submitted input bytes"):
        evaluate_submission({
            "input_text": "IL7R",
            "filename": "genes.txt",
            "producer": "external_team",
            "artifacts": [{"name": "genes.txt", "sha256": "a" * 64, "locator": "artifact://genes"}],
        })


def test_build_submission_result_handles_huge_duplicate_input():
    text = "\n".join(["IL7R"] * 1000 + ["CCR7"] * 1000)
    result = build_submission_result(text, filename="huge.txt", source_name="stress")

    assert result["normalized_input"]["submitted_items"] == 2000
    assert result["normalized_input"]["unique_genes"] == 2
    assert result["prospect"]["typed_status_counts"]["genes"] == 2
    assert result["prospect"]["typed_status_counts"]["drivers"] == 1
    assert result["prospect"]["typed_status_counts"]["passengers"] == 1
