"""Optional browser QA command contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.browser_qa import build_plan, build_node_script


def test_browser_qa_plan_uses_rendered_qa_contract_without_entering_trust_path(tmp_path):
    plan = build_plan(targets=["production", "local"], out_dir=tmp_path)

    assert plan["title"] == "Prospect browser QA run"
    assert plan["status"] == "evidence_attached"
    assert plan["automation_claim"] == "browser_dom_smoke"
    assert plan["trust_boundary"]["model_in_trust_path"] == "no"
    assert plan["trust_boundary"]["accepted_state_mutations"] == 0
    assert plan["output_dir"] == str(tmp_path)
    assert plan["targets"] == [
        {"name": "production", "url": "https://prospect-sepia-six.vercel.app"},
        {"name": "local8124", "url": "http://localhost:8124"},
    ]
    assert plan["viewports"][0]["name"] == "desktop"
    assert plan["viewports"][1]["name"] == "mobile"

    tabs = {item["tab"]: item for item in plan["checks"]}
    assert tabs["Overview"]["texts"] == ["Opening claim checks", "48%", "Judge packet"]
    assert tabs["Findings"]["texts"] == ["Scannable findings index", "Substrate replay packet", "Cross-substrate discovery packet", "MED19"]
    assert tabs["Frontier"]["texts"] == ["Executable bridge path", "accepted=false", "human_signature_required"]
    assert tabs["Agent"]["texts"] == [
        "Campaign pressure summary",
        "Campaign challenger ledger",
        "Donor-condition replay packet",
        "Disease-genetics overlay packet",
        "Gladstone assay operations bundle",
        "Gladstone pilot design",
        "PGGT1B",
    ]
    assert "verified" not in json.dumps(plan).lower()
    assert "true" not in json.dumps(plan).lower()


def test_browser_qa_node_script_keeps_qa_output_local(tmp_path):
    plan = build_plan(targets=["production"], out_dir=tmp_path)
    script = build_node_script(plan)

    assert "output/playwright" not in script
    assert "prospect-browser-qa-results.json" in script
    assert "browser_dom_smoke" in script
    assert "button[data-sidebar=menu-button]" in script
    assert "button[data-sidebar=trigger]" in script
    assert "accepted_state_mutations" in script
    assert "release_manifest" not in script


def test_browser_qa_cli_dry_run_does_not_require_browser(tmp_path):
    proc = subprocess.run(
        [
            os.path.join(ROOT, "prospect"),
            "browser-qa",
            "--dry-run",
            "--target",
            "production",
            "--out-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "dry_run"
    assert payload["plan"]["targets"][0]["name"] == "production"
    assert payload["plan"]["trust_boundary"]["model_in_trust_path"] == "no"
    assert payload["command"][0] == "npx"
    assert not (tmp_path / "prospect-browser-qa-results.json").exists()


if __name__ == "__main__":
    test_browser_qa_plan_uses_rendered_qa_contract_without_entering_trust_path(Path("/tmp/prospect-browser-qa-plan-test"))
    test_browser_qa_node_script_keeps_qa_output_local(Path("/tmp/prospect-browser-qa-script-test"))
    test_browser_qa_cli_dry_run_does_not_require_browser(Path("/tmp/prospect-browser-qa-cli-test"))
    print("PASS: browser QA")
