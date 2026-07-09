"""Anti-overclaim rigor audit tests."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.rigor_audit import build_audit, write_audit


def test_rigor_audit_has_no_blocked_public_overclaim_phrases():
    audit = build_audit()

    assert audit["passed"] is True
    assert audit["blocked_phrase_hits"] == []
    for row in audit["traceable_claims"]:
        assert row["artifact_present"] is True
        assert row["command_present"] is True
    assert audit["framing_guards"]["claude_science"] == "driver-versus-passenger, not signature-is-wrong"
    assert audit["framing_guards"]["pggt1b"] == "proposal-only lead worth testing, not accepted biology"


def test_rigor_audit_writes_markdown_without_boolean_slop(tmp_path):
    out_doc = tmp_path / "RIGOR_AUDIT.md"

    audit = write_audit(out_doc=out_doc)
    doc = out_doc.read_text()

    assert audit["passed"] is True
    assert "Passed: `yes`" in doc
    assert "claims were wrong" not in doc
    assert "PGGT1B clears the fixed bar" not in doc
    assert "independently validated" not in doc


def test_rigor_audit_cli_emits_json_and_writes_doc():
    proc = subprocess.run(
        [os.path.join(ROOT, "prospect"), "rigor-audit", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["passed"] is True
    assert (ROOT / "docs" / "RIGOR_AUDIT.md").exists()


if __name__ == "__main__":
    test_rigor_audit_has_no_blocked_public_overclaim_phrases()
    test_rigor_audit_writes_markdown_without_boolean_slop(Path("/tmp/prospect-rigor-audit-test"))
    test_rigor_audit_cli_emits_json_and_writes_doc()
    print("PASS: rigor audit")
