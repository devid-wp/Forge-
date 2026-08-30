"""Forge - CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from analyzers.files import build_tree, scan_project
from analyzers.git import analyze_git
from analyzers.health import analyze_health
from analyzers.languages import analyze_languages
from analyzers.technologies import detect_technologies
from ui.display import (
    console,
    show_git,
    show_header,
    show_health,
    show_languages,
    show_project_info,
    show_progress,
    show_summary,
    show_technologies,
    show_tree,
)

app = typer.Typer(
    name="devanalyze",
    help="Forge - CLI dev project analyzer.",
    no_args_is_help=True,
)

KNOWN_COMMANDS = {"analyze", "stats", "tree", "git", "health"}


def _resolve_path(path_str: str) -> Path:
    """Resolve a path and validate it exists as a directory."""
    p = Path(path_str).resolve()
    if not p.exists():
        console.print(f"[red]Path does not exist:[/] {p}")
        raise typer.Exit(1)
    if not p.is_dir():
        console.print(f"[red]Not a directory:[/] {p}")
        raise typer.Exit(1)
    return p


@app.command()
def analyze(
    path: str = typer.Argument(".", help="Path to the project"),
    depth: int = typer.Option(4, "--depth", "-d", help="Maximum tree depth"),
    no_tree: bool = typer.Option(False, "--no-tree", help="Skip the file tree"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip the git analysis"),
) -> None:
    """Run a full project analysis."""
    root = _resolve_path(path)

    show_header(root)

    with show_progress("Analysis") as progress:
        task = progress.add_task("Scanning files...", total=None)
        project_info = scan_project(root)
        progress.update(task, description="Analyzing languages...")
        lang_stats = analyze_languages(project_info.files)
        progress.update(task, description="Detecting technologies...")
        techs = detect_technologies(project_info.files)
        progress.update(task, description="Checking health...")
        health = analyze_health(root, project_info.files)

        git_info = None
        if not no_git:
            progress.update(task, description="Analyzing git...")
            git_info = analyze_git(root)
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_project_info(project_info)
    console.print()
    show_languages(lang_stats)
    console.print()
    show_technologies(techs)
    console.print()
    if git_info:
        show_git(git_info)
        console.print()
    show_health(health)

    if not no_tree:
        console.print()
        tree_lines = build_tree(root, max_depth=depth)
        show_tree(tree_lines, project_info.name)

    show_summary(project_info, lang_stats, git_info or analyze_git(root), health, techs)


@app.command()
def stats(
    path: str = typer.Argument(".", help="Path to the project"),
) -> None:
    """Show language and file statistics."""
    root = _resolve_path(path)
    show_header(root)

    with show_progress("Statistics") as progress:
        task = progress.add_task("Scanning...", total=None)
        project_info = scan_project(root)
        lang_stats = analyze_languages(project_info.files)
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_project_info(project_info)
    console.print()
    show_languages(lang_stats)


@app.command()
def tree(
    path: str = typer.Argument(".", help="Path to the project"),
    depth: int = typer.Option(4, "--depth", "-d", help="Maximum depth"),
) -> None:
    """Show the project file tree."""
    root = _resolve_path(path)

    tree_lines = build_tree(root, max_depth=depth)
    show_tree(tree_lines, root.name)


@app.command()
def git(
    path: str = typer.Argument(".", help="Path to the project"),
) -> None:
    """Analyze the git repository."""
    root = _resolve_path(path)
    show_header(root)

    git_info = analyze_git(root)
    console.print()
    show_git(git_info)


@app.command()
def health(
    path: str = typer.Argument(".", help="Path to the project"),
) -> None:
    """Evaluate project health."""
    root = _resolve_path(path)
    show_header(root)

    with show_progress("Health") as progress:
        task = progress.add_task("Analyzing...", total=None)
        project_info = scan_project(root)
        report = analyze_health(root, project_info.files)
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_health(report)


def main() -> None:
    """CLI entry point with command routing."""
    raw = sys.argv[1:]
    if raw and raw[0] not in KNOWN_COMMANDS:
        sys.argv = [sys.argv[0], "analyze", *raw]
    app()


if __name__ == "__main__":
    main()
