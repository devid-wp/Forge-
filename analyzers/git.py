"""Git repository analysis of a project."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitInfo:
    """Information about a git repository."""

    is_repo: bool = False
    branch: str = ""
    total_commits: int = 0
    last_commit_hash: str = ""
    last_commit_message: str = ""
    last_commit_author: str = ""
    last_commit_date: str = ""
    uncommitted_changes: int = 0
    staged_files: int = 0
    untracked_files: int = 0


def _run_git(root: Path, *args: str) -> tuple[int, str]:
    """Run a git command and return (exit code, stdout)."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 1, ""


def analyze_git(root: Path) -> GitInfo:
    """Analyze the git repository of a project."""
    info = GitInfo()

    code, _ = _run_git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return info

    info.is_repo = True

    _, info.branch = _run_git(root, "branch", "--show-current")

    _, count_out = _run_git(root, "rev-list", "--count", "HEAD")
    if count_out.isdigit():
        info.total_commits = int(count_out)

    _, info.last_commit_hash = _run_git(root, "log", "-1", "--format=%h")
    _, info.last_commit_message = _run_git(root, "log", "-1", "--format=%s")
    _, info.last_commit_author = _run_git(root, "log", "-1", "--format=%an")
    _, info.last_commit_date = _run_git(root, "log", "-1", "--format=%cr")

    _, status_out = _run_git(root, "status", "--porcelain")
    if status_out:
        lines = status_out.split("\n")
        info.uncommitted_changes = len(lines)
        info.staged_files = sum(1 for l in lines if l[0] != " " and l[0] != "?")
        info.untracked_files = sum(1 for l in lines if l.startswith("??"))

    return info
