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


if __name__ == "__main__":
    test_tracked_files_do_not_contain_em_dash_or_attribution_footer()
    test_tracked_files_do_not_contain_prior_work_or_weak_status_markers()
    print("PASS: repo hygiene")
