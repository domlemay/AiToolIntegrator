"""Tests for core.installer — plugin installation flow."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aitoolintegrator.core.installer import (
    _generate_plugin_yaml,
    _run_install_script,
    install_plugin,
    uninstall_plugin,
    update_plugin,
)

SAMPLE_ENTRY_DATA = {
    "name": "test-tool",
    "version": "1.0.0",
    "description_short": "A test tool",
    "description_long": "Long description.",
    "repo": "https://github.com/test/test-tool",
    "license": "MIT",
    "stars": 0,
    "category": "dev-tool",
    "tags": ["test"],
    "language": "python",
    "platforms": ["linux"],
    "requires_gpu": False,
    "min_ram_gb": 1,
}


@pytest.fixture()
def registry_file(tmp_path: Path) -> Path:
    p = tmp_path / "tools.json"
    p.write_text(json.dumps([SAMPLE_ENTRY_DATA]), encoding="utf-8")
    return p


@pytest.fixture()
def plugins_dir(tmp_path: Path) -> Path:
    d = tmp_path / "plugins"
    d.mkdir()
    return d


class TestGeneratePluginYaml:
    def test_creates_yaml_file(self, tmp_path: Path) -> None:
        import yaml

        from aitoolintegrator.core.config import RegistryEntry

        entry = RegistryEntry.model_validate(SAMPLE_ENTRY_DATA)
        _generate_plugin_yaml(entry, tmp_path)
        yaml_path = tmp_path / "plugin.yaml"
        assert yaml_path.exists()
        data = yaml.safe_load(yaml_path.read_text())
        assert data["name"] == "test-tool"
        assert data["spec_version"] == "1.0.0"
        assert data["description"]["short"] == "A test tool"

    def test_yaml_has_required_keys(self, tmp_path: Path) -> None:
        import yaml

        from aitoolintegrator.core.config import RegistryEntry

        entry = RegistryEntry.model_validate(SAMPLE_ENTRY_DATA)
        _generate_plugin_yaml(entry, tmp_path)
        data = yaml.safe_load((tmp_path / "plugin.yaml").read_text())
        for key in ("name", "version", "spec_version", "description", "source", "category", "tags"):
            assert key in data


class TestRunInstallScript:
    def test_returns_true_when_no_script(self, tmp_path: Path) -> None:
        result = _run_install_script(tmp_path, {})
        assert result is True

    def test_runs_install_function(self, tmp_path: Path) -> None:
        (tmp_path / "install.py").write_text("def install(plugin_dir, config):\n    return True\n")
        result = _run_install_script(tmp_path, {})
        assert result is True

    def test_returns_false_on_exception(self, tmp_path: Path) -> None:
        (tmp_path / "install.py").write_text(
            "def install(plugin_dir, config):\n    raise RuntimeError('boom')\n"
        )
        result = _run_install_script(tmp_path, {})
        assert result is False


class TestInstallPlugin:
    def test_fails_for_unknown_tool(self, plugins_dir: Path, registry_file: Path) -> None:
        result = install_plugin("no-such-tool", plugins_dir, registry_path=registry_file)
        assert result is False

    @patch("aitoolintegrator.core.installer.clone_repo")
    @patch("aitoolintegrator.core.installer.create_venv")
    def test_successful_install(
        self,
        mock_venv: MagicMock,
        mock_clone: MagicMock,
        plugins_dir: Path,
        registry_file: Path,
    ) -> None:
        mock_clone.return_value = MagicMock()
        mock_venv.return_value = None

        result = install_plugin("test-tool", plugins_dir, registry_path=registry_file)
        assert result is True
        assert (plugins_dir / "test-tool").exists()
        assert (plugins_dir / "test-tool" / "plugin.yaml").exists()

    @patch("aitoolintegrator.core.installer.clone_repo")
    def test_fails_when_clone_raises(
        self, mock_clone: MagicMock, plugins_dir: Path, registry_file: Path
    ) -> None:
        mock_clone.side_effect = RuntimeError("clone failed")
        result = install_plugin("test-tool", plugins_dir, registry_path=registry_file)
        assert result is False

    @patch("aitoolintegrator.core.installer.clone_repo")
    @patch("aitoolintegrator.core.installer.create_venv")
    def test_creates_venv(
        self,
        mock_venv: MagicMock,
        mock_clone: MagicMock,
        plugins_dir: Path,
        registry_file: Path,
    ) -> None:
        mock_clone.return_value = MagicMock()
        mock_venv.return_value = None
        install_plugin("test-tool", plugins_dir, registry_path=registry_file)
        mock_venv.assert_called_once()


class TestUninstallPlugin:
    def test_removes_plugin_directory(self, plugins_dir: Path) -> None:
        tool_dir = plugins_dir / "test-tool"
        tool_dir.mkdir()

        result = uninstall_plugin("test-tool", plugins_dir)
        assert result is True
        assert not tool_dir.exists()

    def test_fails_when_not_installed(self, plugins_dir: Path) -> None:
        result = uninstall_plugin("no-such-tool", plugins_dir)
        assert result is False


class TestUpdatePlugin:
    def test_fails_when_not_installed(self, plugins_dir: Path) -> None:
        result = update_plugin("no-such-tool", plugins_dir)
        assert result is False

    def test_fails_when_src_missing(self, plugins_dir: Path) -> None:
        tool_dir = plugins_dir / "test-tool"
        tool_dir.mkdir()
        # No src/ directory — should fail gracefully
        result = update_plugin("test-tool", plugins_dir)
        assert result is False

    @patch("aitoolintegrator.core.installer.install_requirements")
    @patch("aitoolintegrator.core.installer._run_install_script")
    def test_successful_update(
        self,
        mock_install_script: MagicMock,
        mock_req: MagicMock,
        plugins_dir: Path,
    ) -> None:
        tool_dir = plugins_dir / "test-tool"
        src_dir = tool_dir / "src"
        src_dir.mkdir(parents=True)
        (tool_dir / ".venv").mkdir()

        mock_repo = MagicMock()
        mock_req.return_value = None
        mock_install_script.return_value = True

        with patch("aitoolintegrator.core.installer.Repo", return_value=mock_repo):
            result = update_plugin("test-tool", plugins_dir)

        assert result is True
        mock_repo.git.reset.assert_called_once_with("--hard", "FETCH_HEAD")

    def test_fails_on_git_error(self, plugins_dir: Path) -> None:
        from git import GitCommandError

        tool_dir = plugins_dir / "test-tool"
        src_dir = tool_dir / "src"
        src_dir.mkdir(parents=True)

        mock_repo = MagicMock()
        mock_repo.remotes.origin.fetch.side_effect = GitCommandError("fetch", 1)

        with patch("aitoolintegrator.core.installer.Repo", return_value=mock_repo):
            result = update_plugin("test-tool", plugins_dir)

        assert result is False
