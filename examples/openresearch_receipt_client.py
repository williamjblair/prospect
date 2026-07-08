#!/usr/bin/env python3
"""Submit an external auto-research result as a Prospect receipt proposal.

The input bundle shape is intentionally generic: claim text, artifact hashes,
lineage, and replay command. This demo uses a biology-shaped Perturb-seq claim
that Prospect's Marson checker can re-derive, then submits it through the MCP
receipt bridge. The bridge returns a proposal only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data" / "marson_de_demo_slice.csv"
FRONTIER_SIG = ROOT / "frontier" / "frontier.sig.json"

sys.path.insert(0, str(ROOT))

from engine.checkers.marson_perturbseq import MarsonPerturbseqChecker
from engine.schema import Claim
from receipt.schema import Artifact, EvidenceAtom, Receipt, Verifier

COMMAND = "python examples/openresearch_receipt_client.py --json"
PRODUCER = "external_auto_research"
LINEAGE_ID = "external-run-marson-vav1-stim48hr-v0"
VERIFIER_REPLAY = "python tests/test_marson.py"
HUMAN_ACCEPTANCE_REQUIRES = [
    "frozen_replay_passes",
    "reviewer_accepts_state_delta",
    "human_ed25519_signature",
]


class McpClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [str(ROOT / "prospect"), "mcp"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._next_id = 1

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("MCP process pipes are unavailable")
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params or {},
        }
        self._next_id += 1
        self.proc.stdin.write(json.dumps(req, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError("MCP server closed without a response: " + stderr.strip())
        res = json.loads(line)
        if "error" in res:
            raise RuntimeError(res["error"]["message"])
        return res["result"]

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _frontier_root() -> str:
    if not FRONTIER_SIG.exists():
        return ""
    return json.loads(FRONTIER_SIG.read_text()).get("root", "")


def build_external_result_bundle() -> dict[str, Any]:
    claim = Claim(
        "VAV1 is a major regulator of the stimulated CD4 T-cell transcriptome.",
        gene="VAV1",
        condition="Stim48hr",
        asserts_major=True,
    )
    verdict = MarsonPerturbseqChecker(str(DATA)).check(claim)
    if verdict.status != "supported":
        raise RuntimeError(f"external result no longer re-derives: {verdict.status}")
    return {
        "producer": PRODUCER,
        "domain": "biology",
        "lineage_id": LINEAGE_ID,
        "claim": claim.text,
        "subject": [claim.gene],
        "conditions": [claim.condition],
        "artifact_hashes": [
            {
                "name": DATA.name,
                "sha256": _sha256(DATA),
                "locator": str(DATA.relative_to(ROOT)),
            }
        ],
        "verifier_replay": VERIFIER_REPLAY,
        "engine_verdict": verdict.status,
        "verdict_reason": verdict.reason,
        "evidence": verdict.evidence,
    }


def receipt_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    evidence = [
        EvidenceAtom(
            fact="Marson checker verdict",
            value=bundle["engine_verdict"],
            source="engine.checkers.marson_perturbseq",
        ),
        EvidenceAtom(
            fact="VAV1 Stim48hr released DE genes",
            value=str(bundle["evidence"]["Stim48hr"]["n_total_de_genes"]),
            source="examples/data/marson_de_demo_slice.csv",
        ),
        EvidenceAtom(
            fact="VAV1 Stim48hr on-target category",
            value=bundle["evidence"]["Stim48hr"]["ontarget_effect_category"],
            source="examples/data/marson_de_demo_slice.csv",
        ),
    ]
    receipt = Receipt(
        frontier="prospect_marson_cd4_perturbseq",
        claim=bundle["claim"],
        kind="external_reproduction",
        subject=bundle["subject"],
        producer={
            "kind": PRODUCER,
            "run": bundle["lineage_id"],
            "domain": bundle["domain"],
        },
        artifacts=[Artifact(**artifact) for artifact in bundle["artifact_hashes"]],
        evidence=evidence,
        verifier=Verifier(
            name="MarsonPerturbseqChecker",
            method="frozen lookup over released Marson DE table",
            replay=bundle["verifier_replay"],
        ),
        status="computationally_reproduced",
        replayability="exact",
        scope=bundle["conditions"],
    ).freeze()
    return receipt.to_dict()


def preview() -> dict[str, Any]:
    bundle = build_external_result_bundle()
    receipt = receipt_from_bundle(bundle)
    return {
        "command": COMMAND,
        "producer": PRODUCER,
        "domain": bundle["domain"],
        "lineage_id": bundle["lineage_id"],
        "claim": bundle["claim"],
        "frontier_root": _frontier_root(),
        "typed_status": receipt["status"],
        "engine_verdict": bundle["engine_verdict"],
        "receipt_id": receipt["receipt_id"],
        "accepted": False,
        "next": "human_signature_required",
        "verifier_replay": bundle["verifier_replay"],
        "human_acceptance_requires": HUMAN_ACCEPTANCE_REQUIRES,
    }


def run() -> dict[str, Any]:
    bundle = build_external_result_bundle()
    receipt = receipt_from_bundle(bundle)
    client = McpClient()
    try:
        init = client.call("initialize")
        schema = client.call(
            "tools/call",
            {"name": "prospect.receipt.schema", "arguments": {}},
        )["structuredContent"]
        validate = client.call(
            "tools/call",
            {"name": "prospect.receipt.validate", "arguments": {"receipt": receipt}},
        )["structuredContent"]
        submit = client.call(
            "tools/call",
            {"name": "prospect.receipt.submit", "arguments": {"receipt": receipt}},
        )["structuredContent"]
    finally:
        client.close()

    return {
        "server": init["serverInfo"]["name"],
        "producer": PRODUCER,
        "domain": bundle["domain"],
        "lineage_id": bundle["lineage_id"],
        "frontier_root": schema["manifest"]["frontier_root"],
        "claim": bundle["claim"],
        "typed_status": receipt["status"],
        "engine_verdict": bundle["engine_verdict"],
        "verifier_replay": bundle["verifier_replay"],
        "receipt_id": receipt["receipt_id"],
        "valid": validate["valid"],
        "errors": validate["errors"],
        "accepted": submit["accepted"],
        "next": submit.get("next", ""),
        "proposal_id": submit.get("proposal_id", ""),
        "human_acceptance_requires": HUMAN_ACCEPTANCE_REQUIRES,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="examples/openresearch_receipt_client.py")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    parser.add_argument("--preview", action="store_true", help="print the static UI preview without submitting")
    args = parser.parse_args(argv)

    summary = preview() if args.preview else run()
    if args.json or args.preview:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print("Prospect external run receipt client")
    print(f"producer: {summary['producer']}")
    print(f"frontier_root: {summary['frontier_root']}")
    print(f"claim: {summary['claim']}")
    print(f"typed_status: {summary['typed_status']}")
    print(
        "submit: "
        f"accepted={str(summary['accepted']).lower()}, "
        f"next={summary['next']}, "
        f"proposal_id={summary.get('proposal_id', '')}"
    )


if __name__ == "__main__":
    main()
