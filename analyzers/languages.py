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
    line_count: int = 0


@dataclass
class LanguageStats:
    """Statistics for all languages in a project."""

    languages: dict[str, LanguageInfo] = None  # type: ignore[assignment]
    total_lines: int = 0
    total_files: int = 0

    def __post_init__(self) -> None:
        if self.languages is None:
            self.languages = {}

    def add(self, lang: str, lines: int) -> None:
        if lang not in self.languages:
            self.languages[lang] = LanguageInfo(name=lang)
        self.languages[lang].file_count += 1
        self.languages[lang].line_count += lines
        self.total_lines += lines
        self.total_files += 1


def count_lines(filepath: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
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
        lines = count_lines(filepath)
        stats.add(lang, lines)

    return stats


def get_sorted_languages(stats: LanguageStats) -> list[LanguageInfo]:
    """Return languages sorted by line count descending."""
    if not stats.languages:
        return []
    return sorted(stats.languages.values(), key=lambda x: x.line_count, reverse=True)
