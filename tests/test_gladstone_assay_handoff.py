"""Gladstone assay handoff must stay lab-ready and proposal-only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "GLADSTONE_ASSAY_HANDOFF.md"


def test_gladstone_assay_handoff_names_all_lab_packet_candidates():
    text = DOC.read_text()

    for gene in ["PGGT1B", "RCC1L", "MCAT", "RWDD2B", "CCDC22"]:
        assert gene in text


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
        "/data/judge_packet.json",
        "human signing path",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_gladstone_assay_handoff_names_all_lab_packet_candidates()
    test_gladstone_assay_handoff_keeps_boundary_and_controls()
    print("PASS: Gladstone assay handoff")
