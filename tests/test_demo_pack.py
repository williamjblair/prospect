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


def test_demo_pack_has_timed_recording_beats():
    packet = build_packet()

    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"
    assert [beat["time"] for beat in packet["beats"]] == ["0:00", "0:20", "0:40", "1:05", "1:30", "1:50"]

    script = "\n".join(beat["say"] for beat in packet["beats"])
    for phrase in [
        "A model can assert this in a second",
        "48% were contradicted",
        "PD-1, TIM-3, CTLA-4, and IL-2 are outputs here",
        "The same claim runs through Marson and Replogle checkers",
        "Claude proposes, frozen code decides, and a human key accepts state",
        "accepted=false",
        "PGGT1B remains evidence_attached",
    ]:
        assert phrase in script


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
        "PGGT1B remains `evidence_attached`",
        "Do not claim wet-lab or clinical truth",
    ]:
        assert phrase in text


if __name__ == "__main__":
    test_demo_pack_has_timed_recording_beats()
    test_demo_pack_bans_overclaim_language()
    test_demo_pack_cli_prints_and_emits_json()
    test_demo_teleprompter_doc_tracks_packet()
    print("PASS: demo pack")
