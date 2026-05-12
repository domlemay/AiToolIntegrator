"""Plugin installation: clone repo, create venv, install deps, run install.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import yaml
from git import InvalidGitRepositoryError, Repo
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from aitoolintegrator.core.config import RegistryEntry
from aitoolintegrator.core.registry import get_entry
from aitoolintegrator.utils.git import clone_repo
from aitoolintegrator.utils.logger import get_logger, print_error, print_success
from aitoolintegrator.utils.venv import create_venv, install_requirements

logger = get_logger(__name__)


def _make_progress() -> Progress:
    """Build a Rich Progress instance for installation output."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=False,
    )


def _generate_plugin_yaml(entry: RegistryEntry, plugin_dir: Path) -> None:
    """Generate a plugin.yaml manifest from a registry entry.

    Args:
        entry: The registry entry for this tool.
        plugin_dir: The plugin's root directory.
    """
    manifest_data = {
        "name": entry.name,
        "version": entry.version,
        "spec_version": "1.0.0",
        "display_name": entry.name.capitalize(),
        "description": {
            "short": entry.description_short,
            "long": entry.description_long,
        },
        "source": {
            "repo": entry.repo,
            "branch": "main",
        },
        "category": entry.category,
        "tags": entry.tags,
        "entry": {
            "module": "run.py",
            "function": "run",
            "type": "python",
        },
        "install": {
            "method": "auto",
            "script": "install.py",
            "requirements": "requirements.txt",
        },
        "requirements": {
            "python": ">=3.11",
            "platforms": entry.platforms,
            "gpu": entry.requires_gpu,
            "min_ram_gb": entry.min_ram_gb,
        },
        "isolation": {"type": "venv"},
    }
    manifest_path = plugin_dir / "plugin.yaml"
    with manifest_path.open("w", encoding="utf-8") as fh:
        yaml.dump(manifest_data, fh, default_flow_style=False, sort_keys=False)
    logger.debug("Generated plugin.yaml at %s", manifest_path)


def _run_install_script(plugin_dir: Path, config: dict[str, Any]) -> bool:
    """Execute a plugin's install.py script if present.

    Args:
        plugin_dir: The plugin's root directory.
        config: Installation config dict passed to install().

    Returns:
        True if the script ran successfully or was absent.
    """
    install_script = plugin_dir / "install.py"
    if not install_script.exists():
        return True

    spec = importlib.util.spec_from_file_location("plugin_install", str(install_script))
    if spec is None or spec.loader is None:
        logger.warning("Could not load install.py from %s", plugin_dir)
        return False

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        if hasattr(module, "install"):
            return bool(module.install(str(plugin_dir), config))
        return True
    except Exception as exc:
        logger.error("install.py raised an error: %s", exc)
        return False


def install_plugin(
    tool_name: str,
    plugins_dir: Path,
    registry_path: Path | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Install a tool plugin end-to-end.

    Flow:
        1. Lookup tool in registry
        2. Create plugin directory
        3. Clone repo to plugins/<tool>/src/
        4. Create venv at plugins/<tool>/.venv/
        5. Install requirements.txt if present
        6. Run install.py if present
        7. Generate plugin.yaml

    Args:
        tool_name: Registry slug for the tool to install.
        plugins_dir: Base directory where plugins are installed.
        registry_path: Optional override for tools.json path.
        config: Optional config dict forwarded to install.py.

    Returns:
        True on success, False on failure.
    """
    entry = get_entry(tool_name, registry_path)
    if entry is None:
        print_error(
            f"Tool '{tool_name}' not found in registry.",
            suggestion="Run 'aitool search' to browse available tools.",
        )
        return False

    plugin_dir = plugins_dir / tool_name
    src_dir = plugin_dir / "src"
    venv_dir = plugin_dir / ".venv"

    with _make_progress() as progress:
        # Step 1: Create plugin directory
        task = progress.add_task("Creating plugin directory…", total=7)
        plugin_dir.mkdir(parents=True, exist_ok=True)
        progress.advance(task)

        # Step 2: Clone repository
        progress.update(task, description=f"Cloning {entry.repo}…")
        try:
            clone_repo(entry.repo, src_dir, branch="main")
        except RuntimeError as exc:
            print_error(f"Clone failed: {exc}")
            return False
        progress.advance(task)

        # Step 3: Create venv
        progress.update(task, description="Creating virtual environment…")
        try:
            create_venv(venv_dir)
        except RuntimeError as exc:
            print_error(f"venv creation failed: {exc}")
            return False
        progress.advance(task)

        # Step 4: Install requirements
        req_file = src_dir / "requirements.txt"
        if req_file.exists():
            progress.update(task, description="Installing dependencies…")
            try:
                install_requirements(venv_dir, req_file)
            except (RuntimeError, FileNotFoundError) as exc:
                print_error(f"Dependency installation failed: {exc}")
                return False
        else:
            progress.update(task, description="No requirements.txt found, skipping…")
        progress.advance(task)

        # Step 5: Run install.py
        progress.update(task, description="Running install script…")
        install_ok = _run_install_script(src_dir, config or {})
        if not install_ok:
            print_error("install.py reported failure.", suggestion="Check the plugin's install.py.")
        progress.advance(task)

        # Step 6: Generate plugin.yaml
        progress.update(task, description="Generating plugin manifest…")
        _generate_plugin_yaml(entry, plugin_dir)
        progress.advance(task)

        progress.update(task, description="Done!", completed=7)

    print_success(f"'{tool_name}' installed successfully to {plugin_dir}")
    return True


def update_plugin(tool_name: str, plugins_dir: Path) -> bool:
    """Update an installed plugin by pulling the latest source and reinstalling deps.

    Flow:
        1. Verify plugin is installed and src/ is a git repo
        2. Fetch latest commits (shallow) and reset to origin/<branch>
        3. Reinstall requirements.txt if present
        4. Re-run install.py hook if present

    Args:
        tool_name: Registry slug for the tool to update.
        plugins_dir: Base directory where plugins are installed.

    Returns:
        True on success, False on failure.
    """
    plugin_dir = plugins_dir / tool_name
    src_dir = plugin_dir / "src"
    venv_dir = plugin_dir / ".venv"

    if not plugin_dir.exists():
        print_error(
            f"'{tool_name}' is not installed.",
            suggestion="Run 'aitool install <tool>' first.",
        )
        return False

    if not src_dir.exists():
        print_error(
            f"Source directory missing for '{tool_name}'.",
            suggestion=f"Try: aitool uninstall {tool_name} && aitool install {tool_name}",
        )
        return False

    with _make_progress() as progress:
        task = progress.add_task(f"Updating '{tool_name}'…", total=4)

        # Step 1: git fetch + reset
        progress.update(task, description="Pulling latest source…")
        try:
            repo = Repo(str(src_dir))
            origin = repo.remotes.origin
            origin.fetch(depth=1)
            repo.git.reset("--hard", "FETCH_HEAD")
            logger.debug("Pulled latest commits for %s", tool_name)
        except InvalidGitRepositoryError:
            print_error(
                f"'{src_dir}' is not a git repository.",
                suggestion=f"Try: aitool uninstall {tool_name} && aitool install {tool_name}",
            )
            return False
        except Exception as exc:
            print_error(f"Git pull failed: {exc}")
            return False
        progress.advance(task)

        # Step 2: Reinstall requirements
        req_file = src_dir / "requirements.txt"
        if req_file.exists() and venv_dir.exists():
            progress.update(task, description="Reinstalling dependencies…")
            try:
                install_requirements(venv_dir, req_file)
            except (RuntimeError, FileNotFoundError) as exc:
                print_error(f"Dependency reinstall failed: {exc}")
                return False
        progress.advance(task)

        # Step 3: Re-run install.py hook
        progress.update(task, description="Running install hook…")
        _run_install_script(src_dir, {})
        progress.advance(task)

        progress.update(task, description="Done!", completed=4)

    print_success(f"'{tool_name}' updated successfully.")
    return True


def uninstall_plugin(tool_name: str, plugins_dir: Path) -> bool:
    """Remove an installed plugin directory.

    Args:
        tool_name: Tool slug to uninstall.
        plugins_dir: Base directory where plugins are installed.

    Returns:
        True on success, False if the plugin was not installed.
    """
    import shutil

    plugin_dir = plugins_dir / tool_name
    if not plugin_dir.exists():
        print_error(
            f"'{tool_name}' is not installed.",
            suggestion="Run 'aitool list --installed' to see installed tools.",
        )
        return False

    # Run uninstall hook if present
    install_script = plugin_dir / "src" / "install.py"
    if install_script.exists():
        spec = importlib.util.spec_from_file_location("plugin_install", str(install_script))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)  # type: ignore[union-attr]
                if hasattr(module, "uninstall"):
                    module.uninstall(str(plugin_dir))
            except Exception as exc:
                logger.warning("uninstall hook failed: %s", exc)

    shutil.rmtree(plugin_dir)
    print_success(f"'{tool_name}' uninstalled.")
    return True
