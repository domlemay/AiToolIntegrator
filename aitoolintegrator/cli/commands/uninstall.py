"""CLI command: aitool uninstall <tool_name>."""

from __future__ import annotations

from typing import Annotated

import typer

from aitoolintegrator.core.config import AppConfig
from aitoolintegrator.core.engine import Engine
from aitoolintegrator.utils.logger import print_error, print_info, print_warning


def uninstall_cmd(
    tool_name: Annotated[str, typer.Argument(help="Tool name to uninstall")],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt", is_eager=True),
    ] = False,
) -> None:
    """Uninstall a plugin and remove its directory.

    Runs the uninstall hook (if present in install.py) before deleting
    the plugin directory and its virtual environment.

    Examples:
        aitool uninstall aider
        aitool uninstall ollama --yes
    """
    engine = Engine(AppConfig())
    plugin_dir = engine.plugins_dir / tool_name

    if not plugin_dir.exists():
        print_error(
            f"'{tool_name}' is not installed.",
            suggestion="Run 'aitool list --installed' to see installed tools.",
        )
        raise typer.Exit(1)

    if not yes:
        print_warning(f"This will permanently delete {plugin_dir}")
        confirmed = typer.confirm(f"Uninstall '{tool_name}'?", default=False)
        if not confirmed:
            print_info("Uninstall cancelled.")
            raise typer.Exit(0)

    success = engine.uninstall(tool_name)
    if not success:
        raise typer.Exit(1)
