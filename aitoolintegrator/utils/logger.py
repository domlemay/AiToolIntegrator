"""Rich-based structured logging for AiToolIntegrator."""

from __future__ import annotations

import logging
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text


console = Console(stderr=True)
_output_console = Console()


def get_logger(name: str = "aitoolintegrator") -> logging.Logger:
    """Return a configured logger that outputs via Rich.

    Args:
        name: Logger name, defaults to root project logger.

    Returns:
        A Logger instance with Rich formatting.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            console=console,
            show_time=False,
            show_path=False,
            markup=True,
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def print_success(message: str) -> None:
    """Print a success message with green styling."""
    _output_console.print(f"[bold green]✅ {message}[/bold green]")


def print_error(message: str, suggestion: str | None = None) -> None:
    """Print an error message with red styling and optional suggestion.

    Args:
        message: The error description.
        suggestion: Optional hint for resolving the error.
    """
    _output_console.print(f"[bold red]❌ {message}[/bold red]")
    if suggestion:
        _output_console.print(f"   [dim]→ {suggestion}[/dim]")


def print_warning(message: str) -> None:
    """Print a warning message with yellow styling."""
    _output_console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")


def print_info(message: str) -> None:
    """Print an info message."""
    _output_console.print(f"[cyan]ℹ  {message}[/cyan]")


def print_panel(title: str, content: str, style: str = "blue") -> None:
    """Print a Rich panel with title and content.

    Args:
        title: Panel title.
        content: Panel body content (supports Rich markup).
        style: Panel border style color.
    """
    _output_console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style=style))


def get_output_console() -> Console:
    """Return the main output console instance."""
    return _output_console
