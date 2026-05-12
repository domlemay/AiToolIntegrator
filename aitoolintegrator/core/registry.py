"""Registry read, write, and search operations for AiToolIntegrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from aitoolintegrator.core.config import RegistryEntry
from aitoolintegrator.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_REGISTRY_PATH = Path(__file__).parent.parent / "registry" / "tools.json"


def load_registry(path: Path | None = None) -> list[RegistryEntry]:
    """Load and validate all entries from the registry JSON file.

    Args:
        path: Path to tools.json. Defaults to the bundled registry.

    Returns:
        List of validated RegistryEntry objects.

    Raises:
        FileNotFoundError: If the registry file does not exist.
        ValueError: If any entry fails Pydantic validation.
    """
    registry_path = path or _DEFAULT_REGISTRY_PATH
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found: {registry_path}")

    raw: list[dict[str, Any]] = json.loads(registry_path.read_text(encoding="utf-8"))
    entries: list[RegistryEntry] = []
    for item in raw:
        try:
            entries.append(RegistryEntry.model_validate(item))
        except ValidationError as exc:
            logger.warning("Skipping invalid registry entry %r: %s", item.get("name"), exc)
    return entries


def get_entry(name: str, path: Path | None = None) -> RegistryEntry | None:
    """Look up a single tool by name in the registry.

    Args:
        name: Tool slug to find.
        path: Optional path override for tools.json.

    Returns:
        The matching RegistryEntry, or None if not found.
    """
    for entry in load_registry(path):
        if entry.name == name:
            return entry
    return None


def search_registry(
    query: str,
    tags: list[str] | None = None,
    sort_by: str = "stars",
    path: Path | None = None,
) -> list[RegistryEntry]:
    """Search the registry by name, description, or tags.

    Args:
        query: Search query string (matched against name, descriptions, tags).
        tags: Optional list of tags to filter by (all must match).
        sort_by: Sort field — 'stars' or 'name'.
        path: Optional path override for tools.json.

    Returns:
        Sorted list of matching RegistryEntry objects.
    """
    q = query.lower().strip()
    entries = load_registry(path)
    results: list[RegistryEntry] = []

    for entry in entries:
        # Text match
        searchable = " ".join(
            [
                entry.name,
                entry.description_short,
                entry.description_long,
                " ".join(entry.tags),
                entry.category,
            ]
        ).lower()

        if q and q not in searchable:
            continue

        # Tag filter (ALL supplied tags must be present)
        if tags:
            entry_tags = {t.lower() for t in entry.tags}
            if not all(t.lower() in entry_tags for t in tags):
                continue

        results.append(entry)

    # Sort
    match sort_by:
        case "name":
            results.sort(key=lambda e: e.name)
        case _:  # stars (default)
            results.sort(key=lambda e: e.stars, reverse=True)

    return results


def is_installed(tool_name: str, plugins_dir: Path) -> bool:
    """Check whether a tool is installed locally.

    Args:
        tool_name: Tool slug.
        plugins_dir: Base plugins directory.

    Returns:
        True if the plugin directory exists, False otherwise.
    """
    plugin_path = plugins_dir / tool_name
    return plugin_path.exists() and plugin_path.is_dir()
