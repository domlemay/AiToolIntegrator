"""Typer application entrypoint — registers all CLI commands."""

from __future__ import annotations

import typer

from aitoolintegrator.cli.commands.doctor import doctor_cmd
from aitoolintegrator.cli.commands.info import info_cmd
from aitoolintegrator.cli.commands.install import install_cmd
from aitoolintegrator.cli.commands.list_tools import list_cmd
from aitoolintegrator.cli.commands.run import run_cmd
from aitoolintegrator.cli.commands.search import search_cmd
from aitoolintegrator.cli.commands.uninstall import uninstall_cmd
from aitoolintegrator.cli.commands.update import update_cmd

app = typer.Typer(
    name="aitool",
    help=(
        "AiToolIntegrator — The universal AI tools package manager.\n\n"
        "Discover, install, and orchestrate AI open-source tools in your workflow."
    ),
    rich_markup_mode="rich",
    no_args_is_help=True,
)

app.command("search")(search_cmd)
app.command("install")(install_cmd)
app.command("update")(update_cmd)
app.command("uninstall")(uninstall_cmd)
app.command("list")(list_cmd)
app.command("run")(run_cmd)
app.command("info")(info_cmd)
app.command("doctor")(doctor_cmd)
