"""CLI command: aitool doctor [tool_name]."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import get_output_console, print_info, print_success

console = get_output_console()


def doctor_cmd(
    tool_name: Annotated[
        str | None,
        typer.Argument(help="Tool name to check (omit to check all installed plugins)"),
    ] = None,
) -> None:
    """Check the health of installed plugins.

    Validates that each plugin has:
      - A valid plugin.yaml manifest
      - A functioning virtual environment
      - A run.py entrypoint

    Examples:
        aitool doctor
        aitool doctor aider
    """
    engine = Engine(AppConfig())

    installed = (
        [d.name for d in engine.plugins_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if engine.plugins_dir.exists()
        else []
    )

    if not installed and not tool_name:
        print_info("No plugins installed. Run 'aitool install <tool>' to get started.")
        return

    report = engine.doctor(tool_name)

    if not report:
        print_info("Nothing to check.")
        return

    table = Table(
        title="[bold]Plugin Health Report[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )
    table.add_column("Plugin", style="bold", min_width=14)
    table.add_column("Status", justify="center", min_width=8)
    table.add_column("Issues")

    all_healthy = True
    for name, issues in sorted(report.items()):
        if issues:
            all_healthy = False
            status = "[bold red]FAIL[/bold red]"
            issue_text = "\n".join(f"- {i}" for i in issues)
        else:
            status = "[bold green]OK[/bold green]"
            issue_text = "[dim]-[/dim]"

        table.add_row(name, status, issue_text)

    console.print(table)

    if all_healthy:
        print_success("All plugins are healthy!")
    else:
        console.print(
            "\n[yellow]Tip:[/yellow] Run [bold]aitool install <tool>[/bold]"
            " to reinstall a broken plugin."
        )
        raise typer.Exit(1)
