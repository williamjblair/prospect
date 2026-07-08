"""Run the Prospect submission gate."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    "./prospect verify",
    "python benchmark/mutation_pack.py",
    "python tests/test_skill_parity.py",
    'for t in tests/test_*.py; do python "$t" || exit 1; done',
    "cd web && npm run build",
    "python tests/test_repo_hygiene.py",
    "git diff --check",
    "python examples/receipt_bridge_client.py --json",
    "./prospect submit-pack --json",
    "./prospect demo-pack --json",
    "./prospect campaign-pressure",
    "git diff --exit-code -- examples/data/campaign_pressure_summary.json docs/CAMPAIGN_PRESSURE_SUMMARY.md",
    "./prospect transfer-replay",
    "git diff --exit-code -- examples/data/transfer_replay_packet.json docs/TRANSFER_REPLAY_PACKET.md",
    "./prospect substrate-replay",
    "git diff --exit-code -- examples/data/substrate_replay_packet.json docs/SUBSTRATE_REPLAY_PACKET.md",
    "./prospect judge-pack",
    "cd web && python gen_data.py",
    "git diff --exit-code -- examples/data/judge_packet.json docs/JUDGE_PACKET.md web/public/data/frontier.json web/public/data/judge_packet.json web/public/data/campaign_pressure_summary.json web/public/data/substrate_replay_packet.json",
]


def _print_commands() -> None:
    print("Prospect final-check gate:", flush=True)
    for i, command in enumerate(COMMANDS, start=1):
        print(f"{i}. {command}", flush=True)


def run_gate() -> int:
    _print_commands()
    print("", flush=True)
    for command in COMMANDS:
        print(f"RUN {command}", flush=True)
        proc = subprocess.run(command, cwd=ROOT, shell=True)
        if proc.returncode != 0:
            print(f"FAIL {command}", flush=True)
            return proc.returncode
        print(f"PASS {command}", flush=True)
    print("", flush=True)
    print("FINAL CHECK PASS", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect final-check")
    parser.add_argument("--list", action="store_true", help="list the gate commands without running them")
    args = parser.parse_args(argv)

    if args.list:
        _print_commands()
        return 0
    return run_gate()
