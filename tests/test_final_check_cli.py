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
        "./prospect transfer-replay",
    ]:
        assert command in proc.stdout


if __name__ == "__main__":
    test_final_check_lists_submission_gate_commands()
    print("PASS: final-check CLI")
