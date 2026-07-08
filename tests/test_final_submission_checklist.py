"""Final submitter checklist must point at the current submission surface."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.submit_pack import PUBLIC_ARTIFACTS

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
        "docs/DEMO_TELEPROMPTER.md",
        "docs/JUDGE_QUICKSTART.md",
        "docs/SUBMISSION_FORM_PACKET.md",
        "docs/SUBMISSION.md",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect rendered-qa",
        "./prospect browser-qa --target both",
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
        "./prospect demo-pack",
        "./prospect judge-handout",
        "./prospect rendered-qa",
        "./prospect browser-qa --target both",
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
        "JUDGE_QUICKSTART.md",
        "https://prospect-sepia-six.vercel.app",
        "https://github.com/williamjblair/prospect",
        "root_a8b0dcdd4024e12f",
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect submit-pack",
        "./prospect demo-pack",
        "./prospect rendered-qa",
        "./prospect browser-qa --target both",
        "python examples/receipt_bridge_client.py --json",
        "No model in the trust path",
        "`computationally_reproduced`",
        "`evidence_attached`",
        "`contradicted`",
        "Do not claim wet-lab or clinical truth",
        "What outlasts the week",
        "working software",
        "replayable CLI",
        "public data endpoints",
        "receipt bridge",
        "wet-lab handoff",
    ]:
        assert phrase in text

    for artifact in PUBLIC_ARTIFACTS:
        assert artifact in text


if __name__ == "__main__":
    test_final_submission_checklist_contains_human_submitter_steps()
    test_final_submission_checklist_keeps_trust_boundary_language()
    test_demo_recording_runbook_is_submission_ready()
    test_submission_form_packet_has_copy_paste_fields()
    print("PASS: final submission checklist")
