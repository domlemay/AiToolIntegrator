<div align="center">

# AiToolIntegrator

**The universal AI tools package manager**

*Discover, install, and orchestrate AI open-source tools — one CLI to rule them all.*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Tests](https://img.shields.io/badge/tests-79%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-74%25-yellowgreen)]()

[English](#english) · [Français](README.fr.md)

</div>

---

## Table of Contents

- [Vision](#vision)
- [Why AiToolIntegrator?](#why-aitoolintegrator)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Plugin System](#plugin-system)
- [Built-in Registry](#built-in-registry)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Vision

The AI open-source ecosystem is fragmented. Every tool has its own installation process, its own dependencies, its own interface. Managing five different tools means five different workflows, five potential dependency conflicts, and five sets of documentation to remember.

**AiToolIntegrator** solves this by acting as a universal abstraction layer:

```
┌──────────────────────────────────────────────┐
│            Developer / User                  │
└──────────────────┬───────────────────────────┘
                   │
          ┌────────▼────────┐
          │   aitool CLI    │  ← single interface
          └────────┬────────┘
                   │
     ┌─────────────▼─────────────┐
     │       Core Engine         │
     │  Installer  ·  Executor   │
     │  Registry   ·  Doctor     │
     └─────────────┬─────────────┘
                   │
    ┌──────────────▼──────────────┐
    │     Plugin System V1        │
    │  Ollama · Aider · Fabric    │
    │  Ruflo  · Caveman  · ...    │
    └─────────────────────────────┘
```

One command to search, install, run, and manage any AI tool — with automatic dependency isolation per plugin.

---

## Why AiToolIntegrator?

| Problem | AiToolIntegrator Solution |
|---------|--------------------------|
| Every tool has a different install process | `aitool install <tool>` — always the same |
| Dependency conflicts between tools | Each plugin gets its own isolated `venv` |
| Hard to discover good AI tools | Searchable registry with tags, stars, categories |
| No standard interface to run tools | Unified `run(config, args)` contract for all plugins |
| Can't verify a tool is working correctly | `aitool doctor` validates every installed plugin |

---

## Architecture

```
aitoolintegrator/
├── cli/
│   ├── main.py                 # Typer app, all commands registered here
│   └── commands/
│       ├── search.py           # aitool search
│       ├── install.py          # aitool install
│       ├── update.py           # aitool update
│       ├── uninstall.py        # aitool uninstall
│       ├── list_tools.py       # aitool list
│       ├── run.py              # aitool run
│       ├── info.py             # aitool info
│       ├── refresh.py          # aitool refresh
│       └── doctor.py           # aitool doctor
├── core/
│   ├── engine.py               # Central orchestrator — all operations go through here
│   ├── installer.py            # Clone + venv + deps + install.py hook
│   ├── executor.py             # Dynamic plugin loading + run()
│   ├── registry.py             # Read/search tools.json
│   └── config.py               # Pydantic v2 models (PluginManifest, RegistryEntry, ...)
├── plugins/                    # Installed plugins live here (gitignored)
│   └── <tool_name>/
│       ├── plugin.yaml         # Manifest (auto-generated on install)
│       ├── run.py              # Plugin entrypoint
│       ├── .venv/              # Isolated virtual environment
│       └── src/                # Cloned source code
├── registry/
│   ├── tools.json              # Static tool catalog (12 tools included)
│   └── schema.json             # JSON Schema for validation
└── utils/
    ├── git.py                  # GitPython helpers
    ├── venv.py                 # venv creation/management
    ├── http.py                 # httpx async client
    └── logger.py               # Rich-based structured logging
```

### How installation works

```
aitool install aider
       │
       ├─ 1. Registry lookup    → find "aider" in tools.json
       ├─ 2. Clone repo         → git clone → plugins/aider/src/
       ├─ 3. Create venv        → python -m venv plugins/aider/.venv/
       ├─ 4. Install deps       → pip install -r requirements.txt (in venv)
       ├─ 5. Run install hook   → execute install.py if present
       └─ 6. Generate manifest  → write plugins/aider/plugin.yaml
```

### How execution works

```
aitool run aider
       │
       ├─ 1. Verify installed   → plugins/aider/ exists?
       ├─ 2. Load manifest      → parse + validate plugin.yaml
       ├─ 3. Merge config       → plugin.yaml defaults < config.yaml < CLI args
       ├─ 4. Import module      → importlib.util.spec_from_file_location(run.py)
       └─ 5. Call run()         → run(config, args) → display result
```

---

## Tech Stack

| Component | Library | Role |
|-----------|---------|------|
| CLI framework | [Typer](https://typer.tiangolo.com/) | Command-line interface with type hints |
| Terminal UI | [Rich](https://rich.readthedocs.io/) | Tables, progress bars, panels, colors |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) | Config and plugin manifest validation |
| Git integration | [GitPython](https://gitpython.readthedocs.io/) | Repository cloning |
| HTTP client | [httpx](https://www.python-httpx.org/) | Async HTTP requests |
| Config files | [PyYAML](https://pyyaml.org/) | YAML parsing for plugin manifests |
| Testing | [pytest](https://pytest.org/) | Test suite with ≥70% coverage target |
| Linting | [Ruff](https://docs.astral.sh/ruff/) | Fast linter + formatter |

---

## Installation

### Requirements

- Python 3.11 or higher
- pip
- Git (for cloning plugins)

### Install from PyPI (coming soon)

```bash
pip install aitoolintegrator
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/domlemay/AiToolIntegrator
cd AiToolIntegrator

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify the installation
aitool --help
```

### Install in a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Quick Start

```bash
# 1. Browse the tool catalog (12 tools)
aitool list

# 2. Search for a specific tool or category
aitool search "code assistant"
aitool search --tags llm --tags local

# 3. Get detailed info before installing
aitool info ollama

# 4. Install a tool
aitool install aider

# 5. Run the tool
aitool run aider

# 6. Update a plugin to its latest version
aitool update aider

# 7. Refresh star counts from GitHub
aitool refresh

# 8. Check all your plugins are healthy
aitool doctor
```

---

## Command Reference

### `aitool search <query>`

Search the registry by name, description, tags, or category.

```bash
aitool search "llm"
aitool search "code" --tags git
aitool search "" --tags local --tags privacy --sort stars
aitool search "" --sort name
```

| Option | Short | Description |
|--------|-------|-------------|
| `--tags TAG` | `-t` | Filter by tag. Repeatable — all tags must match |
| `--sort stars\|name` | `-s` | Sort results (default: `stars`) |

**Output:** Rich table with name, category, star count, tags, and short description. Installed tools are highlighted.

---

### `aitool install <tool>`

Install a tool from the registry with full isolation.

```bash
aitool install ollama
aitool install aider
aitool install fabric
```

**What happens:**
1. Looks up the tool in `registry/tools.json`
2. Clones the repository to `plugins/<tool>/src/`
3. Creates a dedicated virtual environment at `plugins/<tool>/.venv/`
4. Installs `requirements.txt` inside the venv (if present)
5. Runs `install.py` custom hook (if present)
6. Generates `plugins/<tool>/plugin.yaml` manifest

A Rich progress bar tracks each step.

---

### `aitool list`

List tools with their installation status.

```bash
aitool list                  # all tools in the registry
aitool list --installed      # only installed tools
```

| Option | Short | Description |
|--------|-------|-------------|
| `--installed` | `-i` | Show only installed tools |

**Output:** Rich table with status indicator, name, version, category, stars, and description.

---

### `aitool info <tool>`

Display a full information panel for any registry tool.

```bash
aitool info ollama
aitool info aider
aitool info fabric
```

**Output:**
- Rich panel with short and long descriptions
- Metadata table: status, version, category, tags, repository, license, stars, platform requirements

---

### `aitool run <tool> [args...]`

Execute an installed plugin.

```bash
aitool run caveman
aitool run aider --model gpt-4o
aitool run fabric --pattern summarize
```

Extra arguments after the tool name are forwarded directly to the plugin's `run(config, args)` function. Arguments in `key=value` format are parsed into the config dict; flags like `--verbose` are set to `True`.

**Config merge priority (lowest → highest):**
```
plugin.yaml defaults  →  config.yaml  →  CLI args
```

---

### `aitool update <tool>`

Pull the latest source and reinstall dependencies for an installed plugin.

```bash
aitool update aider          # update a single tool
aitool update --all          # update every installed plugin
```

| Option | Description |
|--------|-------------|
| `--all` | Update every installed plugin in one pass |

**What happens:**
1. `git fetch --depth=1` + `git reset --hard FETCH_HEAD` in `src/`
2. Reinstalls `requirements.txt` if present
3. Re-runs `install.py` hook if present

---

### `aitool refresh`

Fetch current GitHub star counts and update the local registry file.

```bash
aitool refresh                           # anonymous (60 req/hr limit)
aitool refresh --token ghp_xxxxx         # with token (5 000 req/hr)
GITHUB_TOKEN=ghp_xxxxx aitool refresh    # via environment variable
```

| Option | Short | Description |
|--------|-------|-------------|
| `--token TOKEN` | `-t` | GitHub personal access token (or set `GITHUB_TOKEN`) |

All repository calls are made **concurrently** (`asyncio.gather`). The registry file is updated in-place and a Rich table shows the before/after delta for each tool.

---

### `aitool uninstall <tool>`

Remove an installed plugin completely.

```bash
aitool uninstall aider           # prompts for confirmation
aitool uninstall aider --yes     # skip confirmation
```

| Option | Short | Description |
|--------|-------|-------------|
| `--yes` | `-y` | Skip the confirmation prompt |

The uninstall hook (`uninstall()` in `install.py`) is called before deletion if present.

---

### `aitool doctor [tool]`

Validate plugin health.

```bash
aitool doctor              # check all installed plugins
aitool doctor aider        # check a specific plugin
```

**Checks performed:**
- `plugin.yaml` exists and passes Pydantic validation
- Virtual environment exists and has a working Python binary
- `run.py` entrypoint is present

**Output:** Rich table with OK / FAIL status per plugin, listing each issue found.

---

## Plugin System

### Plugin directory structure

```
plugins/<tool_name>/
├── plugin.yaml         # REQUIRED — metadata manifest (Spec V1)
├── run.py              # REQUIRED — execution entrypoint
├── install.py          # OPTIONAL — custom install/uninstall script
├── config.yaml         # OPTIONAL — default configuration values
├── requirements.txt    # OPTIONAL — pip dependencies (installed in .venv)
├── .venv/              # AUTO — isolated virtual environment
└── src/                # AUTO — cloned source code
```

### plugin.yaml schema

```yaml
name: my-tool                    # unique slug (lowercase, hyphens/underscores)
version: "1.0.0"                 # semver
spec_version: "1.0.0"            # plugin spec version (always 1.0.0)
display_name: "My Tool"          # human-readable name

description:
  short: "One-line description"
  long: |
    Detailed multi-line description. Explain what the tool does,
    why it is useful, and who should use it.

source:
  repo: https://github.com/you/my-tool
  branch: main

category: dev-tool               # see valid categories below
tags: [utility, example]

entry:
  module: run.py
  function: run
  type: python                   # python | binary

install:
  method: auto                   # auto | script | binary | docker
  requirements: requirements.txt

requirements:
  python: ">=3.11"
  platforms: [windows, macos, linux]
  gpu: false
  min_ram_gb: 2

isolation:
  type: venv                     # venv | docker | none
```

### Valid categories

| Category | Description | Examples |
|----------|-------------|---------|
| `llm-runtime` | Local LLM execution | Ollama, llama.cpp |
| `coding-assistant` | AI coding tools | Aider, gptme |
| `agent-framework` | Multi-agent frameworks | CrewAI, AutoGen |
| `agent-orchestrator` | Agent orchestration | Ruflo |
| `prompt-engineering` | Prompt tools | Fabric, Caveman |
| `image-generation` | Image generation | ComfyUI |
| `speech-to-text` | Audio transcription | Whisper.cpp |
| `rag-framework` | RAG / document chat | PrivateGPT |
| `dev-tool` | General dev tools | Open Interpreter |

### Creating a plugin

#### 1. Create the `run.py` entrypoint

Every plugin **must** expose a `run()` function with this exact signature:

```python
# plugins/my-tool/run.py

def run(config: dict, args: list[str] | None = None) -> dict:
    """
    Args:
        config: Merged configuration dict (manifest + config.yaml + CLI args).
        args:   Extra CLI arguments passed by the user.

    Returns:
        {"status": "success"|"error", "output": Any, "metadata": dict}
    """
    # Your tool logic here
    result = do_something(config.get("param", "default"))

    return {
        "status": "success",
        "output": result,
        "metadata": {"version": config.get("version", "1.0.0")},
    }
```

#### 2. Create `plugin.yaml`

Use the schema above. All `[REQUIRED]` fields must be present.

#### 3. (Optional) Create `install.py`

```python
# plugins/my-tool/install.py

def install(plugin_dir: str, config: dict) -> bool:
    """Custom installation logic. Returns True on success."""
    # Download binaries, configure system, etc.
    return True

def uninstall(plugin_dir: str) -> bool:
    """Custom cleanup on uninstall. Returns True on success."""
    return True
```

#### 4. (Optional) Create `config.yaml`

```yaml
# plugins/my-tool/config.yaml
model: default-model
temperature: 0.7
max_tokens: 1024
```

#### 5. Test your plugin

```bash
aitool doctor my-tool    # validate plugin structure
aitool run my-tool       # execute it
```

---

## Built-in Registry

AiToolIntegrator ships with **12 curated tools** across 6 categories. Run `aitool refresh` to sync star counts from GitHub.

| Tool | Category | Stars | Description |
|------|----------|-------|-------------|
| [whisper](https://github.com/openai/whisper) | speech-to-text | ~75k | OpenAI speech recognition — transcribe and translate 99 languages locally |
| [ollama](https://github.com/ollama/ollama) | llm-runtime | ~130k | Run LLMs locally with a single command |
| [open-interpreter](https://github.com/OpenInterpreter/open-interpreter) | agent-framework | ~55k | Natural language interface to run code on your computer |
| [aider](https://github.com/Aider-AI/aider) | coding-assistant | ~44k | AI pair programming in your terminal, Git-native |
| [llama-index](https://github.com/run-llama/llama_index) | rag-framework | ~37k | Data framework for LLM apps over your own data |
| [autogen](https://github.com/microsoft/autogen) | agent-framework | ~35k | Multi-agent conversation framework by Microsoft Research |
| [fabric](https://github.com/danielmiessler/fabric) | prompt-engineering | ~30k | Modular prompt patterns framework for augmenting human capabilities |
| [crewai](https://github.com/crewAIInc/crewAI) | agent-framework | ~25k | Framework for orchestrating role-playing autonomous AI agents |
| [tabby](https://github.com/TabbyML/tabby) | coding-assistant | ~22k | Self-hosted AI coding assistant with IDE integrations |
| [litellm](https://github.com/BerriAI/litellm) | llm-runtime | ~15k | Unified API gateway for 100+ LLM providers |
| [ruflo](https://github.com/ruvnet/ruflo) | agent-orchestrator | ~2k | Multi-agent orchestration platform for AI coding assistants |
| [caveman](https://github.com/explainx/skills) | prompt-engineering | ~500 | Reduce output tokens ~70% with telegraphic style |

### Adding a tool to the registry

Edit `aitoolintegrator/registry/tools.json` and add an entry following this schema:

```json
{
  "name": "my-tool",
  "version": "1.0.0",
  "description_short": "One-line description (max 120 chars)",
  "description_long": "Detailed description explaining what, why, and who.",
  "repo": "https://github.com/org/my-tool",
  "homepage": "https://my-tool.dev",
  "license": "MIT",
  "stars": 1500,
  "category": "dev-tool",
  "tags": ["tag1", "tag2"],
  "language": "python",
  "platforms": ["windows", "macos", "linux"],
  "requires_gpu": false,
  "min_ram_gb": 2
}
```

Then open a pull request — the entry will be validated automatically against `registry/schema.json`.

---

## Development

### Setup

```bash
git clone https://github.com/domlemay/AiToolIntegrator
cd AiToolIntegrator
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Running tests

```bash
# Run all tests with coverage report
pytest

# Run a specific test file
pytest tests/test_registry.py -v

# Run a specific test class
pytest tests/test_cli.py::TestSearchCommand -v

# Run without coverage (faster)
pytest --no-cov
```

### Linting and formatting

```bash
# Check for linting issues
ruff check .

# Auto-fix fixable issues
ruff check . --fix

# Format code
ruff format .

# Type check
mypy aitoolintegrator
```

### Project conventions

| Aspect | Convention |
|--------|-----------|
| Python version | 3.11+ (match statements, `list[str] \| None` syntax) |
| Type hints | Required on all public functions |
| Docstrings | Google style |
| Commits | [Conventional Commits](https://www.conventionalcommits.org/) |
| Line length | 100 characters |
| Import style | `from __future__ import annotations` in every module |

### Conventional commit types

```
feat:     new feature
fix:      bug fix
docs:     documentation change
test:     add or update tests
refactor: code change that neither fixes a bug nor adds a feature
perf:     performance improvement
chore:    maintenance (deps update, CI, tooling)
```

---

## Contributing

Contributions are welcome! Here is how to get started:

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch**: `git checkout -b feat/my-feature` or `fix/my-bug`
4. **Develop** following the project conventions above
5. **Test**: `pytest` must pass with ≥70% coverage
6. **Lint**: `ruff check .` must report no errors
7. **Open a PR** with a clear title and description

### What you can contribute

| Type | Description | Difficulty |
|------|-------------|------------|
| Bug fix | Fix an existing issue | Easy |
| Documentation | Improve README, docstrings, examples | Easy |
| New registry entry | Add a tool to `registry/tools.json` | Easy |
| New command | Add a CLI command (e.g. `aitool workflow`) | Medium |
| New feature | Installer improvements, pipeline engine | Medium |
| Architecture | Docker isolation, central registry API | Advanced |

---

## Roadmap

- **v0.1** ✅ (current) — Core CLI (9 commands), 12 tools in registry, Plugin Spec V1, GitHub star auto-refresh
- **v0.5** — YAML pipeline engine (`aitool workflow run file.yaml`), 20+ tools
- **v0.8** — Plugin scaffolding (`aitool create-plugin`), Docker isolation
- **v1.0** — Central registry API, community marketplace

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full roadmap.

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

*"The universal AI tools package manager"*

Made with Python, Typer, and Rich.

</div>
