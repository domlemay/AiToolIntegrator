"""CLI command: aitool info <tool_name>."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import get_output_console, print_error


console = get_output_console()


def info_cmd(
    tool_name: Annotated[str, typer.Argument(help="Tool name to inspect")],
) -> None:
    """Display detailed information about a registry tool.

    Shows the short and long descriptions, tags, repository URL,
    license, platform requirements, and installation status.

    Examples:
        aitool info ollama
        aitool info fabric
    """
    engine = Engine(AppConfig())
    entry = engine.get_tool_info(tool_name)

    if entry is None:
        print_error(
            f"'{tool_name}' not found in registry.",
            suggestion="Run 'aitool search' to browse available tools.",
        )
        raise typer.Exit(1)

    installed = (engine.plugins_dir / entry.name).exists()
    status_str = "[bold green]Installed[/bold green]" if installed else "[dim]Not installed[/dim]"

    content_lines: list[str] = [
        f"[bold]{entry.description_short}[/bold]\n",
        entry.description_long.strip(),
        "",
    ]

    meta_table = Table(show_header=False, box=None, padding=(0, 1))
    meta_table.add_column("Key", style="bold cyan", min_width=14)
    meta_table.add_column("Value")

    meta_table.add_row("Status", status_str)
    meta_table.add_row("Version", entry.version)
    meta_table.add_row("Category", f"[magenta]{entry.category}[/magenta]")
    meta_table.add_row("Tags", ", ".join(entry.tags))
    meta_table.add_row("Repository", entry.repo)
    if entry.homepage:
        meta_table.add_row("Homepage", entry.homepage)
    meta_table.add_row("License", entry.license)
    meta_table.add_row("Stars", f"{entry.stars:,}" if entry.stars else "-")
    meta_table.add_row("Language", entry.language)
    meta_table.add_row("Platforms", ", ".join(entry.platforms))
    meta_table.add_row("GPU required", "Yes" if entry.requires_gpu else "No")
    meta_table.add_row("Min RAM", f"{entry.min_ram_gb} GB")

    console.print(
        Panel(
            "\n".join(content_lines),
            title=f"[bold blue]{entry.name}[/bold blue]",
            subtitle=f"[dim]v{entry.version}[/dim]",
            border_style="blue",
        )
    )
    console.print(meta_table)
