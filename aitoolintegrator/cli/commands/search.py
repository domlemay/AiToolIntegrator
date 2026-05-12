"""CLI command: aitool search <query> [--tags TAG] [--sort stars|name]."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import get_output_console, print_info, print_warning

console = get_output_console()


def search_cmd(
    query: Annotated[str, typer.Argument(help="Search query (name, description, tags)")] = "",
    tags: Annotated[
        list[str] | None,
        typer.Option("--tags", "-t", help="Filter by tag (repeatable: --tags llm --tags local)"),
    ] = None,
    sort: Annotated[
        str,
        typer.Option("--sort", "-s", help="Sort results by: stars | name"),
    ] = "stars",
) -> None:
    """Search the registry for AI tools.

    Examples:
        aitool search "code assistant"
        aitool search --tags llm --tags local
        aitool search ollama --sort name
    """
    engine = Engine(AppConfig())
    results = engine.search(query, tags=tags, sort_by=sort)

    if not results:
        print_warning(
            f"No results for query {query!r}." + (f" (tags: {tags})" if tags else ""),
        )
        print_info("Try broader search terms or run 'aitool list' to see all tools.")
        raise typer.Exit(0)

    table = Table(
        title=f"[bold]Search results[/bold] — {len(results)} tool(s)",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )
    table.add_column("Name", style="bold", min_width=10)
    table.add_column("Category", style="magenta", min_width=14)
    table.add_column("Stars", justify="right", style="yellow", min_width=6)
    table.add_column("Tags", style="dim", min_width=20)
    table.add_column("Description", min_width=40)

    plugins_dir = engine.plugins_dir
    for entry in results:
        installed = (plugins_dir / entry.name).exists()
        name_cell = f"[bold]{entry.name}[/bold] {'[green]installed[/green]' if installed else ''}"
        stars = f"{entry.stars:,}" if entry.stars else "-"
        tags_str = ", ".join(entry.tags[:4])
        if len(entry.tags) > 4:
            tags_str += f" +{len(entry.tags) - 4}"

        table.add_row(
            name_cell,
            entry.category,
            stars,
            tags_str,
            entry.description_short,
        )

    console.print(table)
