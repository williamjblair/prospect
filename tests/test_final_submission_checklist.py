"""Final submitter checklist must point at the current submission surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "FINAL_SUBMISSION_CHECKLIST.md"
RUNBOOK = ROOT / "docs" / "DEMO_RECORDING_RUNBOOK.md"
FORM = ROOT / "docs" / "SUBMISSION_FORM_PACKET.md"


def test_final_submission_checklist_contains_human_submitter_steps():
    text = DOC.read_text()

    for phrase in [
        "Record the demo video",
        "Submit the project",
        "Final smoke",
        "https://prospect-sepia-six.vercel.app",
        "https://github.com/williamjblair/prospect",
        "docs/DEMO.md",
        "docs/DEMO_RECORDING_RUNBOOK.md",
        "docs/SUBMISSION_FORM_PACKET.md",
        "docs/SUBMISSION.md",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
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


def test_demo_recording_runbook_is_submission_ready():
    text = RUNBOOK.read_text()

    for phrase in [
        "http://localhost:8124",
        "https://prospect-sepia-six.vercel.app",
        "./prospect final-check",
        "python examples/receipt_bridge_client.py --json",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "0:00",
        "0:20",
        "0:40",
        "1:05",
        "1:30",
        "1:50",
        "accepted=false",
        "human_signature_required",
        "`evidence_attached`",
        "Do not claim wet-lab or clinical truth",
    ]:
        assert phrase in text


def test_submission_form_packet_has_copy_paste_fields():
    text = FORM.read_text()

    for phrase in [
        "Project title",
        "Prospect",
        "Short description",
        "Long description",
        "Live URL",
        "Repo URL",
        "Demo video",
        "https://prospect-sepia-six.vercel.app",
        "https://github.com/williamjblair/prospect",
        "root_a8b0dcdd4024e12f",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "python examples/receipt_bridge_client.py --json",
        "No model in the trust path",
        "`computationally_reproduced`",
        "`evidence_attached`",
        "`contradicted`",
        "Do not claim wet-lab or clinical truth",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_final_submission_checklist_contains_human_submitter_steps()
    test_final_submission_checklist_keeps_trust_boundary_language()
    test_demo_recording_runbook_is_submission_ready()
    test_submission_form_packet_has_copy_paste_fields()
    print("PASS: final submission checklist")
