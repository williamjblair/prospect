"""Live production smoke checks for the final submission."""
from __future__ import annotations

import argparse
import hashlib
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


def _fetch_bytes(base_url: str, path: str, opener: Callable[..., Any], timeout: int) -> bytes:
    with opener(_url(base_url, path), timeout=timeout) as response:
        return response.read()


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
        coverage = data.get("coverage", {})
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and len(data.get("rows", [])) == 11
            and coverage.get("coverage_status") == "complete"
            and coverage.get("returned_decisions") == 11
            and coverage.get("requested_limit") == 11
        )
        return Check(
            "campaign gate probe",
            ok,
            "11 proposal-only rows, complete gate coverage recorded" if ok else "campaign gate probe shape drift",
        )
    except Exception as exc:
        return Check("campaign gate probe", False, f"fetch failed: {exc}")


def _check_campaign_pressure(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/campaign_pressure_summary.json", opener, timeout)
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and data.get("accepted_state_mutations") == 0
            and data.get("counts", {}).get("claude_probe_rows") == 20
            and data.get("counts", {}).get("triage_rows") == 11
            and data.get("counts", {}).get("gate_probe_rows") == 11
            and data.get("gate_probe_coverage", {}).get("coverage_status") == "complete"
        )
        return Check("campaign pressure", ok, "20 probe rows summarized without accepted state" if ok else "campaign pressure shape drift")
    except Exception as exc:
        return Check("campaign pressure", False, f"fetch failed: {exc}")


def _check_campaign_probe_audit(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/campaign_probe_audit.json", opener, timeout)
        ok = (
            data.get("status") == "computationally_reproduced"
            and data.get("trust_boundary") == "frozen_audit_over_probe_artifact"
            and data.get("model_in_trust_path") == "no"
            and data.get("accepted_state_mutations") == 0
            and data.get("passed") == "yes"
            and data.get("issue_count") == 0
        )
        return Check("campaign probe audit", ok, "0 audit issues in committed probe" if ok else "campaign probe audit shape drift")
    except Exception as exc:
        return Check("campaign probe audit", False, f"fetch failed: {exc}")


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


def _check_cross_substrate_discovery(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/cross_substrate_discovery.json", opener, timeout)
        counts = data.get("class_counts", {})
        ok = (
            data.get("status") == "computationally_reproduced"
            and data.get("trust_boundary") == "frozen_counts_over_committed_tables"
            and data.get("accepted_state_mutation") == "none"
            and data.get("counts", {}).get("marson_genes_considered") == 11526
            and counts.get("shared_cellular_machinery") == 80
            and counts.get("t_cell_specific_activation") == 409
            and counts.get("non_immune_only_effect") == 333
            and len(data.get("campaign_intersections", [])) == 20
        )
        detail = "11526 genes classified across frozen substrates" if ok else "cross-substrate discovery shape drift"
        return Check("cross-substrate discovery", ok, detail)
    except Exception as exc:
        return Check("cross-substrate discovery", False, f"fetch failed: {exc}")


def _check_donor_condition_replay(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/donor_condition_replay.json", opener, timeout)
        counts = data.get("counts", {})
        ok = (
            data.get("status") == "computationally_reproduced"
            and data.get("trust_boundary") == "frozen_donor_rows_extracted_from_released_h5ad"
            and data.get("accepted_state_mutation") == "none"
            and counts.get("campaign_rows") == 20
            and counts.get("donor_supported") == 13
            and counts.get("donor_fragile") == 4
            and counts.get("guide_limited") == 1
            and len(data.get("rows", [])) == 20
        )
        detail = "20 campaign rows classified by donor replay" if ok else "donor-condition replay shape drift"
        return Check("donor-condition replay", ok, detail)
    except Exception as exc:
        return Check("donor-condition replay", False, f"fetch failed: {exc}")


def _check_disease_genetics_overlay(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/disease_genetics_overlay.json", opener, timeout)
        counts = data.get("counts", {})
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("local_perturbation_status") == "computationally_reproduced"
            and data.get("trust_boundary") == "frozen_external_association_extract"
            and data.get("accepted_state_mutation") == "none"
            and counts.get("campaign_rows") == 20
            and counts.get("immune_or_hematologic_context") == 10
            and counts.get("immune_or_hematologic_genetic_context") == 4
            and len(data.get("rows", [])) == 20
        )
        detail = "20 campaign rows overlaid with external disease context" if ok else "disease-genetics overlay shape drift"
        return Check("disease-genetics overlay", ok, detail)
    except Exception as exc:
        return Check("disease-genetics overlay", False, f"fetch failed: {exc}")


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


def _check_assay_operations(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/assay_operations_bundle.json", opener, timeout)
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and data.get("accepted_state_mutations") == 0
            and len(data.get("candidates", [])) == 5
        )
        return Check("assay operations", ok, "5 proposal-only operations rows" if ok else "assay operations shape drift")
    except Exception as exc:
        return Check("assay operations", False, f"fetch failed: {exc}")


def _check_gladstone_pilot_design(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/gladstone_pilot_design.json", opener, timeout)
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("trust_boundary") == "proposal_only"
            and data.get("accepted_state_mutations") == 0
            and data.get("model_in_trust_path") == "no"
            and data.get("sample_plan", {}).get("culture_arms") == 90
            and len(data.get("candidates", [])) == 5
        )
        detail = "90 culture arms across 5 proposal-only rows" if ok else "pilot design shape drift"
        return Check("Gladstone pilot design", ok, detail)
    except Exception as exc:
        return Check("Gladstone pilot design", False, f"fetch failed: {exc}")


def _check_final_submission_audit(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/final_submission_audit.json", opener, timeout)
        ok = (
            data.get("readiness") == "submission_ready_for_human_upload"
            and data.get("signed_root") == ROOT
            and data.get("public_artifact_count") == len(PUBLIC_ARTIFACTS)
            and "record_demo_video" in data.get("human_only_actions", [])
            and "submit_project_form" in data.get("human_only_actions", [])
        )
        detail = f"{len(PUBLIC_ARTIFACTS)} artifacts and human-only actions" if ok else "final audit shape drift"
        return Check("final submission audit", ok, detail)
    except Exception as exc:
        return Check("final submission audit", False, f"fetch failed: {exc}")


def _check_rendered_qa_packet(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        data = _fetch_json(base_url, "/data/rendered_qa_packet.json", opener, timeout)
        tabs = {item.get("tab"): item for item in data.get("tabs", [])}
        ok = (
            data.get("status") == "evidence_attached"
            and data.get("automation_claim") == "manual_browser_checklist"
            and data.get("production_url") == DEFAULT_BASE_URL
            and data.get("local_url") == "http://localhost:8124"
            and data.get("avoid_port") == 3000
            and "Overview" in tabs
            and "Campaign pressure summary" in tabs.get("Agent", {}).get("must_show", [])
        )
        return Check("rendered QA packet", ok, "manual browser checklist shape" if ok else "rendered QA packet shape drift")
    except Exception as exc:
        return Check("rendered QA packet", False, f"fetch failed: {exc}")


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


def _check_release_manifest(base_url: str, opener: Callable[..., Any], timeout: int) -> Check:
    try:
        manifest = _fetch_json(base_url, "/data/release_manifest.json", opener, timeout)
        failures = []
        if manifest.get("signed_root") != ROOT:
            failures.append(f"frontier root {manifest.get('signed_root')}")
        if manifest.get("hash_algorithm") != "sha256":
            failures.append("hash algorithm drift")
        if manifest.get("manifest_self_hash") != "excluded":
            failures.append("self hash policy drift")
        if manifest.get("public_artifacts") != PUBLIC_ARTIFACTS:
            failures.append("public artifact list drift")

        records = manifest.get("artifacts", [])
        by_path = {record.get("path"): record for record in records}
        expected_hashed = [path for path in PUBLIC_ARTIFACTS if path != "/data/release_manifest.json"]
        for path in expected_hashed:
            record = by_path.get(path)
            if not record:
                failures.append(f"missing hash {path}")
                continue
            payload = _fetch_bytes(base_url, path, opener, timeout)
            digest = hashlib.sha256(payload).hexdigest()
            size = len(payload)
            if record.get("sha256") != digest:
                failures.append(f"hash drift {path}")
            if record.get("bytes") != size:
                failures.append(f"byte drift {path}")
        extras = [path for path in by_path if path not in expected_hashed]
        if extras:
            failures.append(f"unexpected hash {extras[0]}")

        if failures:
            return Check("release manifest", False, "; ".join(failures[:3]))
        return Check("release manifest", True, f"{len(expected_hashed)} hashes match live artifacts")
    except Exception as exc:
        return Check("release manifest", False, f"fetch failed: {exc}")


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
        _check_campaign_pressure(base_url, opener, timeout),
        _check_campaign_probe_audit(base_url, opener, timeout),
        _check_transfer(base_url, opener, timeout),
        _check_substrate(base_url, opener, timeout),
        _check_cross_substrate_discovery(base_url, opener, timeout),
        _check_donor_condition_replay(base_url, opener, timeout),
        _check_disease_genetics_overlay(base_url, opener, timeout),
        _check_lab_packet(base_url, opener, timeout),
        _check_assay_operations(base_url, opener, timeout),
        _check_gladstone_pilot_design(base_url, opener, timeout),
        _check_final_submission_audit(base_url, opener, timeout),
        _check_rendered_qa_packet(base_url, opener, timeout),
        _check_receipt_manifest(base_url, opener, timeout),
        _check_release_manifest(base_url, opener, timeout),
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
