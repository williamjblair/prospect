"""Final submission gate CLI contract."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_final_check_lists_submission_gate_commands():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "final-check", "--list"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    for command in [
        "./prospect verify",
        "python benchmark/mutation_pack.py",
        "python tests/test_skill_parity.py",
        "for t in tests/test_*.py; do python \"$t\" || exit 1; done",
        "cd web && npm run build",
        "python tests/test_repo_hygiene.py",
        "git diff --check",
        "python examples/receipt_bridge_client.py --json",
        "./prospect submit-pack --json",
        "./prospect demo-pack --json",
        "./prospect judge-handout",
        "git diff --exit-code -- docs/JUDGE_HANDOUT.md",
        "./prospect rendered-qa",
        "git diff --exit-code -- examples/data/rendered_qa_packet.json docs/RENDERED_QA_PACKET.md",
        "./prospect submission-audit",
        "git diff --exit-code -- examples/data/final_submission_audit.json docs/FINAL_SUBMISSION_AUDIT.md",
        "./prospect campaign-pressure",
        "git diff --exit-code -- examples/data/campaign_pressure_summary.json docs/CAMPAIGN_PRESSURE_SUMMARY.md",
        "./prospect assay-ops",
        "git diff --exit-code -- examples/data/assay_operations_bundle.json examples/data/assay_operations_bundle.csv docs/ASSAY_OPERATIONS_BUNDLE.md",
        "./prospect transfer-replay",
        "git diff --exit-code -- examples/data/transfer_replay_packet.json docs/TRANSFER_REPLAY_PACKET.md",
        "./prospect substrate-replay",
        "git diff --exit-code -- examples/data/substrate_replay_packet.json docs/SUBSTRATE_REPLAY_PACKET.md",
        "./prospect judge-pack",
        "cd web && python gen_data.py",
        "./prospect release-manifest",
        "git diff --exit-code -- examples/data/judge_packet.json docs/JUDGE_PACKET.md examples/data/release_manifest.json docs/RELEASE_MANIFEST.md web/public/data/frontier.json web/public/data/judge_packet.json web/public/data/campaign_agent_probe.json web/public/data/campaign_pressure_summary.json web/public/data/assay_operations_bundle.json web/public/data/final_submission_audit.json web/public/data/substrate_replay_packet.json web/public/data/release_manifest.json web/public/data/rendered_qa_packet.json",
    ]:
        assert command in proc.stdout


if __name__ == "__main__":
    test_final_check_lists_submission_gate_commands()
    print("PASS: final-check CLI")
