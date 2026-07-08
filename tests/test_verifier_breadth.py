"""Verifier breadth and substrate routing contracts."""
from receipt.acceptance_service import build_submission_result
from receipt.causal_bridge import build_claude_science_packet
from frontier.substrate_coverage import build_packet


def _by_gene(verdicts):
    return {row["gene"]: row for row in verdicts}


def test_sade_feldman_signature_reports_contextual_coverage_drop():
    packet = build_claude_science_packet()
    coverage = packet["prospect"]["coverage_report"]

    assert coverage["primary_substrate"] == "marson_cd4_activation"
    assert coverage["routing_reason"] == "immunotherapy or T-cell claim routes first to the primary CD4+ perturbation substrate"
    assert coverage["before"]["not_assayed"] == 15
    assert coverage["after"]["not_assayed"] < coverage["before"]["not_assayed"]
    assert coverage["after"]["not_assayed"] == 5
    assert coverage["substrates"]["orcs_primary_tcell"]["covered_genes"] == 10
    assert coverage["substrates"]["orcs_primary_tcell"]["source_sha256"]

    tigit = _by_gene(packet["verdicts"])["TIGIT"]
    assert tigit["typed_status"] == "not_assayed"
    assert tigit["substrate_evidence"]["orcs_primary_tcell"]["coverage_status"] == "covered_orthogonal_tcell"
    assert tigit["substrate_evidence"]["orcs_primary_tcell"]["best_row"]["first_author"] == "Shifrut E (2018)"


def test_k562_context_routes_against_replogle_k562():
    result = build_submission_result(
        "MED19\nBCL10\nIL7R",
        filename="k562_markers.txt",
        source_name="external_k562_screen",
        claim_context="k562",
    )
    rows = _by_gene(result["verdicts"])

    assert result["prospect"]["route"]["primary_substrate"] == "replogle_k562"
    assert result["prospect"]["typed_status_counts"]["evidence_attached"] == 1
    assert result["prospect"]["typed_status_counts"]["associative_only"] == 1
    assert result["prospect"]["typed_status_counts"]["not_assayed"] == 1
    assert rows["MED19"]["typed_status"] == "evidence_attached"
    assert rows["MED19"]["primary_substrate"] == "replogle_k562"
    assert rows["MED19"]["magnitude"]["n_total_de_genes"] == 3716
    assert rows["BCL10"]["typed_status"] == "associative_only"
    assert rows["IL7R"]["typed_status"] == "not_assayed"


def test_tcell_verdicts_include_direction_magnitude_and_condition_specificity():
    result = build_submission_result("IL7R\nCCR7", filename="signature.txt", source_name="tcell_team")
    rows = _by_gene(result["verdicts"])
    il7r = rows["IL7R"]

    assert il7r["primary_substrate"] == "marson_cd4_activation"
    assert il7r["direction"]["strongest_condition"] == "Stim8hr"
    assert il7r["magnitude"]["n_total_de_genes"] == 812
    assert il7r["magnitude"]["n_up_genes"] >= 0
    assert il7r["condition_specificity"]["Stim8hr"]["n_total_de_genes"] == 812
    assert set(il7r["condition_specificity"]) == {"Rest", "Stim8hr", "Stim48hr"}


def test_substrate_coverage_packet_is_content_addressed():
    packet = build_packet()

    assert packet["accepted"] is False
    assert packet["next"] == "human_signature_required"
    assert packet["coverage"]["sade_feldman_signature"]["before"]["not_assayed"] == 15
    assert packet["coverage"]["sade_feldman_signature"]["after"]["not_assayed"] == 5
    assert packet["route_examples"]["k562"]["primary_substrate"] == "replogle_k562"
    assert packet["artifacts"]["orcs_primary_tcell"]["sha256"]
    assert packet["artifacts"]["marson_cd4_activation"]["sha256"]
