"""Main orchestrator — coordinates registry, installer, and executor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aitoolintegrator.core.config import AppConfig, RegistryEntry
from aitoolintegrator.core.executor import run_plugin
from aitoolintegrator.core.installer import install_plugin, uninstall_plugin
from aitoolintegrator.core.registry import get_entry, is_installed, load_registry, search_registry
from aitoolintegrator.utils.logger import get_logger
from aitoolintegrator.utils.venv import venv_exists


logger = get_logger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent


def _resolve_plugins_dir(config: AppConfig) -> Path:
    """Resolve the absolute plugins directory path.

    Args:
        config: Application configuration.

    Returns:
        Absolute Path to the plugins directory.
    """
    p = Path(config.plugins_dir)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def _resolve_registry_path(config: AppConfig) -> Path:
    """Resolve the absolute registry path.

    Args:
        config: Application configuration.

    Returns:
        Absolute Path to tools.json.
    """
    p = Path(config.registry_path)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    return p


class Engine:
    """Central orchestrator for all AiToolIntegrator operations."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialise the engine with application configuration.

        Args:
            config: AppConfig instance. Uses defaults if not provided.
        """
        self.config = config or AppConfig()
        self.plugins_dir = _resolve_plugins_dir(self.config)
        self.registry_path = _resolve_registry_path(self.config)

    # ── Registry ───────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        tags: list[str] | None = None,
        sort_by: str = "stars",
    ) -> list[RegistryEntry]:
        """Search the registry.

        Args:
            query: Search query string.
            tags: Optional tag filters.
            sort_by: Sort field ('stars' or 'name').

        Returns:
            Matching registry entries.
        """
        return search_registry(query, tags=tags, sort_by=sort_by, path=self.registry_path)

    def list_tools(self, installed_only: bool = False) -> list[tuple[RegistryEntry, bool]]:
        """List tools with their installation status.

        Args:
            installed_only: If True, only return installed tools.

        Returns:
            List of (RegistryEntry, is_installed) tuples.
        """
        entries = load_registry(self.registry_path)
        result: list[tuple[RegistryEntry, bool]] = []
        for entry in entries:
            installed = is_installed(entry.name, self.plugins_dir)
            if installed_only and not installed:
                continue
            result.append((entry, installed))
        return result

    def get_tool_info(self, tool_name: str) -> RegistryEntry | None:
        """Look up a single tool in the registry.

        Args:
            tool_name: Tool slug.

        Returns:
            RegistryEntry or None.
        """
        return get_entry(tool_name, self.registry_path)

    # ── Installation ───────────────────────────────────────────────────────

    def install(self, tool_name: str, extra_config: dict[str, Any] | None = None) -> bool:
        """Install a plugin.

        Args:
            tool_name: Registry slug.
            extra_config: Optional extra install config.

        Returns:
            True on success.
        """
        if is_installed(tool_name, self.plugins_dir):
            from aitoolintegrator.utils.logger import print_warning
            print_warning(f"'{tool_name}' is already installed.")
            return True

        return install_plugin(
            tool_name,
            self.plugins_dir,
            registry_path=self.registry_path,
            config=extra_config,
        )

    def uninstall(self, tool_name: str) -> bool:
        """Uninstall a plugin.

        Args:
            tool_name: Registry slug.

        Returns:
            True on success.
        """
        return uninstall_plugin(tool_name, self.plugins_dir)

    # ── Execution ──────────────────────────────────────────────────────────

    def run(self, tool_name: str, extra_args: list[str] | None = None) -> bool:
        """Run an installed plugin.

        Args:
            tool_name: Registry slug.
            extra_args: Extra CLI args forwarded to run().

        Returns:
            True if run() returned success.
        """
        return run_plugin(tool_name, self.plugins_dir, extra_args=extra_args)

    # ── Doctor ─────────────────────────────────────────────────────────────

    def doctor(self, tool_name: str | None = None) -> dict[str, list[str]]:
        """Validate installed plugins and report issues.

        Args:
            tool_name: If given, check only this plugin; else check all.

        Returns:
            Dict mapping tool_name → list of issue strings (empty = healthy).
        """
        import yaml
        from pydantic import ValidationError

        report: dict[str, list[str]] = {}

        if tool_name:
            candidates = [tool_name]
        else:
            candidates = [
                d.name
                for d in self.plugins_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]

        for name in candidates:
            plugin_dir = self.plugins_dir / name
            issues: list[str] = []

            if not plugin_dir.exists():
                issues.append("Plugin directory does not exist")
                report[name] = issues
                continue

            # Check plugin.yaml
            manifest_path = plugin_dir / "plugin.yaml"
            if not manifest_path.exists():
                issues.append("Missing plugin.yaml")
            else:
                try:
                    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                    from aitoolintegrator.core.config import PluginManifest
                    PluginManifest.model_validate(raw)
                except (yaml.YAMLError, ValidationError) as exc:
                    issues.append(f"Invalid plugin.yaml: {exc}")

            # Check venv
            venv_dir = plugin_dir / ".venv"
            if not venv_exists(venv_dir):
                issues.append("Virtual environment missing or corrupt")

            # Check run.py
            run_py = plugin_dir / "run.py"
            if not run_py.exists():
                # Also check src/run.py
                src_run = plugin_dir / "src" / "run.py"
                if not src_run.exists():
                    issues.append("Missing run.py entrypoint")

            report[name] = issues

        return report
