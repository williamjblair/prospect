"""Demo recording packet CLI contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cli.demo_pack import build_packet

DOC = Path(ROOT) / "docs" / "DEMO_TELEPROMPTER.md"
LONG_DOC = Path(ROOT) / "docs" / "DEMO.md"


def test_demo_pack_has_timed_recording_beats():
    packet = build_packet()

    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"
    assert "./prospect demo-pack" in packet["preflight"]
    assert "./prospect judge-handout" in packet["preflight"]
    assert "./prospect release-manifest" in packet["preflight"]
    assert "./prospect rendered-qa" in packet["preflight"]
    assert packet["optional_operator_commands"] == [
        "cd web && npm run start",
        "./prospect browser-qa --target both",
    ]
    assert [beat["time"] for beat in packet["beats"]] == ["0:00", "0:20", "0:40", "1:05", "1:30", "1:50"]

    script = "\n".join(beat["say"] for beat in packet["beats"])
    show = "\n".join(beat["show"] for beat in packet["beats"])
    for phrase in [
        "A model can assert this in a second",
        "48% were contradicted",
        "PD-1, TIM-3, CTLA-4, and IL-2 are outputs here",
        "The same claim runs through Marson and Replogle checkers",
        "Claude proposes, frozen code decides, and a human key accepts state",
        "Claude pressure became review work",
        "accepted=false",
        "PGGT1B remains evidence_attached",
        "operations bundle says what would promote",
        "90 proposal-only culture arms",
    ]:
        assert phrase in script
    assert "substrate replay packet" in show


def test_demo_pack_bans_overclaim_language():
    packet = build_packet()
    text = "\n".join(beat["say"] for beat in packet["beats"])

    for forbidden in [
        "verified biology",
        "wet-lab truth",
        "clinical truth",
        "accepted regulator",
        "Claude moves accepted state",
    ]:
        assert forbidden not in text


def test_demo_pack_cli_prints_and_emits_json():
    text_proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "demo-pack"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )
    assert text_proc.returncode == 0, text_proc.stderr
    assert "Prospect demo teleprompter" in text_proc.stdout
    assert "0:00 Refusal" in text_proc.stdout
    assert "./prospect browser-qa --target both" in text_proc.stdout
    assert "Do not say" in text_proc.stdout

    json_proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "demo-pack", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )
    assert json_proc.returncode == 0, json_proc.stderr
    packet = json.loads(json_proc.stdout)
    assert packet["beats"][0]["title"] == "Refusal"


def test_demo_teleprompter_doc_tracks_packet():
    text = DOC.read_text()

    for phrase in [
        "Prospect Demo Teleprompter",
        "./prospect demo-pack",
        "0:00, Refusal",
        "1:50, Close",
        "accepted=false",
        "human_signature_required",
        "campaign pressure summary",
        "assay operations bundle",
        "pilot design",
        "PGGT1B remains `evidence_attached`",
        "Do not claim wet-lab or clinical truth",
    ]:
        assert phrase in text

    preflight = text.split("## Preflight", 1)[1].split("## Script", 1)[0]
    for command in build_packet()["preflight"]:
        assert command in preflight
    for command in build_packet()["optional_operator_commands"]:
        assert command in preflight


def test_long_demo_doc_closes_on_current_artifact_surface():
    text = LONG_DOC.read_text()

    for phrase in [
        "assay operations bundle",
        "expected positive",
        "weakening",
        "reject",
        "campaign pressure summary",
        "Agent tab, campaign pressure summary",
        "twenty probed rows",
        "eleven more-aggressive",
        "all eleven gates returned",
        "substrate replay packet",
        "pilot design",
    ]:
        assert phrase in text
    assert "Back to Overview, the propose panel" not in text


if __name__ == "__main__":
    test_demo_pack_has_timed_recording_beats()
    test_demo_pack_bans_overclaim_language()
    test_demo_pack_cli_prints_and_emits_json()
    test_demo_teleprompter_doc_tracks_packet()
    test_long_demo_doc_closes_on_current_artifact_surface()
    print("PASS: demo pack")
