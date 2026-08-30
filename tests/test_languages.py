"""Tests for language line counting."""

from pathlib import Path

from analyzers.languages import count_lines, _raw_lines, detect_language


def test_count_python_lines_skips_comments_and_blanks(tmp_path: Path) -> None:
    p = tmp_path / "sample.py"
    p.write_text(
        "# comment\n"
        "def hello():\n"
        "    return 1\n"
        "\n"
        "# another\n"
        "x = 2\n",
        encoding="utf-8",
    )
    assert count_lines(p) == 3
    assert _raw_lines(p) == 6


def test_count_slash_comments(tmp_path: Path) -> None:
    p = tmp_path / "app.ts"
    p.write_text("// comment\nconst a = 1;\nconst b = 2;\n", encoding="utf-8")
    assert count_lines(p) == 2


def test_count_plain_text_counts_all_nonempty(tmp_path: Path) -> None:
    p = tmp_path / "data.txt"
    p.write_text("line1\n\nline2\n", encoding="utf-8")
    assert count_lines(p) == 2


def test_return_0_for_directory(tmp_path: Path) -> None:
    assert count_lines(tmp_path) == 0


def test_detect_language_by_extension() -> None:
    assert detect_language(Path("main.py")) == "Python"
    assert detect_language(Path("app.ts")) == "TypeScript"
    assert detect_language(Path("mod.rs")) == "Rust"
    assert detect_language(Path("Dockerfile")) == "Dockerfile"
    assert detect_language(Path("unknown.zzz")) is None
