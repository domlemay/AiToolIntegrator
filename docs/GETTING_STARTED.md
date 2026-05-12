# Getting Started with AiToolIntegrator

This guide walks you through everything you need to go from zero to a working setup — including installing the CLI, exploring the registry, and running your first plugin.

---

## Prerequisites

Before you begin, make sure you have:

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.11 or higher | `python --version` |
| pip | any recent | `pip --version` |
| Git | any | `git --version` |

---

## Step 1 — Install AiToolIntegrator

### From source (recommended while in alpha)

```bash
git clone https://github.com/domlemay/AiToolIntegrator.git
cd AiToolIntegrator
pip install -e ".[dev]"
```

### In a virtual environment (recommended)

```bash
git clone https://github.com/domlemay/AiToolIntegrator.git
cd AiToolIntegrator

python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### Verify the installation

```bash
aitool --help
```

You should see the command list:

```
Usage: aitool [OPTIONS] COMMAND [ARGS]...

  AiToolIntegrator — The universal AI tools package manager.

Commands:
  search     Search the registry for AI tools.
  install    Install an AI tool from the registry.
  list       List tools from the registry with their installation status.
  run        Execute an installed plugin's run() function.
  info       Display detailed information about a registry tool.
  uninstall  Uninstall a plugin and remove its directory.
  doctor     Check the health of installed plugins.
```

---

## Step 2 — Explore the Registry

The registry contains the catalog of available AI tools. Start by listing everything:

```bash
aitool list
```

You'll see a table with all 5 built-in tools, their categories, star counts, and descriptions.

### Search for something specific

```bash
# Search by keyword
aitool search "code"

# Filter by tag
aitool search "" --tags llm

# Multiple tags (all must match)
aitool search "" --tags llm --tags local

# Sort alphabetically
aitool search "" --sort name
```

### Get detailed info about a tool

```bash
aitool info ollama
aitool info aider
aitool info fabric
```

This shows the full description, repository link, license, platform requirements, and installation status.

---

## Step 3 — Install a Tool

Let's install **Aider**, an AI pair programming assistant.

```bash
aitool install aider
```

AiToolIntegrator will:
1. Find `aider` in the registry
2. Clone the GitHub repository to `aitoolintegrator/plugins/aider/src/`
3. Create an isolated virtual environment at `aitoolintegrator/plugins/aider/.venv/`
4. Install all dependencies inside that venv
5. Run any custom install script if present
6. Generate the `plugin.yaml` manifest

A progress bar tracks each step. Installation may take a minute depending on the tool's dependencies.

After installation:

```bash
# Verify it's listed as installed
aitool list --installed

# Check its health
aitool doctor aider
```

---

## Step 4 — Run a Plugin

```bash
# Run with no extra arguments
aitool run aider

# Pass arguments to the plugin
aitool run aider --model gpt-4o

# Pass key=value config overrides
aitool run aider model=gpt-4o temperature=0.5
```

The plugin's `run()` function receives a merged config dict (manifest defaults + `config.yaml` values + your CLI arguments) and any extra args you passed.

Output is displayed in a Rich panel showing status, output, and metadata.

---

## Step 5 — Check Plugin Health

```bash
# Check all installed plugins
aitool doctor

# Check a specific plugin
aitool doctor aider
```

Doctor validates:
- `plugin.yaml` exists and passes schema validation
- Virtual environment is intact and has a working Python binary
- `run.py` entrypoint is present

A healthy output looks like:

```
          Plugin Health Report
┌──────────────┬────────┬────────┐
│ Plugin       │ Status │ Issues │
├──────────────┼────────┼────────┤
│ aider        │  OK    │   -    │
└──────────────┴────────┴────────┘
All plugins are healthy!
```

---

## Step 6 — Uninstall a Tool

```bash
# With confirmation prompt
aitool uninstall aider

# Skip confirmation
aitool uninstall aider --yes
```

This removes the entire `plugins/aider/` directory including the virtual environment and cloned source code.

---

## Configuration Reference

### Plugin config priority

When you run a plugin, its configuration is built by merging three sources (lowest to highest priority):

```
plugin.yaml defaults  →  config.yaml  →  CLI arguments
```

**Example:**

If `plugin.yaml` says `model: llama3` and you run `aitool run my-tool model=mistral`, the plugin receives `model: mistral`.

### Environment variables

You can override plugin config values with environment variables prefixed by `AITOOL_<PLUGIN>_`:

```bash
export AITOOL_OLLAMA_MODEL="mistral"
export AITOOL_OLLAMA_TEMPERATURE="0.5"
aitool run ollama
```

### Plugin directory layout

After installing a tool, its directory looks like:

```
aitoolintegrator/plugins/aider/
├── plugin.yaml        # Generated manifest — do not edit manually
├── run.py             # Entrypoint — provided by the plugin or auto-generated
├── install.py         # Custom install script (if the plugin provides one)
├── config.yaml        # Your local config overrides (create this yourself)
├── requirements.txt   # Plugin's pip dependencies
├── .venv/             # Isolated virtual environment (auto-generated)
│   ├── bin/python     # macOS/Linux
│   └── Scripts/python # Windows
└── src/               # Cloned source code from GitHub
    └── ...
```

---

## Common Issues

### `aitool: command not found`

The `aitool` script is installed to your Python environment's `Scripts/` (Windows) or `bin/` (macOS/Linux) folder. Make sure this is in your `PATH`, or activate your virtual environment first.

```bash
# If installed in a venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
aitool --help
```

### Clone fails

If `aitool install` fails during the clone step:

- Check your internet connection
- Verify the repository URL in `registry/tools.json`
- Try cloning manually: `git clone <repo_url>`

### `aitool doctor` shows venv missing

The virtual environment may have been accidentally deleted or the installation interrupted. Reinstall:

```bash
aitool uninstall <tool> --yes
aitool install <tool>
```

### Unicode errors on Windows

If you see `UnicodeEncodeError` in the terminal output, run Python via the module entrypoint which forces UTF-8:

```bash
python -m aitoolintegrator --help
```

Or set the environment variable before running:

```bash
set PYTHONUTF8=1
aitool --help
```

---

## Next Steps

- Read [PLUGIN_SPEC_V1.md](./PLUGIN_SPEC_V1.md) to learn how to create your own plugin
- Read [CONTRIBUTING.md](./CONTRIBUTING.md) to contribute to the project
- Check [ROADMAP.md](./ROADMAP.md) to see what's coming next
- Browse [TOOL_CATALOG.md](./TOOL_CATALOG.md) for the full list of planned integrations
