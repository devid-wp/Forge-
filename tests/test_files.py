"""Tests for file scanning and ignoring."""

from pathlib import Path

import pytest

from analyzers.files import scan_project, build_tree
from utils.ignore import IgnoreRules, should_ignore_dir, should_ignore_file


def _make_tree(root: Path, structure: dict) -> None:
    for name, content in structure.items():
        if isinstance(content, dict):
            _make_tree(root / name, content)
        else:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(content or "", encoding="utf-8")


def test_scan_project_counts(tmp_path: Path) -> None:
    _make_tree(tmp_path / "proj", {
        "app": {"main.py": "x = 1\n", "style.css": "body {}\n"},
        "node_modules": {"dep": {"index.js": "a\n"}},
        "utils": {"helper.py": "y = 2\n"},
    })

    info = scan_project(tmp_path / "proj")
    assert info.file_count == 3
    assert info.dir_count == 2
    assert all(
        str(f) != "node_modules/dep/index.js"
        for f in info.files
    )


def test_ignore_dir_and_file() -> None:
    assert should_ignore_dir("node_modules")
    assert should_ignore_dir(".venv")
    assert should_ignore_dir("my_pkg.egg-info")
    assert not should_ignore_dir("src")
    assert should_ignore_file("package-lock.json")
    assert not should_ignore_file("main.py")


def test_build_tree_ignores_heavy_dirs(tmp_path: Path) -> None:
    _make_tree(tmp_path / "proj", {
        "src": {"a.py": "1"},
        "node_modules": {"b.py": "2"},
    })
    lines = build_tree(tmp_path / "proj")
    text = "\n".join(lines)
    assert "src/" in text
    assert "node_modules" not in text


def test_forgeignore_skips_directories(tmp_path: Path) -> None:
    _make_tree(tmp_path / "proj", {
        ".forgeignore": "generated/\n",
        "generated": {"out.py": "x = 1\n"},
        "src": {"main.py": "y = 2\n"},
    })
    rules = IgnoreRules(tmp_path / "proj")
    info = scan_project(tmp_path / "proj", rules)
    assert all("generated" not in str(f) for f in info.files)
    assert any(str(f) == "src/main.py" for f in info.files)


def test_forgeignore_skips_file_pattern(tmp_path: Path) -> None:
    _make_tree(tmp_path / "proj", {
        ".forgeignore": "*.min.js\n",
        "src": {"a.min.js": "x\n", "a.js": "y\n"},
    })
    rules = IgnoreRules(tmp_path / "proj")
    info = scan_project(tmp_path / "proj", rules)
    paths = {str(f) for f in info.files}
    assert "src/a.min.js" not in paths
    assert "src/a.js" in paths


def test_forgeignore_nested_directory(tmp_path: Path) -> None:
    _make_tree(tmp_path / "proj", {
        ".forgeignore": "build/\n",
        "src": {"build": {"out.py": "x"}, "main.py": "y"},
    })
    rules = IgnoreRules(tmp_path / "proj")
    info = scan_project(tmp_path / "proj", rules)
    assert all("build" not in str(f) for f in info.files)
