"""Repository-wide hygiene guardrails from AGENTS.md."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [path for line in proc.stdout.splitlines() if line and (path := ROOT / line).exists()]


def test_tracked_files_do_not_contain_em_dash_or_attribution_footer():
    offenders: list[str] = []
    for path in _tracked_files():
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for needle in ["\u2014", "Generated " + "with", "Co-Authored" + "-By"]:
            if needle in text:
                offenders.append(f"{path.relative_to(ROOT)}: {needle}")

    assert not offenders, "\n".join(offenders)


def test_tracked_files_do_not_contain_prior_work_or_weak_status_markers():
    offenders: list[str] = []
    needles = [
        "Epis" + "teme",
        "atlas" + "-platform",
        "WORLD" + "_CLASS_SITE_PLAN",
        "Component " + "Vocabulary",
        "VISUAL" + "_RICHNESS",
        "verified " + "by tool call",
    ]
    for path in _tracked_files():
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for needle in needles:
            if needle in text:
                offenders.append(f"{path.relative_to(ROOT)}: {needle}")

    assert not offenders, "\n".join(offenders)


def test_lab_console_css_does_not_keep_retired_project_vocabulary():
    css = (ROOT / "web" / "app" / "globals.css").read_text()
    retired_terms = [
        "almanac",
        "chart-atlas",
        "erdos",
        "event-ruler",
        "ledger",
        "provenance-thread",
        "rtick-",
        "scrub-",
        "star-core",
        "star-ring",
        "Observatory",
        "kintsugi",
        "Hasui",
    ]

    offenders = [term for term in retired_terms if term in css]
    assert not offenders, ", ".join(offenders)


def test_lab_console_css_uses_typed_status_names_not_verified():
    css = (ROOT / "web" / "app" / "globals.css").read_text()
    forbidden = [
        "state-verified",
        "grade-verified",
        "num-verified",
    ]

    offenders = [term for term in forbidden if term in css]
    assert not offenders, ", ".join(offenders)


def test_lab_console_interaction_motion_uses_deliberate_durations():
    css = (ROOT / "web" / "app" / "globals.css").read_text()

    assert "--transition-fast: 180ms var(--ease);" in css
    assert "--transition-normal: 220ms var(--ease);" in css
    assert "--transition-smooth: 220ms var(--ease);" in css
    assert "transition: background-color 180ms var(--ease), color 180ms var(--ease);" in css


def test_react_ui_uses_lab_console_tokens_not_raw_hex():
    offenders: list[str] = []
    for path in [
        ROOT / "web" / "app" / "page.tsx",
        ROOT / "web" / "components" / "graph-view.tsx",
    ]:
        text = path.read_text()
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "#" in line:
                offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {line.strip()}")

    assert not offenders, "\n".join(offenders)


if __name__ == "__main__":
    test_tracked_files_do_not_contain_em_dash_or_attribution_footer()
    test_tracked_files_do_not_contain_prior_work_or_weak_status_markers()
    test_lab_console_css_does_not_keep_retired_project_vocabulary()
    test_lab_console_css_uses_typed_status_names_not_verified()
    test_lab_console_interaction_motion_uses_deliberate_durations()
    test_react_ui_uses_lab_console_tokens_not_raw_hex()
    print("PASS: repo hygiene")
