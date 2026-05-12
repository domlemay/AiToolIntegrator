"""Tests for CLI commands using typer.testing.CliRunner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from aitoolintegrator.cli.main import app
from aitoolintegrator.core.config import RegistryEntry


runner = CliRunner()

SAMPLE_ENTRY = RegistryEntry(
    name="test-tool",
    version="1.0.0",
    description_short="A test tool",
    description_long="Long description for test tool.",
    repo="https://github.com/test/test-tool",
    license="MIT",
    stars=100,
    category="dev-tool",
    tags=["test"],
    language="python",
    platforms=["linux"],
    requires_gpu=False,
    min_ram_gb=1,
)


def _make_engine(plugins_dir: Path) -> MagicMock:
    """Build a preconfigured Engine mock."""
    engine = MagicMock()
    engine.plugins_dir = plugins_dir
    engine.search.return_value = [SAMPLE_ENTRY]
    engine.list_tools.return_value = [(SAMPLE_ENTRY, False)]
    engine.get_tool_info.return_value = SAMPLE_ENTRY
    engine.install.return_value = True
    engine.uninstall.return_value = True
    engine.run.return_value = True
    engine.doctor.return_value = {"test-tool": []}
    return engine


class TestSearchCommand:
    @patch("aitoolintegrator.cli.commands.search.Engine")
    def test_search_returns_table(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 0
        assert "test-tool" in result.output

    @patch("aitoolintegrator.cli.commands.search.Engine")
    def test_search_empty_query(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["search", ""])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.search.Engine")
    def test_search_with_tags(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["search", "test", "--tags", "test"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.search.Engine")
    def test_search_sort_name(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["search", "", "--sort", "name"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.search.Engine")
    def test_search_no_results_shows_warning(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        engine = _make_engine(tmp_path / "plugins")
        engine.search.return_value = []
        MockEngine.return_value = engine
        result = runner.invoke(app, ["search", "zzz-not-here"])
        assert result.exit_code == 0


class TestListCommand:
    @patch("aitoolintegrator.cli.commands.list_tools.Engine")
    def test_list_all(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "test-tool" in result.output

    @patch("aitoolintegrator.cli.commands.list_tools.Engine")
    def test_list_installed_flag(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["list", "--installed"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.list_tools.Engine")
    def test_list_empty_installed(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        engine = _make_engine(tmp_path / "plugins")
        engine.list_tools.return_value = []
        MockEngine.return_value = engine
        result = runner.invoke(app, ["list", "--installed"])
        assert result.exit_code == 0


class TestInfoCommand:
    @patch("aitoolintegrator.cli.commands.info.Engine")
    def test_info_existing_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["info", "test-tool"])
        assert result.exit_code == 0
        assert "test-tool" in result.output

    @patch("aitoolintegrator.cli.commands.info.Engine")
    def test_info_missing_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        engine = _make_engine(tmp_path / "plugins")
        engine.get_tool_info.return_value = None
        MockEngine.return_value = engine
        result = runner.invoke(app, ["info", "no-such-tool"])
        assert result.exit_code != 0


class TestInstallCommand:
    @patch("aitoolintegrator.cli.commands.install.Engine")
    def test_install_known_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        MockEngine.return_value = _make_engine(tmp_path / "plugins")
        result = runner.invoke(app, ["install", "test-tool"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.install.Engine")
    def test_install_unknown_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        engine = _make_engine(tmp_path / "plugins")
        engine.get_tool_info.return_value = None
        MockEngine.return_value = engine
        result = runner.invoke(app, ["install", "no-such-tool"])
        assert result.exit_code != 0

    @patch("aitoolintegrator.cli.commands.install.Engine")
    def test_install_failure_exits_1(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        engine = _make_engine(tmp_path / "plugins")
        engine.install.return_value = False
        MockEngine.return_value = engine
        result = runner.invoke(app, ["install", "test-tool"])
        assert result.exit_code != 0


class TestUninstallCommand:
    @patch("aitoolintegrator.cli.commands.uninstall.Engine")
    def test_uninstall_installed_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        (plugins / "test-tool").mkdir()
        MockEngine.return_value = _make_engine(plugins)
        result = runner.invoke(app, ["uninstall", "test-tool", "--yes"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.uninstall.Engine")
    def test_uninstall_not_installed(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "empty_plugins"
        plugins.mkdir()
        MockEngine.return_value = _make_engine(plugins)
        result = runner.invoke(app, ["uninstall", "no-such-tool", "--yes"])
        assert result.exit_code != 0

    @patch("aitoolintegrator.cli.commands.uninstall.Engine")
    def test_uninstall_prompts_without_yes(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        (plugins / "test-tool").mkdir()
        MockEngine.return_value = _make_engine(plugins)
        # Provide 'n' as input to cancel
        result = runner.invoke(app, ["uninstall", "test-tool"], input="n\n")
        assert result.exit_code == 0


class TestDoctorCommand:
    @patch("aitoolintegrator.cli.commands.doctor.Engine")
    def test_doctor_all_healthy(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        (plugins / "test-tool").mkdir()
        MockEngine.return_value = _make_engine(plugins)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.doctor.Engine")
    def test_doctor_specific_tool(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        MockEngine.return_value = _make_engine(plugins)
        result = runner.invoke(app, ["doctor", "test-tool"])
        assert result.exit_code == 0

    @patch("aitoolintegrator.cli.commands.doctor.Engine")
    def test_doctor_reports_issues(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "plugins"
        plugins.mkdir()
        (plugins / "bad-tool").mkdir()
        engine = _make_engine(plugins)
        engine.doctor.return_value = {
            "bad-tool": ["Missing plugin.yaml", "Virtual environment missing"]
        }
        MockEngine.return_value = engine
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code != 0

    @patch("aitoolintegrator.cli.commands.doctor.Engine")
    def test_doctor_no_plugins(self, MockEngine: MagicMock, tmp_path: Path) -> None:
        plugins = tmp_path / "empty"
        plugins.mkdir()
        engine = _make_engine(plugins)
        engine.doctor.return_value = {}
        MockEngine.return_value = engine
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
