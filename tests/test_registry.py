"""Tests for core.registry — search, lookup, and validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aitoolintegrator.core.config import RegistryEntry
from aitoolintegrator.core.registry import (
    get_entry,
    is_installed,
    load_registry,
    refresh_stars,
    search_registry,
)

SAMPLE_TOOL = {
    "name": "test-tool",
    "version": "1.0.0",
    "description_short": "A test tool for unit tests",
    "description_long": "A longer description for the test tool used in pytest.",
    "repo": "https://github.com/test/test-tool",
    "license": "MIT",
    "stars": 500,
    "category": "dev-tool",
    "tags": ["test", "unit-test"],
    "language": "python",
    "platforms": ["linux"],
    "requires_gpu": False,
    "min_ram_gb": 1,
}

SAMPLE_TOOL_2 = {
    **SAMPLE_TOOL,
    "name": "another-tool",
    "version": "2.0.0",
    "description_short": "Another tool for testing search",
    "description_long": "Second test tool.",
    "category": "llm-runtime",
    "tags": ["llm", "local"],
    "stars": 1000,
}


@pytest.fixture()
def registry_file(tmp_path: Path) -> Path:
    """Create a temporary tools.json with two sample entries."""
    data = [SAMPLE_TOOL, SAMPLE_TOOL_2]
    p = tmp_path / "tools.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class TestLoadRegistry:
    def test_loads_valid_entries(self, registry_file: Path) -> None:
        entries = load_registry(registry_file)
        assert len(entries) == 2
        assert all(isinstance(e, RegistryEntry) for e in entries)

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_registry(tmp_path / "nonexistent.json")

    def test_skips_invalid_entries(self, tmp_path: Path) -> None:
        data = [SAMPLE_TOOL, {"name": "bad", "version": "x"}]  # missing required fields
        p = tmp_path / "tools.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        entries = load_registry(p)
        # Only the valid entry is returned
        assert len(entries) == 1
        assert entries[0].name == "test-tool"


class TestGetEntry:
    def test_finds_existing_tool(self, registry_file: Path) -> None:
        entry = get_entry("test-tool", registry_file)
        assert entry is not None
        assert entry.name == "test-tool"
        assert entry.version == "1.0.0"

    def test_returns_none_for_missing(self, registry_file: Path) -> None:
        entry = get_entry("nonexistent", registry_file)
        assert entry is None


class TestSearchRegistry:
    def test_search_by_name(self, registry_file: Path) -> None:
        results = search_registry("test-tool", path=registry_file)
        assert any(e.name == "test-tool" for e in results)

    def test_search_by_description(self, registry_file: Path) -> None:
        results = search_registry("unit tests", path=registry_file)
        assert any(e.name == "test-tool" for e in results)

    def test_empty_query_returns_all(self, registry_file: Path) -> None:
        results = search_registry("", path=registry_file)
        assert len(results) == 2

    def test_filter_by_tag(self, registry_file: Path) -> None:
        results = search_registry("", tags=["llm"], path=registry_file)
        assert len(results) == 1
        assert results[0].name == "another-tool"

    def test_sort_by_name(self, registry_file: Path) -> None:
        results = search_registry("", sort_by="name", path=registry_file)
        names = [e.name for e in results]
        assert names == sorted(names)

    def test_sort_by_stars(self, registry_file: Path) -> None:
        results = search_registry("", sort_by="stars", path=registry_file)
        assert results[0].stars >= results[-1].stars

    def test_no_results_returns_empty(self, registry_file: Path) -> None:
        results = search_registry("zzz-totally-not-there", path=registry_file)
        assert results == []

    def test_multiple_tag_filter(self, registry_file: Path) -> None:
        results = search_registry("", tags=["llm", "local"], path=registry_file)
        assert all("llm" in e.tags and "local" in e.tags for e in results)


class TestIsInstalled:
    def test_returns_true_when_dir_exists(self, tmp_path: Path) -> None:
        (tmp_path / "my-tool").mkdir()
        assert is_installed("my-tool", tmp_path) is True

    def test_returns_false_when_dir_absent(self, tmp_path: Path) -> None:
        assert is_installed("no-such-tool", tmp_path) is False


class TestRegistryEntryValidation:
    def test_valid_entry(self) -> None:
        entry = RegistryEntry.model_validate(SAMPLE_TOOL)
        assert entry.name == "test-tool"

    def test_invalid_category_raises(self) -> None:
        from pydantic import ValidationError

        bad = {**SAMPLE_TOOL, "category": "not-a-real-category"}
        with pytest.raises(ValidationError):
            RegistryEntry.model_validate(bad)

    def test_invalid_name_slug_raises(self) -> None:
        from pydantic import ValidationError

        bad = {**SAMPLE_TOOL, "name": "Has Spaces!"}
        with pytest.raises(ValidationError):
            RegistryEntry.model_validate(bad)

    def test_negative_stars_raises(self) -> None:
        from pydantic import ValidationError

        bad = {**SAMPLE_TOOL, "stars": -1}
        with pytest.raises(ValidationError):
            RegistryEntry.model_validate(bad)


class TestRefreshStars:
    def test_updates_stars_in_file(self, registry_file: Path) -> None:
        from unittest.mock import AsyncMock, patch

        with patch(
            "aitoolintegrator.core.registry.fetch_github_stars",
            new=AsyncMock(return_value=9999),
        ):
            report = refresh_stars(registry_file)

        assert "test-tool" in report
        old, new = report["test-tool"]
        assert old == 500
        assert new == 9999

        # Verify the file was updated on disk
        data = json.loads(registry_file.read_text(encoding="utf-8"))
        assert data[0]["stars"] == 9999

    def test_skips_tool_when_api_returns_none(self, registry_file: Path) -> None:
        from unittest.mock import AsyncMock, patch

        with patch(
            "aitoolintegrator.core.registry.fetch_github_stars",
            new=AsyncMock(return_value=None),
        ):
            report = refresh_stars(registry_file)

        # None means API failed — tool should be absent from report
        assert "test-tool" not in report

        # Stars in file should be unchanged
        data = json.loads(registry_file.read_text(encoding="utf-8"))
        assert data[0]["stars"] == 500

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            refresh_stars(tmp_path / "nonexistent.json")
