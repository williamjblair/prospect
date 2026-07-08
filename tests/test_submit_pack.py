"""Copy-safe submission packet CLI contract."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cli.submit_pack import build_packet


def test_submit_pack_includes_copy_safe_submission_fields():
    packet = build_packet()

    assert packet["project_title"] == "Prospect"
    assert packet["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert packet["repo_url"] == "https://github.com/williamjblair/prospect"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"
    assert "ANTHROPIC_API_KEY" not in json.dumps(packet)

    for command in [
        "./prospect verify",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
        "python tests/test_marson.py",
        "python examples/receipt_bridge_client.py --json",
        "python examples/claude_science_connector_client.py --json",
        "python examples/prospect_connector_client.py --case openresearch --json",
        "python examples/openresearch_receipt_client.py --json",
        "./prospect writeback --check",
    ]:
        assert command in packet["verification_commands"]

    for path in [
        "README.md",
        "docs/SUBMISSION.md",
        "docs/DEMO.md",
        "docs/FINDINGS.md",
        "docs/PROTOCOL.md",
        "docs/RECEIPT_BRIDGE.md",
        "docs/RECEIPT_SCHEMA.md",
        "docs/LAB_WRITEBACK_RECEIPT.md",
        "docs/JUDGE_HANDOUT.md",
    ]:
        assert path in packet["source_docs"]


def test_submit_pack_lists_the_consolidated_public_artifact_surface():
    packet = build_packet()
    expected = [
        "/data/frontier.json",
        "/data/finding_index.json",
        "/data/receipt_bridge/receipt_contract.json",
        "/data/receipt_bridge/receipt_manifest.json",
        "/data/receipt_bridge/receipt_bundle.json",
        "/data/claude_science_acceptance_demo.json",
        "/data/defended_discovery_endgame_preregistration.json",
        "/data/pggt1b_endgame_decision.json",
        "/data/defended_discovery_endgame_exhaustion.json",
        "/data/pggt1b_deep_dive.json",
        "/data/pggt1b_matrix_slice.json",
        "/data/agent_campaign.json",
        "/data/disease_genetics_overlay.json",
        "/data/lab_packet.json",
        "/data/lab_writeback_receipt.json",
    ]

    assert packet["public_artifacts"] == expected
    # No cut packet artifacts leak back in.
    for cut in ["judge_packet", "campaign_pressure", "substrate_replay", "release_manifest"]:
        assert not any(cut in artifact for artifact in packet["public_artifacts"])


def test_submit_pack_cli_prints_human_packet():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submit-pack"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "Prospect submission packet" in proc.stdout
    assert "Live URL: https://prospect-sepia-six.vercel.app" in proc.stdout
    assert "Signed root: root_a8b0dcdd4024e12f" in proc.stdout
    assert "./prospect verify" in proc.stdout
    assert "python benchmark/mutation_pack.py" in proc.stdout
    assert "Do not paste secrets." in proc.stdout


def test_submit_pack_cli_can_emit_json():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "submit-pack", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    packet = json.loads(proc.stdout)
    assert packet["project_title"] == "Prospect"
    assert packet["signed_root"] == "root_a8b0dcdd4024e12f"


if __name__ == "__main__":
    test_submit_pack_includes_copy_safe_submission_fields()
    test_submit_pack_lists_the_consolidated_public_artifact_surface()
    test_submit_pack_cli_prints_human_packet()
    test_submit_pack_cli_can_emit_json()
    print("PASS: submit pack")
