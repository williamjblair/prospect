"""Final submitter checklist must point at the current submission surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "FINAL_SUBMISSION_CHECKLIST.md"


def test_final_submission_checklist_contains_human_submitter_steps():
    text = DOC.read_text()

    for phrase in [
        "Record the demo video",
        "Submit the project",
        "Final smoke",
        "https://prospect-sepia-six.vercel.app",
        "https://github.com/williamjblair/prospect",
        "docs/DEMO.md",
        "docs/SUBMISSION.md",
        "./prospect final-check",
        "/data/judge_packet.json",
        "/data/campaign_gate_probe.json",
        "root_a8b0dcdd4024e12f",
    ]:
        assert phrase in text


def test_final_submission_checklist_keeps_trust_boundary_language():
    text = DOC.read_text()

    for phrase in [
        "proposal only",
        "`evidence_attached`",
        "No model in the trust path",
        "human signing path",
        "accepted=false",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_final_submission_checklist_contains_human_submitter_steps()
    test_final_submission_checklist_keeps_trust_boundary_language()
    print("PASS: final submission checklist")
