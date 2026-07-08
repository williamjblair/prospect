"""Static contract for the Findings evidence table rhythm.

The Findings tab is the judge's main science-reading surface. These checks
pin a reusable evidence panel and responsive row treatment so the evidence
tables stay scannable without changing the underlying science.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "app" / "page.tsx"
CSS = ROOT / "web" / "app" / "globals.css"


def test_findings_evidence_tables_use_shared_rhythm_components():
    page = PAGE.read_text()
    css = CSS.read_text()

    assert "function FindingEvidencePanel" in page
    assert "function FindingEvidenceRow" in page
    assert "finding-evidence-panel" in page
    assert "finding-evidence-row" in page
    assert "finding-metric-strip" in page
    assert ".finding-evidence-row" in css
    assert "@media (max-width: 700px)" in css
    assert "grid-template-columns: minmax(72px, 0.6fr) minmax(0, 1fr) minmax(92px, auto)" in css


if __name__ == "__main__":
    test_findings_evidence_tables_use_shared_rhythm_components()
    print("PASS: findings visual rhythm")
