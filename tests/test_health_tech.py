"""Tests for health and technology detection."""

from pathlib import Path

from analyzers.health import analyze_health
from analyzers.technologies import detect_technologies


def test_health_checks(tmp_path: Path) -> None:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "README.md").write_text("# hi", encoding="utf-8")
    (p / "pyproject.toml").write_text("", encoding="utf-8")
    (p / "tests").mkdir()
    (p / "tests" / "test_x.py").write_text("", encoding="utf-8")

    files = [
        f.relative_to(p)
        for f in p.rglob("*") if f.is_file()
    ]
    report = analyze_health(p, files)

    checks = {c.name: c.passed for c in report.checks}
    assert checks["README"] is True
    assert checks["Dependencies"] is True
    assert checks["Tests"] is True


def test_health_score_zero_on_empty(tmp_path: Path) -> None:
    report = analyze_health(tmp_path, [])
    assert report.score == 0


def test_detect_technologies(tmp_path: Path) -> None:
    p = tmp_path / "proj"
    (p / "package.json").parent.mkdir(parents=True)
    (p / "package.json").write_text("{}", encoding="utf-8")
    (p / "Cargo.toml").write_text("", encoding="utf-8")

    files = [f.relative_to(p) for f in p.iterdir() if f.is_file()]
    techs = detect_technologies(files)
    names = {t.name for t in techs}
    assert "Node.js" in names
    assert "Rust" in names
