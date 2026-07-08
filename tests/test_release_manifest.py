"""Public release manifest contract."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.submit_pack import PUBLIC_ARTIFACTS
from frontier.release_manifest import build_manifest, write_manifest


def test_release_manifest_hashes_public_artifacts_without_self_reference():
    manifest = build_manifest()

    assert manifest["title"] == "Prospect public release manifest"
    assert manifest["live_url"] == "https://prospect-sepia-six.vercel.app"
    assert manifest["signed_root"] == "root_a8b0dcdd4024e12f"
    assert manifest["hash_algorithm"] == "sha256"
    assert manifest["trust_boundary"]["model_in_trust_path"] == "no"
    assert manifest["trust_boundary"]["accepted_state_mutations"] == 0
    assert manifest["manifest_self_hash"] == "excluded"
    assert manifest["public_artifact_count"] == len(PUBLIC_ARTIFACTS)

    by_path = {item["path"]: item for item in manifest["artifacts"]}
    assert "/data/release_manifest.json" in PUBLIC_ARTIFACTS
    assert "/data/release_manifest.json" not in by_path
    assert len(by_path) == len(PUBLIC_ARTIFACTS) - 1

    frontier = by_path["/data/frontier.json"]
    assert frontier["bytes"] > 1_000_000
    assert len(frontier["sha256"]) == 64
    assert frontier["source_path"] == "web/public/data/frontier.json"

    assert "verified" not in json.dumps(manifest).lower()
    assert "true" not in json.dumps(manifest).lower()


def test_release_manifest_writes_json_and_markdown(tmp_path):
    out_json = tmp_path / "release_manifest.json"
    out_doc = tmp_path / "RELEASE_MANIFEST.md"

    write_manifest(out_json=out_json, out_doc=out_doc)

    data = json.loads(out_json.read_text())
    doc = out_doc.read_text()
    assert data["hash_algorithm"] == "sha256"
    assert data["manifest_self_hash"] == "excluded"
    assert "/data/frontier.json" in doc
    assert "/data/release_manifest.json" in doc
    assert "No model in the trust path" in doc


def test_release_manifest_runs_from_prospect_cli():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "release-manifest"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert proc.returncode == 0, proc.stderr
    assert "release_manifest.json" in proc.stdout


if __name__ == "__main__":
    test_release_manifest_hashes_public_artifacts_without_self_reference()
    test_release_manifest_writes_json_and_markdown(Path("/tmp/prospect-release-manifest-test"))
    test_release_manifest_runs_from_prospect_cli()
    print("PASS: release manifest")
