"""CLI command: aitool run <tool_name> [extra_args...]."""

from __future__ import annotations

from typing import Annotated

import typer

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine


def run_cmd(
    tool_name: Annotated[str, typer.Argument(help="Tool name to run")],
    extra_args: Annotated[
        list[str] | None,
        typer.Argument(help="Extra arguments forwarded to the plugin's run() function"),
    ] = None,
) -> None:
    """Execute an installed plugin's run() function.

    Loads plugin.yaml, merges configuration (manifest defaults → config.yaml → CLI args),
    dynamically imports run.py, and calls run(config, args).

    Examples:
        aitool run caveman
        aitool run aider --model gpt-4o
    """
    engine = Engine(AppConfig())
    success = engine.run(tool_name, extra_args=extra_args or [])
    if not success:
        raise typer.Exit(1)
