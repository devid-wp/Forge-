"""Filesystem analysis of a project."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from utils.ignore import should_ignore_dir, should_ignore_file


@dataclass
class ProjectInfo:
    """Basic information about a project."""

    name: str
    root: Path
    total_size: int = 0
    file_count: int = 0
    dir_count: int = 0
    files: list[Path] = field(default_factory=list)


def _dir_size(path: Path) -> int:
    """Compute the size of a directory in bytes."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False) and not should_ignore_dir(entry.name):
                total += _dir_size(Path(entry.path))
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


def scan_project(root: Path) -> ProjectInfo:
    """Scan a project and collect basic information."""
    info = ProjectInfo(name=root.name, root=root)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d)]
        info.dir_count += len(dirnames)

        for f in filenames:
            if should_ignore_file(f):
                continue
            filepath = Path(dirpath) / f
            info.files.append(filepath.relative_to(root))
            info.file_count += 1
            try:
                info.total_size += filepath.stat().st_size
            except OSError:
                pass

    return info


def _get_sorted_entries(path: Path) -> list[tuple[str, bool]]:
    """Return sorted directory entries as (name, is_dir) tuples."""
    try:
        entries = []
        for entry in os.scandir(path):
            if should_ignore_dir(entry.name):
                continue
            entries.append((entry.name, entry.is_dir(follow_symlinks=False)))
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
            sub_entries = _get_sorted_entries(path / name)
            _build_tree_recursive(
                path / name, sub_entries, lines,
                new_prefix, max_depth, current_depth + 1,
            )


def build_tree(root: Path, max_depth: int = 4) -> list[str]:
    """Build a text-based tree of a project."""
    lines: list[str] = []
    entries = _get_sorted_entries(root)
    _build_tree_recursive(root, entries, lines, prefix="", max_depth=max_depth, current_depth=0)
    return lines
