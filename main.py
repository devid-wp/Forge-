"""Forge - CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from analyzers.files import (
    build_tree,
    dir_size_breakdown,
    file_type_summary,
    find_largest_files,
    scan_project,
)
from analyzers.git import analyze_git
from analyzers.health import analyze_health
from analyzers.languages import analyze_languages
from analyzers.technologies import detect_technologies
from ui.display import (
    build_json_output,
    console,
    show_dir_sizes,
    show_file_types,
    show_git,
    show_header,
    show_health,
    show_languages,
    show_largest_files,
    show_project_info,
    show_progress,
    show_summary,
    show_technologies,
    show_tree,
)
from utils.ignore import IgnoreRules

VERSION = "1.0.0"

app = typer.Typer(
    name="forge",
    help="Forge - CLI dev project analyzer.",
    no_args_is_help=False,
    invoke_without_command=True,
)

KNOWN_COMMANDS = {"analyze", "stats", "tree", "git", "health"}
TOP_LEVEL_FLAGS = {"--help", "-h", "--version", "-V", "--install-completion", "--show-completion"}


@app.callback()
def _main_callback(
    version: bool = typer.Option(False, "--version", "-V", help="Show the version."),
) -> None:
    """Forge entry point."""
    if version:
        console.print(f"Forge {VERSION}")
        raise typer.Exit()


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
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    top_files: int = typer.Option(
        10, "--top-files", "-f", help="Number of largest files to show (0 to skip)"
    ),
    dir_sizes: bool = typer.Option(False, "--dir-sizes", help="Show directory sizes"),
) -> None:
    """Run a full project analysis."""
    root = _resolve_path(path)
    rules = IgnoreRules(root)

    if json_output:
        _analyze_json(root, depth, no_git, top_files, dir_sizes)
        return

    show_header(root)

    with show_progress("Analysis") as progress:
        task = progress.add_task("Scanning files...", total=None)
        project_info = scan_project(root, rules)
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

        largest = find_largest_files(project_info.files, root, top_files) if top_files else []
        dir_sizes_list = dir_size_breakdown(project_info.files, root) if dir_sizes else []
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_project_info(project_info)
    console.print()
    show_languages(lang_stats)
    console.print()
    show_technologies(techs)

    if largest:
        console.print()
        show_largest_files(largest)
    if dir_sizes_list:
        console.print()
        show_dir_sizes(dir_sizes_list)

    console.print()
    if git_info:
        show_git(git_info)
        console.print()
    show_health(health)

    if not no_tree:
        console.print()
        tree_lines = build_tree(root, max_depth=depth, rules=rules)
        show_tree(tree_lines, project_info.name)

    show_summary(project_info, lang_stats, git_info, health, techs)


def _analyze_json(root: Path, depth: int, no_git: bool, top_files: int, dir_sizes: bool) -> None:
    """Collect full analysis and print as JSON."""
    rules = IgnoreRules(root)
    project_info = scan_project(root, rules)
    lang_stats = analyze_languages(project_info.files)
    techs = detect_technologies(project_info.files)
    health = analyze_health(root, project_info.files)

    git_info = None if no_git else analyze_git(root)

    largest = find_largest_files(project_info.files, root, top_files) if top_files else []
    dir_sizes_list = dir_size_breakdown(project_info.files, root) if dir_sizes else []
    type_summary = file_type_summary(project_info.files, root)

    output = build_json_output(
        project_info, lang_stats, techs, git_info, health, largest, dir_sizes_list,
        type_summary,
    )
    console.print(output)


def _analyze_stats(path: str, json_output: bool, top_files: int, show_types: bool = True) -> None:
    """Shared implementation for stats output."""
    root = _resolve_path(path)
    rules = IgnoreRules(root)

    if json_output:
        _analyze_json(root, depth=4, no_git=True, top_files=top_files, dir_sizes=False)
        return

    show_header(root)

    with show_progress("Statistics") as progress:
        task = progress.add_task("Scanning...", total=None)
        project_info = scan_project(root, rules)
        lang_stats = analyze_languages(project_info.files)
        largest = find_largest_files(project_info.files, root, top_files) if top_files else []
        type_summary = file_type_summary(project_info.files, root) if show_types else {}
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_project_info(project_info)
    console.print()
    show_languages(lang_stats)

    if type_summary:
        console.print()
        show_file_types(type_summary)

    if largest:
        console.print()
        show_largest_files(largest)


@app.command()
def stats(
    path: str = typer.Argument(".", help="Path to the project"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    top_files: int = typer.Option(
        10, "--top-files", "-f", help="Number of largest files to show (0 to skip)"
    ),
    show_types: bool = typer.Option(True, "--types/--no-types", help="Show text vs binary summary"),
) -> None:
    """Show language and file statistics."""
    _analyze_stats(path, json_output, top_files, show_types)


@app.command()
def tree(
    path: str = typer.Argument(".", help="Path to the project"),
    depth: int = typer.Option(4, "--depth", "-d", help="Maximum depth"),
) -> None:
    """Show the project file tree."""
    root = _resolve_path(path)
    rules = IgnoreRules(root)

    tree_lines = build_tree(root, max_depth=depth, rules=rules)
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
    rules = IgnoreRules(root)
    show_header(root)

    with show_progress("Health") as progress:
        task = progress.add_task("Analyzing...", total=None)
        project_info = scan_project(root, rules)
        report = analyze_health(root, project_info.files)
        progress.update(task, description="Done!", completed=1)

    console.print()
    show_health(report)


def main() -> None:
    """CLI entry point with command routing.

    `forge` and `forge /path/to/project` run a full analysis directly,
    while named subcommands (stats, tree, git, health) stay available.
    """
    raw = sys.argv[1:]

    if not raw:
        sys.argv = [sys.argv[0], "analyze"]
    elif raw[0] not in KNOWN_COMMANDS and raw[0] not in TOP_LEVEL_FLAGS:
        sys.argv = [sys.argv[0], "analyze", *raw]

    app()


if __name__ == "__main__":
    main()
