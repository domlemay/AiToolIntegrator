"""CLI command: aitool list [--installed]."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import get_output_console, print_info


console = get_output_console()


def list_cmd(
    installed: Annotated[
        bool,
        typer.Option("--installed", "-i", help="Show only installed tools"),
    ] = False,
) -> None:
    """List tools from the registry with their installation status.

    Examples:
        aitool list
        aitool list --installed
    """
    engine = Engine(AppConfig())
    tools = engine.list_tools(installed_only=installed)

    if not tools:
        if installed:
            print_info("No tools installed yet. Run 'aitool install <tool>' to get started.")
        else:
            print_info("Registry is empty.")
        return

    label = "Installed tools" if installed else f"All tools ({len(tools)} total)"
    table = Table(
        title=f"[bold]{label}[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )
    table.add_column("Status", justify="center", min_width=6)
    table.add_column("Name", style="bold", min_width=12)
    table.add_column("Version", min_width=8)
    table.add_column("Category", style="magenta", min_width=16)
    table.add_column("Stars", justify="right", style="yellow", min_width=6)
    table.add_column("Description")

    for entry, is_inst in tools:
        if installed and not is_inst:
            continue
        status = "[green]OK[/green]" if is_inst else "[dim]-[/dim]"
        stars = f"{entry.stars:,}" if entry.stars else "-"
        table.add_row(
            status,
            entry.name,
            entry.version,
            entry.category,
            stars,
            entry.description_short,
        )

    console.print(table)
