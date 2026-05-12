"""CLI command: aitool update <tool_name> [--all]."""

from __future__ import annotations

from typing import Annotated

import typer

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import print_error, print_info


def update_cmd(
    tool_name: Annotated[
        str,
        typer.Argument(help="Tool slug to update (omit to use --all)."),
    ] = "",
    all_tools: Annotated[
        bool,
        typer.Option("--all", help="Update every installed plugin."),
    ] = False,
) -> None:
    """Pull the latest source and reinstall dependencies for an installed plugin.

    Examples:
        aitool update aider
        aitool update --all
    """
    engine = Engine(AppConfig())

    if not tool_name and not all_tools:
        print_error(
            "Specify a tool name or pass --all.",
            suggestion="Example: aitool update aider  OR  aitool update --all",
        )
        raise typer.Exit(1)

    if all_tools:
        if not engine.plugins_dir.exists():
            print_info("No plugins installed.")
            return
        candidates = [
            d.name
            for d in engine.plugins_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if not candidates:
            print_info("No plugins installed.")
            return
        failed: list[str] = []
        for name in candidates:
            ok = engine.update(name)
            if not ok:
                failed.append(name)
        if failed:
            print_error(f"Failed to update: {', '.join(failed)}")
            raise typer.Exit(1)
    else:
        ok = engine.update(tool_name)
        if not ok:
            raise typer.Exit(1)
