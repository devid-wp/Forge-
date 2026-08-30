"""Render analysis results using Rich."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from analyzers.files import ProjectInfo, _format_size
from analyzers.git import GitInfo
from analyzers.health import HealthReport
from analyzers.languages import LanguageStats, get_sorted_languages
from analyzers.technologies import TechInfo


console = Console()


def show_header(path: Path) -> None:
    """Render the analysis header."""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]Forge[/] - Project Analysis\n"
            f"[dim]{path.resolve()}[/]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def show_project_info(info: ProjectInfo) -> None:
    """Render basic project information."""
    table = Table(
        title="[bold]Project Information[/]",
        border_style="blue",
        show_header=False,
        title_style="bold",
    )
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Name", info.name)
    table.add_row("Path", str(info.root))
    table.add_row("Size", _format_size(info.total_size))
    table.add_row("Files", str(info.file_count))
    table.add_row("Directories", str(info.dir_count))

    console.print(table)


def show_languages(stats: LanguageStats) -> None:
    """Render language statistics."""
    langs = get_sorted_languages(stats)
    if not langs:
        console.print("[yellow]No languages detected[/]")
        return

    table = Table(
        title="[bold]Programming Languages[/]",
        border_style="green",
    )
    table.add_column("Language", style="bold")
    table.add_column("Files", justify="right")
    table.add_column("Lines", justify="right")
    table.add_column("Code", justify="right")
    table.add_column("%", justify="right")

    total_code = sum(lang.code_lines for lang in langs)

    for lang in langs:
        pct = (lang.code_lines / total_code * 100) if total_code else 0
        table.add_row(
            lang.name,
            str(lang.file_count),
            f"{lang.total_lines:,}",
            f"{lang.code_lines:,}",
            f"{pct:.1f}%",
        )

    total_lines_sum = sum(lang.total_lines for lang in langs)
    table.add_row(
        "[bold]Total[/]",
        f"[bold]{stats.total_files}[/]",
        f"[bold]{total_lines_sum:,}[/]",
        f"[bold]{total_code:,}[/]",
        "[bold]100%[/]",
        end_section=True,
    )

    console.print(table)


def show_tree(lines: list[str], root_name: str) -> None:
    """Render the project tree."""
    if not lines:
        console.print("[yellow]Tree is empty[/]")
        return

    tree_lines = [f"[bold cyan]{root_name}/[/]"] + list(lines)
    content = "\n".join(tree_lines)
    console.print(Panel(content, title="[bold]Project Structure[/]", border_style="magenta"))


def show_technologies(techs: list[TechInfo]) -> None:
    """Render detected technologies."""
    if not techs:
        console.print("[yellow]No technologies detected[/]")
        return

    table = Table(
        title="[bold]Technologies[/]",
        border_style="yellow",
    )
    table.add_column("Technology", style="bold")
    table.add_column("Config File")
    table.add_column("Package Manager")

    for t in techs:
        table.add_row(t.name, t.config_file, t.description)

    console.print(table)


def show_git(info: GitInfo) -> None:
    """Render git information."""
    if not info.is_repo:
        console.print(Panel(
            "[yellow]Project is not a git repository[/]",
            title="[bold]Git[/]",
            border_style="red",
        ))
        return

    table = Table(
        title="[bold]Git[/]",
        border_style="cyan",
        show_header=False,
    )
    table.add_column("Field", style="dim")
    table.add_column("Value")

    table.add_row("Branch", info.branch)
    table.add_row("Commits", str(info.total_commits))
    table.add_row("Last commit", f"[green]{info.last_commit_hash}[/] {info.last_commit_message}")
    table.add_row("Author", info.last_commit_author)
    table.add_row("Date", info.last_commit_date)

    changes_str = f"{info.uncommitted_changes} (staged: {info.staged_files}, untracked: {info.untracked_files})"
    style = "green" if info.uncommitted_changes == 0 else "yellow"
    table.add_row("Uncommitted", f"[{style}]{changes_str}[/]")

    console.print(table)


def show_health(report: HealthReport) -> None:
    """Render the project health report."""
    table = Table(
        title=f"[bold]Project Health - {report.score}/100[/]",
        border_style="blue",
    )
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Description")

    for check in report.checks:
        status = "[green]\u2713 PASS[/]" if check.passed else "[red]\u2717 FAIL[/]"
        table.add_row(check.name, status, check.description)

    console.print(table)


def show_summary(
    info: ProjectInfo,
    lang_stats: LanguageStats,
    git_info: GitInfo | None,
    health: HealthReport,
    techs: list[TechInfo],
) -> None:
    """Render the final summary."""
    langs = get_sorted_languages(lang_stats)
    primary_lang = langs[0].name if langs else "N/A"

    parts = [
        f"[bold]{info.name}[/]",
        f"[cyan]{info.file_count} files[/] | [green]{_format_size(info.total_size)}[/]",
        f"[yellow]{primary_lang}[/] ({len(langs)} languages)",
        f"Health: [bold]{health.score}/100[/] ({health.passed_count}/{len(health.checks)} checks)",
    ]

    if git_info is None:
        parts.append("[dim]Git skipped[/]")
    elif git_info.is_repo:
        parts.append(f"Git: [cyan]{git_info.branch}[/] ({git_info.total_commits} commits)")
    else:
        parts.append("[dim]No git[/]")

    parts.append(f"Tech: {', '.join(t.name for t in techs) or 'N/A'}")

    console.print()
    console.print(Panel(
        "\n".join(parts),
        title="[bold cyan]\u2728 Analysis Complete[/]",
        border_style="cyan",
        padding=(1, 2),
    ))


def show_progress(action: str, total: int = 0) -> Progress:
    """Create a progress bar for long operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def show_largest_files(largest: list[tuple[Path, int]]) -> None:
    """Render the largest files table."""
    if not largest:
        return

    table = Table(
        title="[bold]Largest Files[/]",
        border_style="red",
    )
    table.add_column("File", style="bold")
    table.add_column("Size", justify="right")

    for filepath, size in largest:
        table.add_row(str(filepath), _format_size(size))

    console.print(table)


def show_dir_sizes(dirs: list[tuple[str, int]]) -> None:
    """Render directory size breakdown."""
    if not dirs:
        return

    table = Table(
        title="[bold]Directory Sizes[/]",
        border_style="yellow",
    )
    table.add_column("Directory", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Bar", min_width=20)

    total = sum(s for _, s in dirs) or 1
    for name, size in dirs:
        pct = size / total
        bar_len = int(pct * 20)
        bar = "\u2588" * bar_len + "\u2591" * (20 - bar_len)
        table.add_row(name, _format_size(size), f"[green]{bar}[/] {pct:.0%}")

    console.print(table)


def show_file_types(summary: dict[str, int]) -> None:
    """Render text vs binary file summary."""
    text, binary, unknown = summary.get("text", 0), summary.get("binary", 0), summary.get("unknown", 0)
    total = text + binary + unknown
    pct_text = (text / total * 100) if total else 0

    table = Table(
        title="[bold]File Types[/]",
        border_style="blue",
    )
    table.add_column("Type", style="bold")
    table.add_column("Files", justify="right")
    table.add_column("%", justify="right")

    table.add_row("Text", str(text), f"{pct_text:.1f}%")
    table.add_row("Binary", str(binary), f"{100 - pct_text:.1f}%" if total else "0.0%")
    if unknown:
        table.add_row("Unknown", str(unknown), "N/A")

    console.print(table)


def build_json_output(
    info: ProjectInfo,
    lang_stats: LanguageStats,
    techs: list[TechInfo],
    git_info: GitInfo | None,
    health: HealthReport,
    largest: list[tuple[Path, int]],
    dir_sizes: list[tuple[str, int]],
    type_summary: dict[str, int] | None = None,
) -> str:
    """Build a JSON string of the full analysis."""
    langs = get_sorted_languages(lang_stats)
    total_code = sum(l.code_lines for l in langs)

    data = {
        "project": {
            "name": info.name,
            "path": str(info.root),
            "size_bytes": info.total_size,
            "size_human": _format_size(info.total_size),
            "file_count": info.file_count,
            "dir_count": info.dir_count,
        },
        "languages": [
            {
                "name": l.name,
                "files": l.file_count,
                "code_lines": l.code_lines,
                "total_lines": l.total_lines,
                "percent": round(l.code_lines / total_code * 100, 1) if total_code else 0,
            }
            for l in langs
        ],
        "technologies": [
            {"name": t.name, "config_file": t.config_file, "package_manager": t.description}
            for t in techs
        ],
        "git": {
            "is_repo": git_info.is_repo,
            "branch": git_info.branch,
            "total_commits": git_info.total_commits,
            "last_commit_hash": git_info.last_commit_hash,
            "last_commit_message": git_info.last_commit_message,
            "last_commit_author": git_info.last_commit_author,
            "last_commit_date": git_info.last_commit_date,
            "uncommitted_changes": git_info.uncommitted_changes,
        } if git_info else None,
        "health": {
            "score": health.score,
            "checks": [
                {"name": c.name, "passed": c.passed, "description": c.description}
                for c in health.checks
            ],
        },
        "largest_files": [
            {"path": str(p), "size_bytes": s, "size_human": _format_size(s)}
            for p, s in largest
        ],
        "directory_sizes": [
            {"name": n, "size_bytes": s, "size_human": _format_size(s)}
            for n, s in dir_sizes
        ],
        "file_types": type_summary,
    }
    return json.dumps(data, indent=2)
