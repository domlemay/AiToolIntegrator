"""CLI command: aitool refresh — update GitHub star counts in the registry."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from rich.table import Table

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import get_output_console, print_error, print_info, print_success


def refresh_cmd(
    token: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            help="GitHub personal access token (or set GITHUB_TOKEN env var).",
            envvar="GITHUB_TOKEN",
        ),
    ] = "",
) -> None:
    """Fetch current GitHub star counts and update the local registry.

    Without a token the GitHub API allows 60 requests/hour. With a token
    (classic or fine-grained, no special scopes needed for public repos)
    the limit rises to 5 000 requests/hour.

    Examples:
        aitool refresh
        aitool refresh --token ghp_xxxxx
        GITHUB_TOKEN=ghp_xxxxx aitool refresh
    """
    resolved_token = token or os.environ.get("GITHUB_TOKEN") or None

    engine = Engine(AppConfig())
    console = get_output_console()

    if not resolved_token:
        print_info(
            "No GitHub token provided — using anonymous API (60 req/hr limit). "
            "Pass --token or set GITHUB_TOKEN to raise the limit."
        )

    print_info(f"Fetching star counts for {engine.registry_path.name}…")

    try:
        report = engine.refresh(token=resolved_token)
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    except OSError as exc:
        print_error(
            f"Cannot write to registry: {exc}",
            suggestion=(
                "The registry may be inside a read-only pip installation. "
                "Set AITOOL_REGISTRY_PATH to a writable copy."
            ),
        )
        raise typer.Exit(1) from exc

    if not report:
        print_info("No star counts were updated (all requests may have failed).")
        return

    table = Table(title="GitHub Star Count Update", show_lines=False)
    table.add_column("Tool", style="bold cyan", no_wrap=True)
    table.add_column("Before", justify="right", style="dim")
    table.add_column("After", justify="right", style="bold green")
    table.add_column("Change", justify="right")

    for name, (old, new) in sorted(report.items(), key=lambda x: x[1][1], reverse=True):
        delta = new - old
        if delta > 0:
            delta_str = f"[green]+{delta:,}[/green]"
        elif delta < 0:
            delta_str = f"[red]{delta:,}[/red]"
        else:
            delta_str = "[dim]—[/dim]"
        table.add_row(name, f"{old:,}", f"{new:,}", delta_str)

    console.print(table)
    print_success(f"Updated {len(report)} tool(s) in {engine.registry_path}")
