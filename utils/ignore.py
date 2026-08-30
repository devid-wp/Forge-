"""Directories and patterns to ignore during analysis."""

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


def should_ignore_dir(dirname: str) -> bool:
    """Check whether a directory should be ignored."""
    if dirname in IGNORED_DIRS:
        return True
    if dirname.endswith(".egg-info"):
        return True
    for pattern in IGNORED_DIRS:
        if pattern.startswith("*") and dirname.endswith(pattern[1:]):
            return True
    return False


def should_ignore_file(filename: str) -> bool:
    """Check whether a file should be ignored."""
    return filename in IGNORED_FILES
