# 🤖 AiToolIntegrator — Prompt Final Claude Code

> Prompt optimisé pour générer le projet complet avec Claude Code.  
> Copier-coller ce prompt tel quel.

---

## Prompt

```
You are a senior Python architect and open-source project creator.
Your task is to generate a complete, production-ready open-source project named "AiToolIntegrator".

═══════════════════════════════════════════════════════════
PROJECT VISION
═══════════════════════════════════════════════════════════

AiToolIntegrator is a CLI tool that allows developers to discover, install,
and orchestrate AI-related open-source tools inside their development workflow.
It acts as a "package manager + orchestrator for AI tools".

The CLI command is: aitool

═══════════════════════════════════════════════════════════
TECH STACK (strict, do not deviate)
═══════════════════════════════════════════════════════════

- Python 3.11+
- Typer (CLI framework)
- Rich (terminal UI: tables, progress bars, panels)
- Pydantic v2 (config validation, plugin.yaml schema)
- GitPython (repo cloning)
- httpx (async HTTP client)
- PyYAML (config parsing)
- pytest (testing)
- Ruff (linting + formatting)

═══════════════════════════════════════════════════════════
PROJECT STRUCTURE (follow exactly)
═══════════════════════════════════════════════════════════

aitoolintegrator/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Typer app, entrypoint
│   └── commands/
│       ├── __init__.py
│       ├── search.py         # aitool search <query>
│       ├── install.py        # aitool install <tool>
│       ├── run.py            # aitool run <tool> [args]
│       ├── list_tools.py     # aitool list
│       ├── info.py           # aitool info <tool>
│       ├── uninstall.py      # aitool uninstall <tool>
│       └── doctor.py         # aitool doctor
├── core/
│   ├── __init__.py
│   ├── engine.py             # Main orchestrator
│   ├── installer.py          # Clone + venv + deps + install.py
│   ├── executor.py           # Dynamic plugin loading + run()
│   ├── registry.py           # Registry read/write/search
│   └── config.py             # Pydantic models for all configs
├── plugins/                  # Installed plugins (gitignored)
│   └── .gitkeep
├── registry/
│   ├── tools.json            # Static registry (≥5 tools)
│   └── schema.json           # JSON Schema for validation
├── utils/
│   ├── __init__.py
│   ├── git.py                # GitPython helpers
│   ├── venv.py               # venv creation/management
│   ├── http.py               # httpx client wrapper
│   └── logger.py             # Rich-based structured logging
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_installer.py
│   ├── test_executor.py
│   └── test_registry.py
├── main.py                   # python -m aitoolintegrator
├── pyproject.toml            # Project config + dependencies
├── README.md
├── LICENSE                   # MIT
└── .gitignore

═══════════════════════════════════════════════════════════
CLI COMMANDS (implement all)
═══════════════════════════════════════════════════════════

1. aitool search <query> [--tags TAG] [--sort stars|name]
   → Search the registry, display results as a Rich table
   → Show: name, short description, stars, tags

2. aitool install <tool_name>
   → Lookup tool in registry
   → Clone repo to plugins/<tool>/src/
   → Create venv at plugins/<tool>/.venv/
   → Install requirements.txt in venv
   → Run install.py if present
   → Display Rich progress bar during installation

3. aitool list [--all | --installed]
   → List tools (all from registry or installed only)
   → Rich table with status indicators

4. aitool run <tool_name> [-- extra_args...]
   → Load plugin.yaml
   → Merge config (defaults + config.yaml + CLI args)
   → Dynamically import run.py
   → Call run(config, args) in the plugin's venv
   → Display output with Rich formatting

5. aitool info <tool_name>
   → Show detailed info panel (Rich Panel)
   → Display both short and long descriptions
   → Show tags, repo, license, requirements

6. aitool uninstall <tool_name>
   → Run uninstall hook if present
   → Delete plugins/<tool>/ directory
   → Confirm with user before deletion

7. aitool doctor [tool_name]
   → Validate all installed plugins (or one specific)
   → Check: plugin.yaml valid, venv exists, run.py exists
   → Report issues with Rich formatting

═══════════════════════════════════════════════════════════
PLUGIN SYSTEM — SPEC V1 (critical, follow exactly)
═══════════════════════════════════════════════════════════

Each installed plugin lives in plugins/<tool_name>/ with this structure:

  plugins/<tool_name>/
  ├── plugin.yaml       # REQUIRED - metadata manifest
  ├── run.py            # REQUIRED - execution entrypoint
  ├── install.py        # OPTIONAL - custom install script
  ├── config.yaml       # OPTIONAL - default configuration
  ├── requirements.txt  # OPTIONAL - pip dependencies
  ├── .venv/            # AUTO-GENERATED - isolated venv
  └── src/              # AUTO-GENERATED - cloned source

plugin.yaml schema (Pydantic model in core/config.py):

  name: str              # unique slug identifier
  version: str           # semver
  spec_version: "1.0.0"  # plugin spec version
  display_name: str      # human-readable name
  description:
    short: str           # one-line description
    long: str            # detailed multi-line description
  source:
    repo: str            # GitHub URL
    branch: str = "main"
  category: str          # one of the official categories
  tags: list[str]
  entry:
    module: str = "run.py"
    function: str = "run"
    type: str = "python"  # python | binary
  install:
    method: str = "auto"  # auto | script
    script: str | None = "install.py"
    requirements: str | None = "requirements.txt"
  requirements:
    python: str = ">=3.11"
    platforms: list[str] = ["windows", "macos", "linux"]
    gpu: bool = False
    min_ram_gb: int = 4
  isolation:
    type: str = "venv"    # venv | docker | none

run.py contract:

  def run(config: dict, args: list[str] | None = None) -> dict:
      """
      Returns: {"status": "success"|"error", "output": Any, "metadata": dict}
      """

install.py contract:

  def install(plugin_dir: str, config: dict) -> bool:
      """Returns True on success."""

  def uninstall(plugin_dir: str) -> bool:
      """Optional cleanup."""

═══════════════════════════════════════════════════════════
REGISTRY (tools.json)
═══════════════════════════════════════════════════════════

Include at least these 5 tools in the initial registry:

1. ruflo
   - repo: https://github.com/ruvnet/ruflo
   - category: agent-orchestrator
   - tags: [orchestration, multi-agent, coding, mcp]
   - short: "Multi-agent orchestration platform for AI coding assistants"

2. caveman
   - repo: https://github.com/explainx/skills
   - category: prompt-engineering
   - tags: [prompt, token-optimization, cost, speed]
   - short: "Prompt skill that reduces ~70% output tokens via telegraphic style"

3. ollama
   - repo: https://github.com/ollama/ollama
   - category: llm-runtime
   - tags: [llm, local, inference, privacy, cli]
   - short: "Run LLMs locally with a single command"

4. aider
   - repo: https://github.com/Aider-AI/aider
   - category: coding-assistant
   - tags: [coding, git, terminal, pair-programming]
   - short: "AI pair programming in your terminal, Git-native"

5. fabric
   - repo: https://github.com/danielmiessler/fabric
   - category: prompt-engineering
   - tags: [prompts, patterns, workflow, modular, cli]
   - short: "Modular prompt patterns framework for augmenting human capabilities"

═══════════════════════════════════════════════════════════
PYDANTIC MODELS (core/config.py)
═══════════════════════════════════════════════════════════

Create strict Pydantic v2 models for:
- PluginManifest (validates plugin.yaml)
- RegistryEntry (validates each tool in tools.json)
- AppConfig (global app configuration)
- PluginConfig (runtime config for a plugin)

Use model_validator and field_validator where appropriate.

═══════════════════════════════════════════════════════════
INSTALLER (core/installer.py)
═══════════════════════════════════════════════════════════

The install flow must be:
1. Lookup tool in registry → get repo URL
2. Create plugins/<tool>/ directory
3. Clone repo → plugins/<tool>/src/
4. Create venv → plugins/<tool>/.venv/
5. If requirements.txt exists → pip install in venv
6. If install.py exists → execute install() function
7. Generate/validate plugin.yaml
8. Show Rich progress bar for each step

═══════════════════════════════════════════════════════════
EXECUTOR (core/executor.py)
═══════════════════════════════════════════════════════════

The execution flow must be:
1. Verify plugin is installed
2. Load and validate plugin.yaml
3. Merge configs: plugin.yaml defaults → config.yaml → CLI args
4. Dynamically import run.py module
5. Call run(config, args)
6. Handle and display the result dict
7. Catch and display errors gracefully with Rich

═══════════════════════════════════════════════════════════
UX REQUIREMENTS
═══════════════════════════════════════════════════════════

- Use Rich throughout for beautiful terminal output
- Progress bars for installation steps
- Tables for search results and tool listings
- Panels for info display
- Colored status indicators (✅ installed, ❌ not found, ⚠️ outdated)
- Structured error messages with suggestions
- --help on every command with clear descriptions

═══════════════════════════════════════════════════════════
TESTING
═══════════════════════════════════════════════════════════

- pytest with ≥70% coverage target
- Test CLI commands (typer.testing.CliRunner)
- Test registry search/lookup
- Test plugin validation (valid + invalid manifests)
- Test installer (mock git clone)
- Test executor (mock plugin execution)

═══════════════════════════════════════════════════════════
PYPROJECT.TOML
═══════════════════════════════════════════════════════════

Use modern Python packaging:
- [build-system] with hatchling or setuptools
- [project.scripts] aitool = "aitoolintegrator.cli.main:app"
- All dependencies declared
- [tool.ruff] configuration
- [tool.pytest] configuration

═══════════════════════════════════════════════════════════
README.MD
═══════════════════════════════════════════════════════════

Professional README with:
- Project description and vision
- Installation instructions (pip install)
- Quick start guide
- Command reference
- Plugin creation guide (how to create a plugin)
- Contributing section
- License (MIT)

═══════════════════════════════════════════════════════════
CONSTRAINTS
═══════════════════════════════════════════════════════════

- Type hints on ALL functions (mypy strict compatible)
- Google-style docstrings on all public functions
- Conventional commits style
- No overengineering — keep it simple but extensible
- Every file must have a module-level docstring
- Handle errors gracefully — never crash without a helpful message
- Python 3.11+ features only (match statements OK, tomllib OK)

Generate ALL files with complete, working code. No placeholders, no TODOs.
```

---

## Utilisation

1. Ouvrir Claude Code (ou tout agent IA compatible)
2. Coller le prompt ci-dessus
3. Laisser l'agent générer le projet complet
4. Vérifier avec `pytest` et `aitool --help`

> **Note** : Ce prompt est conçu pour produire un projet fonctionnel en une seule génération. Ajustez les détails du registry ou des plugins selon vos besoins avant de lancer.
