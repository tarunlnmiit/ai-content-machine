"""Shared rich console + progress helpers for all content-machine scripts."""

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.theme import Theme

_theme = Theme({
    "info":    "cyan",
    "success": "bold green",
    "warn":    "yellow",
    "error":   "bold red",
    "dim":     "dim white",
    "niche":   "bold magenta",
})

console = Console(theme=_theme)


def progress_bar(description: str = "Working...") -> Progress:
    """Standard determinate progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=32),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


def spinner(description: str = "Working...") -> Progress:
    """Indeterminate spinner — for single API calls with unknown duration."""
    return Progress(
        SpinnerColumn("dots"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )
