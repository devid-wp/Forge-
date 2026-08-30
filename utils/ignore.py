"""Directories and patterns to ignore during analysis."""

import fnmatch
from pathlib import Path

IGNORED_DIRS: set[str] = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".eggs",
    ".cache",
    ".npm",
    ".yarn",
    "coverage",
    ".next",
    ".nuxt",
    "out",
    ".output",
}

IGNORED_FILES: set[str] = {
    "poetry.lock",
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "go.sum",
}

IGNORE_FILE_NAME = ".forgeignore"


def should_ignore_dir(dirname: str) -> bool:
    """Check whether a directory should be ignored by default rules."""
    if dirname in IGNORED_DIRS:
        return True
    if dirname.endswith(".egg-info"):
        return True
    for pattern in IGNORED_DIRS:
        if pattern.startswith("*") and dirname.endswith(pattern[1:]):
            return True
    return False


def should_ignore_file(filename: str) -> bool:
    """Check whether a file should be ignored by default rules."""
    return filename in IGNORED_FILES


class IgnoreRules:
    """Built-in ignores plus user patterns from a .forgeignore file."""

    def __init__(self, root: Path | None = None) -> None:
        self.patterns: list[tuple[str, bool]] = []
        if root is not None:
            self._load_forgeignore(root)

    def _load_forgeignore(self, root: Path) -> None:
        forge_ignore = root / IGNORE_FILE_NAME
        if not forge_ignore.is_file():
            return
        try:
            raw = forge_ignore.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            dir_only = line.endswith("/")
            self.patterns.append((line.rstrip("/"), dir_only))

    def _match_any(self, rel: str, is_dir: bool) -> bool:
        """Check a relative path against all custom patterns."""
        rel = rel.rstrip("/")
        for pattern, dir_only in self.patterns:
            if dir_only and not is_dir:
                continue
            if fnmatch.fnmatch(rel, pattern):
                return True
            if fnmatch.fnmatch(rel, f"{pattern}/**"):
                return True
            if fnmatch.fnmatch(rel, f"**/{pattern}"):
                return True
            if "/" + pattern in "/" + rel:
                return True
        return False

    def matches(self, rel: str, is_dir: bool = False) -> bool:
        """Check whether a relative path matches any custom pattern."""
        return self._match_any(rel, is_dir=is_dir)

    def should_ignore(self, root: Path, path: Path, is_dir: bool) -> bool:
        """Combine default ignores and custom rules for a path under root."""
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            rel = path.name

        if self.matches(rel, is_dir=is_dir):
            return True
        return should_ignore_dir(path.name) if is_dir else should_ignore_file(path.name)