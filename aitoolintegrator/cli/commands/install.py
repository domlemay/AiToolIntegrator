"""CLI command: aitool install <tool_name>."""

from __future__ import annotations

from typing import Annotated

import typer

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import print_error, print_info


def install_cmd(
    tool_name: Annotated[str, typer.Argument(help="Tool name from the registry")],
) -> None:
    """Install an AI tool from the registry.

    Clones the repository, creates an isolated virtual environment,
    installs dependencies, and runs the custom install script if present.

    Examples:
        aitool install aider
        aitool install ollama
    """
    print_info(f"Installing '{tool_name}'...")
    engine = Engine(AppConfig())

    entry = engine.get_tool_info(tool_name)
    if entry is None:
        print_error(
            f"'{tool_name}' not found in registry.",
            suggestion="Run 'aitool search' to browse available tools.",
        )
        raise typer.Exit(1)

    success = engine.install(tool_name)
    if not success:
        raise typer.Exit(1)
