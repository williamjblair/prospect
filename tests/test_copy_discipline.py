"""Public copy guardrails for typed evidence status."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_COPY_FILES = [
    ROOT / "web" / "app" / "page.tsx",
    ROOT / "docs" / "HANDOFF.md",
    ROOT / "docs" / "DEMO.md",
    ROOT / "docs" / "JUDGE_PACKET.md",
]

PROHIBITED_PHRASES = [
    "Verified regulatory frontier",
    "verified regulators",
    "Verified regulatory state",
    "verified class",
    "verified facts",
    "verified graph",
    "verified edges",
    "verified tool calls",
    "Verified evidence",
    "fully built, verified",
    "verified state",
]


def test_public_copy_uses_typed_status_language():
    offenders: list[str] = []
    for path in PUBLIC_COPY_FILES:
        text = path.read_text()
        for phrase in PROHIBITED_PHRASES:
            if phrase in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")

    assert not offenders, "\n".join(offenders)


if __name__ == "__main__":
    test_public_copy_uses_typed_status_language()
    print("PASS: public copy uses typed status language")
