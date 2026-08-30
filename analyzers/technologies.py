"""Technology detection by configuration files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TechInfo:
    """Information about a single technology."""

    name: str
    config_file: str
    description: str


TECH_MARKERS: dict[str, tuple[str, str]] = {
    "requirements.txt": ("Python", "pip"),
    "pyproject.toml": ("Python (pyproject)", "pip/poetry/uv"),
    "setup.py": ("Python (setuptools)", "pip"),
    "setup.cfg": ("Python (setuptools)", "pip"),
    "package.json": ("Node.js", "npm/yarn/pnpm"),
    "yarn.lock": ("Node.js (Yarn)", "yarn"),
    "pnpm-lock.yaml": ("Node.js (pnpm)", "pnpm"),
    "bun.lockb": ("Node.js (Bun)", "bun"),
    "Cargo.toml": ("Rust", "cargo"),
    "go.mod": ("Go", "go"),
    "pom.xml": ("Java (Maven)", "mvn"),
    "build.gradle": ("Java/Kotlin (Gradle)", "gradle"),
    "build.gradle.kts": ("Kotlin (Gradle)", "gradle"),
    "Gemfile": ("Ruby", "bundler"),
    "composer.json": ("PHP (Composer)", "composer"),
    "pubspec.yaml": ("Dart (Flutter)", "dart/flutter"),
    "mix.exs": ("Elixir", "mix"),
    "Dockerfile": ("Docker", "docker"),
    "docker-compose.yml": ("Docker Compose", "docker compose"),
    "docker-compose.yaml": ("Docker Compose", "docker compose"),
    "Makefile": ("Make", "make"),
    "CMakeLists.txt": ("CMake", "cmake"),
    ".eslintrc.js": ("ESLint", "eslint"),
    "eslint.config.js": ("ESLint (flat)", "eslint"),
    "tsconfig.json": ("TypeScript", "tsc"),
    "vite.config.js": ("Vite", "vite"),
    "vite.config.ts": ("Vite (TS)", "vite"),
    "webpack.config.js": ("Webpack", "webpack"),
    "next.config.js": ("Next.js", "next"),
    "next.config.mjs": ("Next.js", "next"),
    "nuxt.config.js": ("Nuxt.js", "nuxt"),
    "nuxt.config.ts": ("Nuxt.js (TS)", "nuxt"),
    "svelte.config.js": ("SvelteKit", "svelte"),
    "tailwind.config.js": ("Tailwind CSS", "tailwind"),
    "tailwind.config.ts": ("Tailwind CSS (TS)", "tailwind"),
    "pytest.ini": ("Pytest", "pytest"),
    "conftest.py": ("Pytest", "pytest"),
    ".pre-commit-config.yaml": ("Pre-commit", "pre-commit"),
    "tox.ini": ("Tox", "tox"),
}


def detect_technologies(files: list[Path]) -> list[TechInfo]:
    """Detect technologies of a project by configuration files."""
    file_names = {f.name for f in files}
    detected: list[TechInfo] = []
    seen: set[str] = set()

    for fname, (name, desc) in TECH_MARKERS.items():
        if fname in file_names and name not in seen:
            detected.append(TechInfo(name=name, config_file=fname, description=desc))
            seen.add(name)

    return detected
