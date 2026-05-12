"""Dynamic plugin loading and execution for AiToolIntegrator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from rich.panel import Panel

from aitoolintegrator.core.config import PluginManifest
from aitoolintegrator.utils.logger import get_logger, get_output_console, print_error, print_warning

logger = get_logger(__name__)
console = get_output_console()


def _load_manifest(plugin_dir: Path) -> PluginManifest | None:
    """Load and validate a plugin's plugin.yaml.

    Args:
        plugin_dir: Root directory of the plugin.

    Returns:
        Validated PluginManifest, or None if validation fails.
    """
    manifest_path = plugin_dir / "plugin.yaml"
    if not manifest_path.exists():
        print_error(
            f"No plugin.yaml found in {plugin_dir}.",
            suggestion="Run 'aitool doctor' to diagnose plugin issues.",
        )
        return None

    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        return PluginManifest.model_validate(raw)
    except (yaml.YAMLError, ValidationError) as exc:
        print_error(f"Invalid plugin.yaml: {exc}")
        return None


def _load_config_yaml(plugin_dir: Path) -> dict[str, Any]:
    """Load optional config.yaml defaults for a plugin.

    Args:
        plugin_dir: Root directory of the plugin.

    Returns:
        Config dict (empty if file absent or invalid).
    """
    config_path = plugin_dir / "config.yaml"
    if not config_path.exists():
        return {}
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError as exc:
        logger.warning("Could not parse config.yaml: %s", exc)
        return {}


def _merge_config(
    manifest: PluginManifest,
    config_yaml: dict[str, Any],
    cli_args: list[str],
) -> dict[str, Any]:
    """Merge configs in priority order: manifest defaults < config.yaml < CLI args.

    Args:
        manifest: The plugin manifest (lowest priority defaults).
        config_yaml: Values from config.yaml.
        cli_args: Raw CLI extra args (parsed as key=value pairs where possible).

    Returns:
        Merged configuration dict.
    """
    merged: dict[str, Any] = {
        "name": manifest.name,
        "version": manifest.version,
    }
    merged.update(config_yaml)

    # Parse CLI args in key=value format
    for arg in cli_args:
        if "=" in arg:
            key, _, value = arg.partition("=")
            merged[key.lstrip("-")] = value
        else:
            # Flags like --verbose become {"verbose": True}
            merged[arg.lstrip("-")] = True

    return merged


def _load_run_module(plugin_dir: Path, module_name: str) -> Any:  # noqa: ANN401
    """Dynamically import a plugin's run module.

    Args:
        plugin_dir: Root directory of the plugin.
        module_name: Filename of the module (e.g. 'run.py').

    Returns:
        The imported module object.

    Raises:
        ImportError: If the module cannot be loaded.
    """
    module_path = plugin_dir / module_name
    if not module_path.exists():
        raise ImportError(f"Module '{module_name}' not found in {plugin_dir}")

    spec = importlib.util.spec_from_file_location(f"plugin_{plugin_dir.name}", str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _display_result(result: dict[str, Any]) -> None:
    """Display a plugin run() result with Rich formatting.

    Args:
        result: The dict returned by run(config, args).
    """
    status = result.get("status", "unknown")
    output = result.get("output", "")
    metadata = result.get("metadata", {})

    if status == "success":
        color = "green"
        icon = "✅"
    elif status == "error":
        color = "red"
        icon = "❌"
    else:
        color = "yellow"
        icon = "⚠️"

    content = f"[bold {color}]{icon} Status: {status}[/bold {color}]\n\n"

    if isinstance(output, str):
        content += output
    elif isinstance(output, dict):
        for k, v in output.items():
            content += f"[bold]{k}:[/bold] {v}\n"
    else:
        content += str(output)

    if metadata:
        content += "\n\n[dim]Metadata:[/dim]\n"
        for k, v in metadata.items():
            content += f"[dim]  {k}: {v}[/dim]\n"

    console.print(Panel(content, title="[bold]Plugin Output[/bold]", border_style=color))


def run_plugin(
    tool_name: str,
    plugins_dir: Path,
    extra_args: list[str] | None = None,
) -> bool:
    """Execute an installed plugin.

    Flow:
        1. Verify plugin is installed
        2. Load and validate plugin.yaml
        3. Merge configs (manifest defaults → config.yaml → CLI args)
        4. Dynamically import run.py
        5. Call run(config, args)
        6. Display result

    Args:
        tool_name: Tool slug to run.
        plugins_dir: Base plugins directory.
        extra_args: Additional CLI args passed through to run().

    Returns:
        True if run() returned status 'success', False otherwise.
    """
    plugin_dir = plugins_dir / tool_name

    # Step 1: Verify installed
    if not plugin_dir.exists():
        print_error(
            f"'{tool_name}' is not installed.",
            suggestion=f"Run 'aitool install {tool_name}' first.",
        )
        return False

    # Step 2: Load manifest
    manifest = _load_manifest(plugin_dir)
    if manifest is None:
        return False

    # Step 3: Merge config
    config_yaml = _load_config_yaml(plugin_dir)
    config = _merge_config(manifest, config_yaml, extra_args or [])

    # Step 4: Import run module
    try:
        module = _load_run_module(plugin_dir, manifest.entry.module)
    except ImportError as exc:
        print_error(f"Could not load plugin module: {exc}")
        return False

    if not hasattr(module, manifest.entry.function):
        print_error(
            f"Plugin module missing function '{manifest.entry.function}'.",
            suggestion="Ensure run.py exports a run(config, args) function.",
        )
        return False

    # Step 5: Execute
    run_fn = getattr(module, manifest.entry.function)
    try:
        result: dict[str, Any] = run_fn(config, extra_args or [])
    except Exception as exc:
        print_error(f"Plugin raised an exception: {exc}")
        logger.exception("Plugin %s crashed", tool_name)
        return False

    # Step 6: Display result
    if not isinstance(result, dict):
        print_warning(f"Plugin returned unexpected type {type(result).__name__}, wrapping.")
        result = {"status": "success", "output": str(result), "metadata": {}}

    _display_result(result)
    return result.get("status") == "success"
