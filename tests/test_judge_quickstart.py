"""Judge quickstart must compress the submission surface without changing claims."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.submit_pack import PUBLIC_ARTIFACTS, SOURCE_DOCS, build_packet

DOC = ROOT / "docs" / "JUDGE_QUICKSTART.md"
README = ROOT / "README.md"
SUBMISSION = ROOT / "docs" / "SUBMISSION.md"


def test_judge_quickstart_exists_and_points_to_core_evidence():
    text = DOC.read_text()

    for phrase in [
        "# Judge quickstart",
        "https://prospect-sepia-six.vercel.app",
        "https://github.com/williamjblair/prospect",
        "root_a8b0dcdd4024e12f",
        "A1BG",
        "48%",
        "64%",
        "PGGT1B",
        "No model in the trust path",
        "`computationally_reproduced`",
        "`evidence_attached`",
        "`contradicted`",
        "accepted=false",
        "human_signature_required",
        "not wet-lab or clinical truth",
    ]:
        assert phrase in text

    for command in [
        "./prospect final-check",
        "./prospect submit-smoke",
        "./prospect verify",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
        "python examples/receipt_bridge_client.py --json",
    ]:
        assert command in text

    for artifact in PUBLIC_ARTIFACTS:
        assert artifact in text


def test_judge_quickstart_is_in_submission_sources_and_entrypoints():
    packet = build_packet()
    readme = README.read_text()
    submission = SUBMISSION.read_text()

    assert "docs/JUDGE_QUICKSTART.md" in SOURCE_DOCS
    assert "docs/JUDGE_QUICKSTART.md" in packet["source_docs"]
    assert "docs/JUDGE_QUICKSTART.md" in readme
    assert "JUDGE_QUICKSTART.md" in submission


def test_judge_quickstart_names_durable_build_track_evidence():
    text = DOC.read_text()

    for phrase in [
        "## What outlasts the week",
        "a skeptical immunologist or computational biologist reading the Marson lab screen",
        "working software",
        "replayable CLI",
        "public data endpoints",
        "receipt bridge",
        "wet-lab handoff",
        "human signature",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_judge_quickstart_exists_and_points_to_core_evidence()
    test_judge_quickstart_is_in_submission_sources_and_entrypoints()
    test_judge_quickstart_names_durable_build_track_evidence()
    print("PASS: judge quickstart")
