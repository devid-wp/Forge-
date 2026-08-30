"""Programming language analysis of a project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".jsx": "JavaScript (React)",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".r": "R",
    ".R": "R",
    ".lua": "Lua",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".sql": "SQL",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".dockerfile": "Dockerfile",
    ".tf": "Terraform",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".hs": "Haskell",
    ".ml": "OCaml",
    ".scala": "Scala",
    ".gradle": "Gradle",
    ".proto": "Protocol Buffers",
    ".zig": "Zig",
    ".nim": "Nim",
}


@dataclass
class LanguageInfo:
    """Information about a single language."""

    name: str
    file_count: int = 0
    code_lines: int = 0
    total_lines: int = 0


@dataclass
class LanguageStats:
    """Statistics for all languages in a project."""

    languages: dict[str, LanguageInfo] = None  # type: ignore[assignment]
    total_lines: int = 0
    total_files: int = 0

    def __post_init__(self) -> None:
        if self.languages is None:
            self.languages = {}

    def add(self, lang: str, code_lines: int, total_lines: int) -> None:
        if lang not in self.languages:
            self.languages[lang] = LanguageInfo(name=lang)
        self.languages[lang].file_count += 1
        self.languages[lang].code_lines += code_lines
        self.languages[lang].total_lines += total_lines
        self.total_lines += total_lines
        self.total_files += 1


HASH_COMMENT_EXTS = {
    ".py", ".rb", ".sh", ".bash", ".zsh", ".r", ".yaml", ".yml", ".toml",
    ".tf", ".go", ".rs", ".ex", ".exs", ".php", ".erl", ".hs", ".nim", ".zig",
}

SLASH_COMMENT_EXTS = {
    ".js", ".ts", ".jsx", ".tsx", ".java", ".kt", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".swift", ".scala", ".gradle", ".proto", ".svelte", ".vue",
}

SEMI_COMMENT_EXTS = {".sql"}


def _count_code_lines(raw: str, is_source: bool, comment_char: str | None) -> int:
    """Count non-empty lines, skipping single-line comments when requested."""
    if not is_source or comment_char is None:
        return sum(1 for line in raw.splitlines() if line.strip())

    count = 0
    for line in raw.splitlines():
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith(comment_char):
            continue
        count += 1
    return count


def count_lines(filepath: Path) -> int:
    """Count meaningful code lines, skipping empty and comment lines."""
    try:
        raw = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    suffix = filepath.suffix.lower()

    if suffix in HASH_COMMENT_EXTS:
        return _count_code_lines(raw, True, "#")
    if suffix in SLASH_COMMENT_EXTS:
        return _count_code_lines(raw, True, "//")
    if suffix in SEMI_COMMENT_EXTS:
        return _count_code_lines(raw, True, "--")

    always_source = {
        "Dockerfile", "Makefile",
    }
    name = filepath.name.lower()
    if name in ("dockerfile", "makefile") or suffix in always_source or suffix == ".py":
        return _count_code_lines(raw, True, "#")

    return _count_code_lines(raw, False, None)


def _raw_lines(filepath: Path) -> int:
    """Count the total number of lines in a file (including empty/comments)."""
    try:
        raw = filepath.read_text(encoding="utf-8", errors="ignore")
        return sum(1 for _ in raw.splitlines())
    except OSError:
        return 0


def detect_language(filepath: Path) -> str | None:
    """Detect the language of a file by extension."""
    suffix = filepath.suffix.lower()

    if filepath.name.lower() == "dockerfile":
        return "Dockerfile"
    if filepath.name.lower() == "makefile":
        return "Makefile"

    return EXTENSION_MAP.get(suffix)


def analyze_languages(files: list[Path]) -> LanguageStats:
    """Analyze the languages of a project by file list."""
    stats = LanguageStats()

    for filepath in files:
        lang = detect_language(filepath)
        if lang is None:
            continue
        code_lines = count_lines(filepath)
        total_lines = _raw_lines(filepath)
        stats.add(lang, code_lines, total_lines)

    return stats


def get_sorted_languages(stats: LanguageStats) -> list[LanguageInfo]:
    """Return languages sorted by code line count descending."""
    if not stats.languages:
        return []
    return sorted(stats.languages.values(), key=lambda x: x.code_lines, reverse=True)
