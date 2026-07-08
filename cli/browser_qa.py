"""Run optional Playwright browser QA for the final judge path."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cli.rendered_qa import LOCAL_URL, build_packet

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "playwright"
RESULTS_NAME = "prospect-browser-qa-results.json"

TARGETS = {
    "production": "production",
    "local": "local8124",
}


def _target_url(name: str, packet: dict[str, Any]) -> dict[str, str]:
    if name == "production":
        return {"name": "production", "url": packet["production_url"]}
    if name == "local":
        return {"name": "local8124", "url": LOCAL_URL}
    raise ValueError(f"unknown browser QA target: {name}")


def build_plan(targets: list[str], out_dir: Path = OUT_DIR) -> dict[str, Any]:
    packet = build_packet()
    return {
        "title": "Prospect browser QA run",
        "status": "evidence_attached",
        "automation_claim": "browser_dom_smoke",
        "output_dir": str(out_dir),
        "results_file": str(out_dir / RESULTS_NAME),
        "targets": [_target_url(name, packet) for name in targets],
        "viewports": packet["viewports"],
        "checks": [{"tab": item["tab"], "texts": item["must_show"]} for item in packet["tabs"]],
        "trust_boundary": {
            "model_role": "none",
            "model_in_trust_path": "no",
            "accepted_state_mutations": 0,
        },
        "limitation": (
            "Browser QA proves the rendered judge path loaded expected text. "
            "It does not alter signed state and does not prove wet-lab or clinical truth."
        ),
    }


def build_node_script(plan: dict[str, Any]) -> str:
    plan_json = json.dumps(plan, indent=2)
    return f"""
const path = require("path");
const fs = require("fs");

const bin = process.env.PATH.split(":").find((entry) =>
  entry.includes("/_npx/") && entry.endsWith("node_modules/.bin")
);
if (!bin) {{
  throw new Error("could not locate npx temporary node_modules/.bin path");
}}
const {{ chromium }} = require(path.join(bin, "..", "playwright"));

const plan = {plan_json};
const outDir = plan.output_dir;
const resultsFile = path.join(outDir, "{RESULTS_NAME}");

function safeName(value) {{
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}}

async function switchTab(page, label, mobileNav) {{
  if (mobileNav) {{
    await page.locator("button[data-sidebar=trigger]").click({{ timeout: 10000 }});
    await page.locator("button[data-sidebar=menu-button]").filter({{ hasText: label }}).click({{ timeout: 10000 }});
    await page.keyboard.press("Escape");
  }} else {{
    await page.locator("button[data-sidebar=menu-button]").filter({{ hasText: label }}).click({{ timeout: 10000 }});
  }}
  await page.waitForTimeout(350);
}}

(async () => {{
  fs.mkdirSync(outDir, {{ recursive: true }});
  const browser = await chromium.launch({{ headless: true }});
  const results = [];
  try {{
    for (const target of plan.targets) {{
      for (const viewport of plan.viewports) {{
        const page = await browser.newPage({{ viewport: {{ width: viewport.width, height: viewport.height }} }});
        await page.goto(target.url, {{ waitUntil: "networkidle", timeout: 60000 }});
        await page.waitForTimeout(1000);
        for (const check of plan.checks) {{
          await switchTab(page, check.tab, viewport.name === "mobile");
          const bodyText = (await page.locator("body").innerText({{ timeout: 10000 }})).toLowerCase();
          for (const expectedText of check.texts) {{
            if (!bodyText.includes(expectedText.toLowerCase())) {{
              throw new Error(`${{target.name}} ${{viewport.name}} ${{check.tab}} missing ${{expectedText}}`);
            }}
          }}
          const screenshot = path.join(
            outDir,
            `prospect-${{safeName(target.name)}}-${{safeName(viewport.name)}}-${{safeName(check.tab)}}.png`
          );
          await page.screenshot({{ path: screenshot, fullPage: false }});
          results.push({{
            target: target.name,
            viewport: viewport.name,
            tab: check.tab,
            screenshot,
            checks: check.texts,
          }});
        }}
        await page.close();
      }}
    }}
  }} finally {{
    await browser.close();
  }}
  const payload = {{
    title: plan.title,
    status: "pass",
    automation_claim: plan.automation_claim,
    trust_boundary: plan.trust_boundary,
    results,
  }};
  fs.writeFileSync(resultsFile, JSON.stringify(payload, null, 2) + "\\n");
  console.log(`browser QA PASS: ${{results.length}} tab-view checks`);
  console.log(`wrote ${{resultsFile}}`);
}})().catch((error) => {{
  console.error(error.stack || error.message);
  process.exit(1);
}});
""".strip() + "\n"


def _npx_command(script_path: Path) -> list[str]:
    return ["npx", "--yes", "--package=playwright", "--", "node", str(script_path)]


def run_browser_qa(plan: dict[str, Any]) -> int:
    if not shutil.which("npx"):
        print("FAIL: npx is required for browser QA", flush=True)
        return 2

    out_dir = Path(plan["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
        script_path = Path(handle.name)
        handle.write(build_node_script(plan))
    try:
        proc = subprocess.run(_npx_command(script_path), cwd=ROOT)
        return proc.returncode
    finally:
        script_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect browser-qa")
    parser.add_argument(
        "--target",
        choices=["production", "local", "both"],
        default="production",
        help="which rendered surface to check; local uses http://localhost:8124",
    )
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR, help="directory for local QA evidence")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and npx command without running a browser")
    args = parser.parse_args(argv)

    targets = ["production", "local"] if args.target == "both" else [args.target]
    plan = build_plan(targets=targets, out_dir=args.out_dir)
    if args.dry_run:
        with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
            command = _npx_command(Path(handle.name))
        Path(command[-1]).unlink(missing_ok=True)
        print(json.dumps({"status": "dry_run", "command": command, "plan": plan}, indent=2, sort_keys=True))
        return 0
    return run_browser_qa(plan)


if __name__ == "__main__":
    raise SystemExit(main())
