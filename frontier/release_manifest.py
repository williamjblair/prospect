"""Build a public hash manifest for the deployed data surface."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cli.submit_pack import LIVE_URL, PUBLIC_ARTIFACTS, REPO_URL, SIGNED_ROOT

ROOT = Path(__file__).resolve().parents[1]
WEB_PUBLIC = ROOT / "web" / "public"
OUT_JSON = ROOT / "examples" / "data" / "release_manifest.json"
OUT_WEB = WEB_PUBLIC / "data" / "release_manifest.json"
OUT_DOC = ROOT / "docs" / "RELEASE_MANIFEST.md"
SELF_PATH = "/data/release_manifest.json"


def _public_path(path: str) -> Path:
    if not path.startswith("/"):
        raise ValueError(f"public artifact path must start with /: {path}")
    return WEB_PUBLIC / path.removeprefix("/")


def _artifact_record(path: str) -> dict[str, Any]:
    source = _public_path(path)
    if not source.exists():
        raise FileNotFoundError(f"missing public artifact: {source}")
    payload = source.read_bytes()
    return {
        "path": path,
        "source_path": str(source.relative_to(ROOT)),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def build_manifest() -> dict[str, Any]:
    artifacts = [_artifact_record(path) for path in PUBLIC_ARTIFACTS if path != SELF_PATH]
    return {
        "title": "Prospect public release manifest",
        "live_url": LIVE_URL,
        "repo_url": REPO_URL,
        "signed_root": SIGNED_ROOT,
        "hash_algorithm": "sha256",
        "manifest_self_hash": "excluded",
        "public_artifact_count": len(PUBLIC_ARTIFACTS),
        "hashed_artifact_count": len(artifacts),
        "public_artifacts": PUBLIC_ARTIFACTS,
        "artifacts": artifacts,
        "trust_boundary": {
            "model_role": "propose_search_pressure_test",
            "model_in_trust_path": "no",
            "accepted_state_gate": "frozen_replay_plus_human_ed25519_signature",
            "accepted_state_mutations": 0,
        },
        "rebuild": "./prospect release-manifest",
        "limitation": "Hashes prove deployed byte identity, not wet-lab or clinical truth.",
    }


def _markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Prospect public release manifest",
        "",
        f"Live: [{manifest['live_url']}]({manifest['live_url']})",
        "",
        f"Repo: [{manifest['repo_url']}]({manifest['repo_url']})",
        "",
        f"Signed root: `{manifest['signed_root']}`",
        "",
        "## No model in the trust path",
        "",
        "This manifest hashes the public data artifacts served by the app. It does not move accepted state. The signed frontier root is still gated by frozen replay and a human Ed25519 key.",
        "",
        "## Hash scope",
        "",
        f"- Hash algorithm: `{manifest['hash_algorithm']}`",
        f"- Public artifacts: {manifest['public_artifact_count']}",
        f"- Hashed artifacts: {manifest['hashed_artifact_count']}",
        f"- Manifest self hash: `{manifest['manifest_self_hash']}`",
        "",
        "## Public artifact hashes",
        "",
        "| path | bytes | sha256 |",
        "|---|---:|---|",
    ]
    for item in manifest["artifacts"]:
        lines.append(f"| `{item['path']}` | {item['bytes']} | `{item['sha256']}` |")
    lines += [
        f"| `{SELF_PATH}` | n/a | `self_hash_excluded` |",
        "",
        manifest["limitation"],
        "",
        "Rebuild:",
        "",
        "```bash",
        manifest["rebuild"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_manifest(
    out_json: Path = OUT_JSON,
    out_doc: Path = OUT_DOC,
    out_web: Path | None = None,
) -> dict[str, Any]:
    manifest = build_manifest()
    payload = json.dumps(manifest, indent=2) + "\n"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_doc.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(payload)
    out_doc.write_text(_markdown(manifest))
    if out_web is not None:
        out_web.parent.mkdir(parents=True, exist_ok=True)
        out_web.write_text(payload)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect release-manifest")
    parser.add_argument("--json", action="store_true", help="print the manifest as JSON")
    args = parser.parse_args(argv)

    manifest = write_manifest(out_web=OUT_WEB)
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_WEB}")
    print(f"wrote {OUT_DOC}")
    print(f"hashed {manifest['hashed_artifact_count']} public artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
