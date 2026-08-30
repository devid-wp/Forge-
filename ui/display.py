"""Render analysis results using Rich."""

from __future__ import annotations

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
    table.add_column("%", justify="right")

    for lang in langs:
        pct = (lang.line_count / stats.total_lines * 100) if stats.total_lines else 0
        table.add_row(
            lang.name,
            str(lang.file_count),
            f"{lang.line_count:,}",
            f"{pct:.1f}%",
        )

    table.add_row(
        "[bold]Total[/]",
        f"[bold]{stats.total_files}[/]",
        f"[bold]{stats.total_lines:,}[/]",
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
    git_info: GitInfo,
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

    if git_info.is_repo:
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
