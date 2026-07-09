"""Deploy readiness helper contracts."""
import http.client
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.deploy_readiness import build_checklist


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get(port: int, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    res = conn.getresponse()
    text = res.read().decode()
    headers = dict(res.getheaders())
    conn.close()
    return res.status, headers, text


def _options(port: int, path: str, *, origin: str = ""):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {"Origin": origin} if origin else {}
    conn.request("OPTIONS", path, headers=headers)
    res = conn.getresponse()
    text = res.read().decode()
    headers = dict(res.getheaders())
    conn.close()
    return res.status, headers, text


def _wait_ready(port: int) -> None:
    for _ in range(40):
        try:
            status, _, _ = _get(port, "/health")
            if status == 200:
                return
        except OSError:
            time.sleep(0.1)
    raise AssertionError("service did not become ready")


def test_deploy_checklist_lists_non_deploying_gate_and_will_commands():
    checklist = build_checklist()

    assert checklist["prepare_command"] == "./scripts/prepare_deploy.sh"
    assert "./prospect verify" in checklist["local_gate"]
    assert "python -m pytest tests/ -q" in checklist["local_gate"]
    assert "cd web && npm run typecheck" in checklist["local_gate"]
    assert "cd web && npm run build" in checklist["local_gate"]
    assert "docker build -f Dockerfile.acceptance -t prospect-acceptance:local ." in checklist["local_gate"]
    assert "fly deploy --config fly.acceptance.toml" in checklist["deploy_commands_for_will"]
    assert checklist["web_env"]["NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL"]
    assert checklist["signed_frontier_policy"]["mutation_allowed"] is False
    assert checklist["signed_frontier_policy"]["root"] == "root_a8b0dcdd4024e12f"
    assert "vercel --prod" in " ".join(checklist["do_not_run_here"])
    script = (ROOT / "scripts" / "prepare_deploy.sh").read_text()
    assert "python frontier/build.py" not in script
    assert 'SIGNED_STATE_BEFORE="$(state_digest)"' in script
    assert 'SIGNED_STATE_AFTER="$(state_digest)"' in script
    assert "python -m pytest tests/ -q" in script
    assert "npm run typecheck" in script
    assert "cd web && npm run build" in script
    assert "docker build -f Dockerfile.acceptance -t prospect-acceptance:local ." in script
    assert "NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL" in script
    assert "fly deploy --config fly.acceptance.toml" in script


def test_deploy_checklist_cli_emits_json():
    proc = subprocess.run(
        [str(ROOT / "prospect"), "deploy-checklist", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["title"] == "Prospect deploy readiness checklist"
    assert payload["post_deploy_smoke"].startswith("./prospect post-deploy-smoke")


def test_acceptance_service_cors_and_post_deploy_smoke(tmp_path):
    port = _free_port()
    proc = subprocess.Popen(
        [
            str(ROOT / "prospect"),
            "serve-acceptance",
            "--port",
            str(port),
            "--data-dir",
            str(tmp_path),
            "--cors-origin",
            "https://prospect.example",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_ready(port)
        status, headers, _ = _options(port, "/submit", origin="https://prospect.example")
        assert status == 204
        assert headers["access-control-allow-origin"] == "https://prospect.example"
        assert "POST" in headers["access-control-allow-methods"]

        smoke = subprocess.run(
            [
                str(ROOT / "prospect"),
                "post-deploy-smoke",
                "--base-url",
                f"http://127.0.0.1:{port}",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        assert smoke.returncode == 0, smoke.stderr
        payload = json.loads(smoke.stdout)
        assert payload["accepted"] is False
        assert payload["next"] == "human_signature_required"
        assert payload["proposal_status"] == 200
        assert payload["proposal_json_status"] == 200
        assert payload["second_proposal_status"] == 200
        assert payload["ledger_status"] == 200
        assert payload["typed_status_counts"]["drivers"] == 1
        assert payload["proposal_page_has_replay"] is True
        assert payload["receipt_id_matches"] is True
        assert payload["verdicts_reproduced"] is True
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_web_submitter_exposes_public_service_env_hook():
    page = (ROOT / "web" / "app" / "page.tsx").read_text()
    assert "NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL" in page
    assert "Hosted service" in page
    assert "/ledger" in page


if __name__ == "__main__":
    test_deploy_checklist_lists_non_deploying_gate_and_will_commands()
    test_deploy_checklist_cli_emits_json()
    test_web_submitter_exposes_public_service_env_hook()
    print("PASS: deploy readiness")
