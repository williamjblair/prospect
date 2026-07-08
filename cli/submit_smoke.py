"""Live production smoke checks for the final submission."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import urlopen

from cli.submit_pack import PUBLIC_ARTIFACTS

DEFAULT_BASE_URL = "https://prospect-sepia-six.vercel.app"
ROOT = "root_a8b0dcdd4024e12f"
REQUIRED_GATE_COMMANDS = [
    "./prospect final-check",
    "./prospect submit-smoke",
    "./prospect submit-pack",
    "./prospect demo-pack",
]


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class SmokeResult:
    base_url: str
    checks: list[Check]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _fetch_text(base_url: str, path: str, opener: Callable[..., Any], timeout: int) -> str:
    with opener(_url(base_url, path), timeout=timeout) as response:
        return response.read().decode("utf-8")


def _fetch_json(base_url: str, path: str, opener: Callable[..., Any], timeout: int) -> dict[str, Any]:
    return json.loads(_fetch_text(base_url, path, opener, timeout))


def _check_home(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        text = _fetch_text(base_url, "/", opener, timeout)
        ok = "Prospect" in text
        return Check("home page", ok, "contains Prospect" if ok else "home page missing Prospect")
    except Exception as exc:
        return Check("home page", False, f"fetch failed: {exc}")


def _check_judge(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/judge_packet.json", opener, timeout)
        failures = []
        if data.get("frontier_root") != ROOT:
            failures.append(f"frontier root {data.get('frontier_root')}")
        gate_commands = data.get("gate_commands", [])
        for command in REQUIRED_GATE_COMMANDS:
            if command not in gate_commands:
                failures.append(f"missing {command.removeprefix('./prospect ')} gate")
        public_data = data.get("public_data", [])
        if public_data != PUBLIC_ARTIFACTS:
            missing = [path for path in PUBLIC_ARTIFACTS if path not in public_data]
            extra = [path for path in public_data if path not in PUBLIC_ARTIFACTS]
            detail = "public data drift"
            if missing:
                detail += f", missing {missing[0]}"
            if extra:
                detail += f", extra {extra[0]}"
            failures.append(detail)
        if failures:
            return Check("judge packet", False, "; ".join(failures))
        return Check("judge packet", True, f"root {ROOT}")
    except Exception as exc:
        return Check("judge packet", False, f"fetch failed: {exc}")


def _check_public_artifacts(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    failures = []
    for path in PUBLIC_ARTIFACTS:
        try:
            _fetch_text(base_url, path, opener, timeout)
        except HTTPError as exc:
            if exc.code == 404:
                failures.append(f"missing {path}")
            else:
                failures.append(f"fetch failed {path}: HTTP {exc.code}")
        except Exception as exc:
            failures.append(f"fetch failed {path}: {exc}")

    if failures:
        detail = "; ".join(failures[:3])
        if len(failures) > 3:
            detail += f"; {len(failures) - 3} more"
        return Check("public artifacts", False, detail)
    return Check("public artifacts", True, f"{len(PUBLIC_ARTIFACTS)} public artifacts reachable")


def _check_campaign_gate(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/campaign_gate_probe.json", opener, timeout)
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and len(data.get("rows", [])) == 4
        )
        return Check("campaign gate probe", ok, "4 proposal-only rows" if ok else "campaign gate probe shape drift")
    except Exception as exc:
        return Check("campaign gate probe", False, f"fetch failed: {exc}")


def _check_transfer(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/transfer_replay_packet.json", opener, timeout)
        ok = (
            data.get("status") == "computationally_reproduced"
            and data.get("accepted_state_mutation") == "none"
            and data.get("counts", {}).get("t_cell_regulators_compared") == 377
        )
        return Check("transfer replay", ok, "377 reproduced transfer rows" if ok else "transfer replay shape drift")
    except Exception as exc:
        return Check("transfer replay", False, f"fetch failed: {exc}")


def _check_substrate(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/substrate_replay_packet.json", opener, timeout)
        ok = (
            data.get("status") == "computationally_reproduced"
            and data.get("accepted_state_mutation") == "none"
            and data.get("counts", {}).get("t_cell_regulators_compared") == 377
            and len(data.get("datasets", [])) == 3
        )
        return Check("substrate replay", ok, "377 reproduced rows across 3 substrates" if ok else "substrate replay shape drift")
    except Exception as exc:
        return Check("substrate replay", False, f"fetch failed: {exc}")


def _check_lab_packet(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/lab_packet.json", opener, timeout)
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and len(data.get("candidates", [])) == 5
        )
        return Check("lab packet", ok, "5 proposal-only assay rows" if ok else "lab packet shape drift")
    except Exception as exc:
        return Check("lab packet", False, f"fetch failed: {exc}")


def _check_receipt_manifest(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/receipt_bridge/receipt_manifest.json", opener, timeout)
        ok = (
            data.get("frontier_root") == ROOT
            and data.get("receipt_count") == 6
            and data.get("mcp_command") == "./prospect mcp"
        )
        return Check("receipt bridge manifest", ok, "6 receipts and MCP command" if ok else "receipt manifest shape drift")
    except Exception as exc:
        return Check("receipt bridge manifest", False, f"fetch failed: {exc}")


def run_checks(
    base_url: str = DEFAULT_BASE_URL,
    opener: Callable[..., Any] = urlopen,
    timeout: int = 20,
) -> SmokeResult:
    checks = [
        _check_home(base_url, opener, timeout),
        _check_judge(base_url, opener, timeout),
        _check_public_artifacts(base_url, opener, timeout),
        _check_campaign_gate(base_url, opener, timeout),
        _check_transfer(base_url, opener, timeout),
        _check_substrate(base_url, opener, timeout),
        _check_lab_packet(base_url, opener, timeout),
        _check_receipt_manifest(base_url, opener, timeout),
    ]
    return SmokeResult(base_url=base_url, checks=checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prospect submit-smoke",
        description="Run production submission smoke checks against the live Prospect site.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="site URL to check")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    args = parser.parse_args(argv)

    result = run_checks(args.base_url, timeout=args.timeout)
    print(f"Prospect production submission smoke: {result.base_url}", flush=True)
    for check in result.checks:
        mark = "PASS" if check.ok else "FAIL"
        print(f"{mark} {check.name}: {check.detail}", flush=True)
    if result.ok:
        print("SUBMIT SMOKE PASS", flush=True)
        return 0
    print("SUBMIT SMOKE FAIL", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
