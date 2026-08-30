"""Filesystem analysis of a project."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from utils.ignore import IgnoreRules


@dataclass
class ProjectInfo:
    """Basic information about a project."""

    name: str
    root: Path
    total_size: int = 0
    file_count: int = 0
    dir_count: int = 0
    files: list[Path] = field(default_factory=list)


def _dir_size(path: Path, rules: IgnoreRules | None = None) -> int:
    """Compute the size of a directory in bytes."""
    rules = rules or IgnoreRules()
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                dir_path = Path(entry.path)
                if rules.should_ignore(path, dir_path, is_dir=True):
                    continue
                total += _dir_size(dir_path, rules)
    except PermissionError:
        pass
    return total


def _format_size(size_bytes: int) -> str:
    """Format a byte count into a human readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def scan_project(root: Path, rules: IgnoreRules | None = None) -> ProjectInfo:
    """Scan a project and collect basic information."""
    rules = rules or IgnoreRules(root)
    info = ProjectInfo(name=root.name, root=root)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if not rules.should_ignore(root, Path(dirpath) / d, is_dir=True)
        ]
        info.dir_count += len(dirnames)

        for f in filenames:
            filepath = Path(dirpath) / f
            if not rules.should_ignore(root, filepath, is_dir=False):
                info.files.append(filepath.relative_to(root))
                info.file_count += 1
                try:
                    info.total_size += filepath.stat().st_size
                except OSError:
                    pass

    return info


def _get_sorted_entries(path: Path, rules: IgnoreRules) -> list[tuple[str, bool]]:
    """Return sorted directory entries as (name, is_dir) tuples."""
    try:
        entries = []
        for entry in os.scandir(path):
            entry_path = Path(entry.path)
            is_dir = entry.is_dir(follow_symlinks=False)
            if rules.should_ignore(path, entry_path, is_dir=is_dir):
                continue
            entries.append((entry.name, is_dir))
        entries.sort(key=lambda x: (not x[1], x[0].lower()))
        return entries
    except PermissionError:
        return []


def _build_tree_recursive(
    path: Path,
    entries: list[tuple[str, bool]],
    lines: list[str],
    prefix: str,
    max_depth: int,
    current_depth: int,
    rules: IgnoreRules,
) -> None:
    """Recursively build a file tree as text lines."""
    if current_depth >= max_depth:
        return

    for i, (name, is_dir) in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
        suffix = "/" if is_dir else ""
        lines.append(f"{prefix}{connector}{name}{suffix}")

        if is_dir:
            new_prefix = prefix + ("    " if is_last else "\u2502   ")
            sub_entries = _get_sorted_entries(path / name, rules)
            _build_tree_recursive(
                path / name, sub_entries, lines,
                new_prefix, max_depth, current_depth + 1, rules,
            )


def find_largest_files(files: list[Path], root: Path, top_n: int = 10) -> list[tuple[Path, int]]:
    """Return the largest files sorted by size descending."""
    sized: list[tuple[Path, int]] = []
    for f in files:
        full = root / f
        try:
            sized.append((f, full.stat().st_size))
        except OSError:
            pass
    sized.sort(key=lambda x: x[1], reverse=True)
    return sized[:top_n]


def dir_size_breakdown(files: list[Path], root: Path) -> list[tuple[str, int]]:
    """Compute total size per top-level directory."""
    dirs: dict[str, int] = {}
    for f in files:
        parts = f.parts
        top = parts[0] if len(parts) > 1 else "(root)"
        full = root / f
        try:
            dirs[top] = dirs.get(top, 0) + full.stat().st_size
        except OSError:
            pass
    result = sorted(dirs.items(), key=lambda x: x[1], reverse=True)
    return result


def classify_file_type(filepath: Path) -> str:
    """Classify a file as 'text' or 'binary' by probing its content."""
    try:
        with open(filepath, "rb") as fh:
            chunk = fh.read(8192)
    except OSError:
        return "unknown"
    if not chunk:
        return "text"
    return "binary" if b"\x00" in chunk else "text"


def file_type_summary(files: list[Path], root: Path) -> dict[str, int]:
    """Return counts of 'text' and 'binary' files."""
    counts = {"text": 0, "binary": 0, "unknown": 0}
    for f in files:
        kind = classify_file_type(root / f)
        counts[kind] = counts.get(kind, 0) + 1
    return counts


def build_tree(root: Path, max_depth: int = 4, rules: IgnoreRules | None = None) -> list[str]:
    """Build a text-based tree of a project."""
    rules = rules or IgnoreRules(root)
    lines: list[str] = []
    entries = _get_sorted_entries(root, rules)
    _build_tree_recursive(
        root, entries, lines, prefix="", max_depth=max_depth, current_depth=0, rules=rules
    )
    return lines
