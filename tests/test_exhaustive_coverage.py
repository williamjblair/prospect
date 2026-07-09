"""Contracts for the exhaustive coverage expansion runner."""
from __future__ import annotations

from frontier.exhaustive_coverage import build_preregistration, compact_coverage_row


def test_exhaustive_coverage_preregistration_locks_source_and_scale():
    packet = build_preregistration()

    assert packet["phase"] == "exhaustive_coverage_expansion_preregistration"
    assert packet["frontier_root"] == "root_a8b0dcdd4024e12f"
    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["anthropic_budget_usd"] == 0
    assert packet["gene_universe"]["gene_count"] == 11526
    assert packet["target_scale"] == "all 11,526 genes in the current frozen atlas"


def test_exhaustive_coverage_preregistration_keeps_noncoverage_honest():
    packet = build_preregistration()
    rules = packet["coverage_rules"]

    assert rules["covered"].startswith("NCBI maps")
    assert rules["mapped_no_tcell_rows"].startswith("NCBI maps")
    assert rules["unmapped"].startswith("NCBI does not map")
    assert rules["noncoverage_policy"] == "noncoverage is never a contradiction"
    assert "resume" in packet["checkpoint_contract"]["resume_rule"]


def test_compact_coverage_row_keeps_counts_without_raw_payload():
    compact = compact_coverage_row({
        "gene": "PGGT1B",
        "gene_id": "5229",
        "coverage_status": "covered",
        "records_filtered": 2,
        "rows": [
            {
                "dataset_id": "763",
                "screen_id": "1905",
                "first_author": "Carnevale J (2022)",
                "cell_type": "T cell",
                "cell_line": "Primary T-cells",
                "phenotype": "cell proliferation",
                "condition": "TCR stimulation",
                "hit_status": "hit",
            },
            {
                "dataset_id": "712",
                "screen_id": "2424",
                "first_author": "Schmidt R (2022)",
                "cell_type": "T cell",
                "cell_line": "CD4+ T-cells",
                "phenotype": "protein accumulation",
                "condition": "IL-2",
                "hit_status": "non_hit",
            },
        ],
    })

    assert compact["gene"] == "PGGT1B"
    assert compact["coverage_status"] == "covered"
    assert compact["row_count"] == 2
    assert compact["hit_count"] == 1
    assert compact["non_hit_count"] == 1
    assert compact["primary_tcell_row_count"] == 2
    assert compact["dataset_ids"] == ["763", "712"]
    assert compact["accepted"] is False
    assert compact["next"] == "human_signature_required"
    assert "rows" not in compact
