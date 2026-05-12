# Contributing to AiToolIntegrator

Thank you for your interest in contributing! This document explains how to get involved, what kinds of contributions are welcome, and the standards we follow.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)
- [Adding a Tool to the Registry](#adding-a-tool-to-the-registry)
- [Creating a Plugin](#creating-a-plugin)

---

## Code of Conduct

This project is open and welcoming. We expect all contributors to:

- Be respectful and constructive in all interactions
- Focus on the technical merits of contributions
- Accept feedback gracefully and give feedback kindly

---

## Ways to Contribute

| Type | Description | Difficulty | Good First Issue? |
|------|-------------|------------|-------------------|
| Bug report | Open a GitHub issue with reproduction steps | Any | — |
| Bug fix | Fix an issue and open a PR | Easy | Yes |
| Documentation | Improve README, docstrings, or docs/ files | Easy | Yes |
| Registry entry | Add a new tool to `registry/tools.json` | Easy | Yes |
| Test coverage | Add missing tests for untested code paths | Easy–Medium | Yes |
| New command | Add a CLI command (e.g. `aitool update`) | Medium | — |
| New feature | Installer improvements, GitHub scraper, etc. | Medium | — |
| Plugin | Create a working plugin for a popular AI tool | Medium | — |
| Architecture | Docker isolation, YAML pipeline engine | Advanced | — |

---

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip

### Clone and install

```bash
git clone https://github.com/domlemay/AiToolIntegrator.git
cd AiToolIntegrator

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### Verify everything works

```bash
# CLI should respond
aitool --help

# All tests should pass
pytest

# Linter should be clean
ruff check .
```

---

## Project Structure

```
aitoolintegrator/
├── cli/commands/       # One file per CLI command — keep commands thin
├── core/               # Business logic — installer, executor, registry, engine
├── utils/              # Standalone helpers — no business logic here
├── registry/           # Static tool catalog (tools.json + schema.json)
├── plugins/            # Installed plugins — gitignored
└── tests/              # pytest test suite
```

**Key principle:** CLI commands should be thin — they call `Engine` methods and display output. Business logic belongs in `core/`.

---

## Coding Standards

### Type hints

All public functions **must** have full type hints. We target mypy strict compatibility.

```python
# Good
def search_registry(query: str, tags: list[str] | None = None) -> list[RegistryEntry]:
    ...

# Bad — missing return type
def search_registry(query, tags=None):
    ...
```

### Docstrings

Use **Google style** docstrings on all public functions and classes.

```python
def install_plugin(tool_name: str, plugins_dir: Path) -> bool:
    """Install a tool plugin end-to-end.

    Args:
        tool_name: Registry slug for the tool to install.
        plugins_dir: Base directory where plugins are installed.

    Returns:
        True on success, False on failure.

    Raises:
        RuntimeError: If the clone or venv creation fails.
    """
```

### Module docstrings

Every file must have a one-line module-level docstring:

```python
"""Registry read, write, and search operations for AiToolIntegrator."""
```

### Imports

Every module must start with:

```python
from __future__ import annotations
```

Use `ruff` import ordering (it handles this automatically with `ruff format`).

### Error handling

- Never crash without a helpful message
- Use `print_error(message, suggestion=...)` from `utils/logger.py`
- Catch specific exceptions, not bare `except Exception`
- Return `False` / `None` from functions rather than raising where it makes sense

```python
# Good
try:
    clone_repo(url, dest)
except RuntimeError as exc:
    print_error(f"Clone failed: {exc}", suggestion="Check your internet connection.")
    return False

# Bad
clone_repo(url, dest)  # lets exceptions propagate uncaught to the user
```

### Line length

100 characters maximum. Configured in `pyproject.toml`.

---

## Testing Requirements

- All PRs must maintain **≥70% overall test coverage**
- New features must include tests
- Bug fixes should include a regression test

### Running tests

```bash
# Full suite with coverage
pytest

# Specific file
pytest tests/test_registry.py -v

# Skip coverage check (for quick iteration)
pytest --no-cov -q
```

### Test patterns

**For core logic** — test the function directly:

```python
def test_search_finds_by_tag(registry_file: Path) -> None:
    results = search_registry("", tags=["llm"], path=registry_file)
    assert all("llm" in e.tags for e in results)
```

**For CLI commands** — use `typer.testing.CliRunner` + mock `Engine`:

```python
@patch("aitoolintegrator.cli.commands.search.Engine")
def test_search_returns_table(self, MockEngine: MagicMock, tmp_path: Path) -> None:
    MockEngine.return_value.search.return_value = [SAMPLE_ENTRY]
    MockEngine.return_value.plugins_dir = tmp_path / "plugins"
    result = runner.invoke(app, ["search", "test"])
    assert result.exit_code == 0
    assert "test" in result.output
```

**For installer** — mock `clone_repo` and `create_venv` to avoid network/FS overhead:

```python
@patch("aitoolintegrator.core.installer.clone_repo")
@patch("aitoolintegrator.core.installer.create_venv")
def test_successful_install(self, mock_venv, mock_clone, ...) -> None:
    mock_clone.return_value = MagicMock()
    mock_venv.return_value = None
    result = install_plugin("test-tool", plugins_dir, registry_path=registry_file)
    assert result is True
```

---

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code change with no functional impact |
| `perf` | Performance improvement |
| `chore` | Maintenance (deps, CI, tooling) |
| `style` | Formatting, whitespace (no logic change) |

### Examples

```
feat(registry): add GitHub star count auto-refresh
fix(installer): handle missing requirements.txt gracefully
docs(readme): add quick start section
test(executor): add edge case for missing run() function
chore(deps): bump pydantic to 2.8.0
```

### Breaking changes

Add `!` after the type and a `BREAKING CHANGE:` footer:

```
feat(plugin-spec)!: rename entry.type values

BREAKING CHANGE: "script" is now "python". Update all plugin.yaml files.
```

---

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Make your changes** following the coding standards above
4. **Run the full check suite locally:**
   ```bash
   ruff check .          # must be clean
   ruff format .         # auto-formats
   pytest                # must pass with ≥70% coverage
   ```
5. **Commit** using conventional commits
6. **Push** your branch and **open a PR** against `main`
7. Fill in the PR template:
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Any breaking changes?

### PR review criteria

- [ ] Code follows project conventions (type hints, docstrings, error handling)
- [ ] Tests added / updated for changed code
- [ ] Coverage ≥70% maintained
- [ ] `ruff check .` passes
- [ ] Commit messages follow conventional commits
- [ ] No unrelated changes mixed in

---

## Adding a Tool to the Registry

The registry is at `aitoolintegrator/registry/tools.json`. Each entry is validated against `registry/schema.json` and the `RegistryEntry` Pydantic model.

### Entry template

```json
{
  "name": "tool-slug",
  "version": "1.0.0",
  "description_short": "One-line description — max 120 chars, no period at end",
  "description_long": "Multi-paragraph description. Explain what the tool does, key features, and who should use it. Be specific and useful.",
  "repo": "https://github.com/org/tool-name",
  "homepage": null,
  "license": "MIT",
  "stars": 5000,
  "category": "dev-tool",
  "tags": ["relevant", "tags", "here"],
  "language": "python",
  "platforms": ["windows", "macos", "linux"],
  "requires_gpu": false,
  "min_ram_gb": 4
}
```

### Name rules

- Must be a slug: lowercase letters, digits, hyphens, underscores
- Must be unique in the registry
- Should match the tool's common name (e.g. `aider`, `ollama`, `fabric`)

### Valid categories

`llm-runtime`, `coding-assistant`, `agent-framework`, `agent-orchestrator`, `prompt-engineering`, `image-generation`, `speech-to-text`, `rag-framework`, `dev-tool`

### Quality criteria for registry entries

- The tool must be open source with a clear license
- The repo must be actively maintained (last commit within 12 months)
- Stars are approximate — use the current count from GitHub
- Tags should be specific and useful for search (3–6 tags recommended)
- `description_long` should explain the value proposition, not just repeat the short description

---

## Creating a Plugin

If you want to contribute a working plugin (an adapter for an existing AI tool), see [PLUGIN_SPEC_V1.md](./PLUGIN_SPEC_V1.md) for the full specification.

### Quick checklist

- [ ] `plugin.yaml` — valid against the spec, passes `aitool doctor`
- [ ] `run.py` — exports `run(config: dict, args: list[str] | None) -> dict`
- [ ] `run()` returns `{"status": "success"|"error", "output": Any, "metadata": dict}`
- [ ] `install.py` — if custom install needed, exports `install(plugin_dir, config) -> bool`
- [ ] `requirements.txt` — all pip dependencies listed
- [ ] Tested with `aitool install`, `aitool run`, and `aitool doctor`

---

## Questions?

- Open a [GitHub Discussion](https://github.com/domlemay/AiToolIntegrator/discussions) for questions and ideas
- Open a [GitHub Issue](https://github.com/domlemay/AiToolIntegrator/issues) for bugs and feature requests
