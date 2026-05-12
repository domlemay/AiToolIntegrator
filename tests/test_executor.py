"""Tests for core.executor — plugin loading and execution."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aitoolintegrator.core.executor import (
    _load_config_yaml,
    _load_manifest,
    _merge_config,
    run_plugin,
)

VALID_MANIFEST = {
    "name": "test-tool",
    "version": "1.0.0",
    "spec_version": "1.0.0",
    "display_name": "Test Tool",
    "description": {
        "short": "A test tool",
        "long": "Long description.",
    },
    "source": {"repo": "https://github.com/test/test-tool"},
    "category": "dev-tool",
    "tags": ["test"],
    "entry": {"module": "run.py", "function": "run", "type": "python"},
    "install": {"method": "auto"},
    "requirements": {"python": ">=3.11", "platforms": ["linux"], "gpu": False, "min_ram_gb": 1},
    "isolation": {"type": "venv"},
}


@pytest.fixture()
def plugin_dir(tmp_path: Path) -> Path:
    d = tmp_path / "plugins" / "test-tool"
    d.mkdir(parents=True)
    return d


@pytest.fixture()
def plugin_with_manifest(plugin_dir: Path) -> Path:
    (plugin_dir / "plugin.yaml").write_text(yaml.dump(VALID_MANIFEST), encoding="utf-8")
    return plugin_dir


class TestLoadManifest:
    def test_loads_valid_manifest(self, plugin_with_manifest: Path) -> None:
        from aitoolintegrator.core.config import PluginManifest

        manifest = _load_manifest(plugin_with_manifest)
        assert manifest is not None
        assert isinstance(manifest, PluginManifest)
        assert manifest.name == "test-tool"

    def test_returns_none_when_missing(self, plugin_dir: Path) -> None:
        manifest = _load_manifest(plugin_dir)
        assert manifest is None

    def test_returns_none_on_invalid_yaml(self, plugin_dir: Path) -> None:
        (plugin_dir / "plugin.yaml").write_text("name: bad\n  invalid: yaml", encoding="utf-8")
        manifest = _load_manifest(plugin_dir)
        assert manifest is None


class TestLoadConfigYaml:
    def test_returns_empty_when_missing(self, plugin_dir: Path) -> None:
        result = _load_config_yaml(plugin_dir)
        assert result == {}

    def test_loads_config_dict(self, plugin_dir: Path) -> None:
        (plugin_dir / "config.yaml").write_text(
            "model: llama3\ntemperature: 0.7\n", encoding="utf-8"
        )
        result = _load_config_yaml(plugin_dir)
        assert result["model"] == "llama3"
        assert result["temperature"] == pytest.approx(0.7)

    def test_returns_empty_on_invalid_yaml(self, plugin_dir: Path) -> None:
        (plugin_dir / "config.yaml").write_text(":\n  bad: yaml\n  - nope", encoding="utf-8")
        result = _load_config_yaml(plugin_dir)
        assert result == {}


class TestMergeConfig:
    def test_manifest_defaults_present(self, plugin_with_manifest: Path) -> None:
        from aitoolintegrator.core.config import PluginManifest

        manifest = PluginManifest.model_validate(VALID_MANIFEST)
        result = _merge_config(manifest, {}, [])
        assert result["name"] == "test-tool"

    def test_config_yaml_overrides_defaults(self, plugin_with_manifest: Path) -> None:
        from aitoolintegrator.core.config import PluginManifest

        manifest = PluginManifest.model_validate(VALID_MANIFEST)
        result = _merge_config(manifest, {"model": "mistral"}, [])
        assert result["model"] == "mistral"

    def test_cli_args_override_config_yaml(self, plugin_with_manifest: Path) -> None:
        from aitoolintegrator.core.config import PluginManifest

        manifest = PluginManifest.model_validate(VALID_MANIFEST)
        result = _merge_config(manifest, {"model": "mistral"}, ["model=llama3"])
        assert result["model"] == "llama3"

    def test_flag_args_set_to_true(self) -> None:
        from aitoolintegrator.core.config import PluginManifest

        manifest = PluginManifest.model_validate(VALID_MANIFEST)
        result = _merge_config(manifest, {}, ["--verbose"])
        assert result.get("verbose") is True


class TestRunPlugin:
    def test_fails_when_not_installed(self, tmp_path: Path) -> None:
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        result = run_plugin("nonexistent", plugins_dir)
        assert result is False

    def test_runs_plugin_successfully(self, plugin_with_manifest: Path) -> None:
        plugins_dir = plugin_with_manifest.parent
        # Create a minimal run.py
        run_py = plugin_with_manifest / "run.py"
        run_py.write_text(
            "def run(config, args=None):\n"
            '    return {"status": "success", "output": "ok", "metadata": {}}\n'
        )
        result = run_plugin("test-tool", plugins_dir)
        assert result is True

    def test_fails_on_run_error(self, plugin_with_manifest: Path) -> None:
        plugins_dir = plugin_with_manifest.parent
        run_py = plugin_with_manifest / "run.py"
        run_py.write_text('def run(config, args=None):\n    raise ValueError("boom")\n')
        result = run_plugin("test-tool", plugins_dir)
        assert result is False

    def test_fails_when_no_run_py(self, plugin_with_manifest: Path) -> None:
        plugins_dir = plugin_with_manifest.parent
        result = run_plugin("test-tool", plugins_dir)
        assert result is False

    def test_handles_error_status(self, plugin_with_manifest: Path) -> None:
        plugins_dir = plugin_with_manifest.parent
        run_py = plugin_with_manifest / "run.py"
        run_py.write_text(
            "def run(config, args=None):\n"
            '    return {"status": "error", "output": "fail", "metadata": {}}\n'
        )
        result = run_plugin("test-tool", plugins_dir)
        assert result is False
