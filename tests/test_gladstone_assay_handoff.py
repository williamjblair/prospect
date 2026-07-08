"""Gladstone assay handoff must stay lab-ready and proposal-only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "GLADSTONE_ASSAY_HANDOFF.md"


def test_gladstone_assay_handoff_names_all_lab_packet_candidates():
    text = DOC.read_text()
    compact = " ".join(text.split())

    for gene in ["PGGT1B", "RCC1L", "MCAT", "CCDC22", "CYB5RL"]:
        assert gene in text
    assert "RWDD2B is removed from primary assay capacity" in compact


def test_gladstone_assay_handoff_keeps_boundary_and_controls():
    text = DOC.read_text()

    for phrase in [
        "proposal only",
        "`evidence_attached`",
        "orthogonal knockdown",
        "non-targeting guide",
        "safe-harbor guide",
        "unstimulated matched culture",
        "activation-marker flow cytometry",
        "targeted RNA-seq",
        "/data/lab_packet.json",
        "/data/campaign_challenger_ledger.json",
        "/data/judge_packet.json",
        "human signing path",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_gladstone_assay_handoff_names_all_lab_packet_candidates()
    test_gladstone_assay_handoff_keeps_boundary_and_controls()
    print("PASS: Gladstone assay handoff")
