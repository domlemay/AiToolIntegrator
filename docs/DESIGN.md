# AiToolIntegrator — Document de Conception

> **"Le package manager + orchestrateur universel des outils IA"**
>
> Version : 0.1.0 — Mise à jour : 2026-05-12

---

## Vision

AiToolIntegrator est un **CLI open source en Python** permettant de :

- **Découvrir** des outils IA open source via un registre local consultable
- **Installer** automatiquement ces outils avec isolation des dépendances (venv par plugin)
- **Standardiser** leur utilisation via un système de plugins uniforme (Plugin Spec V1)
- **Orchestrer** plusieurs outils dans un workflow unifié (pipelines YAML — roadmap v0.8)

### Pourquoi AiToolIntegrator ?

L'écosystème des outils IA open source est **fragmenté**. Chaque outil a son propre processus d'installation, ses propres dépendances, sa propre interface. AiToolIntegrator agit comme une **couche d'abstraction universelle** : un seul CLI pour les gouverner tous.

```
┌─────────────────────────────────────────────┐
│           Développeur / Utilisateur          │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────▼────────┐
          │   aitool CLI    │  ← Interface unique
          └────────┬────────┘
                   │
     ┌─────────────▼─────────────┐
     │       Core Engine         │
     │  ┌─────┐ ┌──────┐ ┌────┐ │
     │  │Inst.│ │Exec. │ │Reg.│ │
     │  └─────┘ └──────┘ └────┘ │
     └─────────────┬─────────────┘
                   │
    ┌──────────────▼──────────────┐
    │     Plugin System (V1)      │
    │  ┌──────┐ ┌──────┐ ┌─────┐ │
    │  │Ollama│ │Aider │ │Ruflo│ │
    │  └──────┘ └──────┘ └─────┘ │
    └─────────────────────────────┘
```

---

## Architecture réelle (v0.1)

### Structure du projet

```
aitoolintegrator/
├── cli/
│   ├── __init__.py
│   ├── main.py                 # App Typer — enregistre toutes les commandes
│   └── commands/
│       ├── __init__.py
│       ├── search.py           # aitool search <query>
│       ├── install.py          # aitool install <tool>
│       ├── run.py              # aitool run <tool> [args]
│       ├── list_tools.py       # aitool list
│       ├── info.py             # aitool info <tool>
│       ├── uninstall.py        # aitool uninstall <tool>
│       └── doctor.py           # aitool doctor
├── core/
│   ├── __init__.py
│   ├── engine.py               # Orchestrateur central (Engine class)
│   ├── installer.py            # Clone + venv + deps + hook install.py
│   ├── executor.py             # Chargement dynamique + run()
│   ├── registry.py             # load_registry, get_entry, search_registry
│   └── config.py               # Modèles Pydantic v2
├── plugins/                    # Plugins installés (gitignored)
│   └── .gitkeep
├── registry/
│   ├── tools.json              # Catalogue statique — 5 outils
│   └── schema.json             # JSON Schema pour validation
├── utils/
│   ├── __init__.py
│   ├── git.py                  # Helpers GitPython (clone_repo, is_git_repo)
│   ├── venv.py                 # create_venv, install_requirements, venv_exists
│   ├── http.py                 # Client httpx async (get_json, fetch_github_stars)
│   └── logger.py               # Rich console helpers (print_success, print_error...)
├── tests/
│   ├── __init__.py
│   ├── test_cli.py             # Tests Typer CliRunner — 20 tests
│   ├── test_installer.py       # Tests installer — 11 tests
│   ├── test_executor.py        # Tests executor — 15 tests
│   └── test_registry.py       # Tests registry — 19 tests
├── __init__.py
├── __main__.py                 # python -m aitoolintegrator
└── ...
```

### Modèles Pydantic (core/config.py)

| Modèle | Rôle |
|--------|------|
| `PluginManifest` | Valide le `plugin.yaml` d'un plugin installé |
| `RegistryEntry` | Valide chaque entrée dans `tools.json` |
| `AppConfig` | Configuration globale de l'application |
| `PluginConfig` | Configuration runtime d'un plugin |
| `DescriptionModel` | Descriptions courte + longue |
| `SourceModel` | URL repo + branche |
| `EntryModel` | Définition du point d'entrée d'exécution |
| `InstallModel` | Configuration de l'installation |
| `RequirementsModel` | Prérequis système |
| `IsolationModel` | Type d'isolation (venv / docker / none) |

---

## Flux détaillés

### Flux d'installation

```
aitool install ruflo
       │
       ├─ 1. Registry lookup
       │      get_entry("ruflo", registry/tools.json)
       │      → RegistryEntry validé par Pydantic
       │
       ├─ 2. Créer répertoire
       │      mkdir plugins/ruflo/
       │
       ├─ 3. Clone repo (GitPython)
       │      Repo.clone_from(entry.repo, plugins/ruflo/src/, depth=1)
       │
       ├─ 4. Créer venv (stdlib)
       │      subprocess.run([python, "-m", "venv", plugins/ruflo/.venv/])
       │
       ├─ 5. Installer requirements
       │      pip install -r plugins/ruflo/src/requirements.txt (si existe)
       │
       ├─ 6. Hook install.py (optionnel)
       │      importlib → module.install(plugin_dir, config)
       │
       └─ 7. Générer plugin.yaml
              yaml.dump(manifest_data, plugins/ruflo/plugin.yaml)
```

### Flux d'exécution

```
aitool run ruflo model=llama3
       │
       ├─ 1. Vérifier plugin installé
       │      plugins/ruflo/ exists?
       │
       ├─ 2. Charger manifeste
       │      yaml.safe_load(plugin.yaml) → PluginManifest.model_validate()
       │
       ├─ 3. Fusion de configuration
       │      {}                     # defaults vides
       │      + config.yaml values   # si config.yaml présent
       │      + {"model": "llama3"}  # args CLI parsés
       │
       ├─ 4. Import dynamique
       │      importlib.util.spec_from_file_location(plugins/ruflo/run.py)
       │
       └─ 5. Appel run() + affichage
              result = module.run(config, args)
              → Rich Panel avec status + output + metadata
```

### Flux de validation (doctor)

```
aitool doctor [outil]
       │
       ├─ Lister plugins installés (ou plugin demandé)
       │
       └─ Pour chaque plugin :
              ├─ plugin.yaml existe ?
              ├─ plugin.yaml valide (Pydantic) ?
              ├─ .venv/ existe + python binary présent ?
              └─ run.py présent ?
```

---

## Décisions techniques

### Isolation des dépendances — venv par plugin

**Problème :** Chaque outil IA a ses propres dépendances Python. Installer tout dans le même environnement garantit des conflits (ex. torch 1.x vs 2.x, numpy 1.x vs 2.x).

**Solution MVP — venv par plugin :**
```
plugins/
├── ollama/.venv/     ← environnement isolé d'Ollama
├── aider/.venv/      ← environnement isolé d'Aider
└── fabric/.venv/     ← environnement isolé de Fabric
```

| Critère | Évaluation |
|---------|-----------|
| Simplicité | Natif Python, pas de dépendance externe |
| Isolation | Complète au niveau Python, pas au niveau système |
| Espace disque | Chaque venv = ~50-200 MB |
| Vitesse | Création rapide (~2-5 secondes) |

**Solution future — Docker (v0.8+) :**
```yaml
isolation:
  type: docker
  docker_image: python:3.11-slim
```

### Chargement dynamique des plugins

Les plugins sont chargés avec `importlib.util.spec_from_file_location()`. Cela permet d'importer `run.py` depuis n'importe quel chemin sans modifier `sys.path` de façon permanente.

### Registre statique vs dynamique

**v0.1** : Registre JSON statique (`registry/tools.json`). Simple, rapide, versionné avec le code.

**v0.5** : Scraping GitHub trending + mise en cache SQLite locale.

**v1.0** : API de registre centralisée avec contributions communautaires.

---

## Stack technique complète

| Composant | Version | Justification |
|-----------|---------|---------------|
| Python | 3.11+ | Match statements, `str \| None` syntax, tomllib stdlib |
| Typer | ≥0.12 | CLI moderne basé sur type hints, auto-help, autocomplétion |
| Rich | ≥13.7 | Tableaux, Progress, Panel — UX terminale de qualité |
| Pydantic v2 | ≥2.7 | Validation stricte, erreurs lisibles, modèles imbriqués |
| GitPython | ≥3.1 | Clone avec paramètres fins (branch, depth, single-branch) |
| httpx | ≥0.27 | Client async moderne, meilleur que requests pour l'async |
| PyYAML | ≥6.0 | Parsing YAML des manifestes plugins |
| pytest | ≥8.2 | Suite de tests, fixtures, coverage intégré |
| Ruff | ≥0.4 | Linter + formateur ultra-rapide (remplace flake8+black+isort) |

---

## Couverture de tests (v0.1)

| Module | Couverture |
|--------|-----------|
| `core/registry.py` | 100% |
| `core/config.py` | 90% |
| `core/executor.py` | 86% |
| `cli/commands/install.py` | 100% |
| `cli/commands/search.py` | 97% |
| `cli/commands/info.py` | 97% |
| **TOTAL** | **74%** |

65 tests — tous en vert. Cible ≥70% atteinte.

---

## Évolution prévue

### v0.5 — Intelligence

- Commande `aitool update <tool>` (git pull + reinstall)
- Scraper GitHub trending (httpx + GitHub API)
- Auto-tagging des outils découverts
- Cache SQLite des résultats de recherche
- 15+ outils dans le registre

### v0.8 — Orchestration

- Moteur de pipelines YAML : `aitool workflow run pipeline.yaml`
- Chaînage de plugins (output d'un tool → input du suivant)
- Exécution parallèle dans les pipelines
- Commande `aitool create-plugin <name>` (scaffold automatique)

### v1.0 — Écosystème

- API de registre centralisé
- Workflow de contribution (PR → registry)
- Interface web de gestion (dashboard)
- Marketplace communautaire

---

*Voir aussi :*
- [PLUGIN_SPEC_V1.md](./PLUGIN_SPEC_V1.md) — Spécification du format plugin
- [ROADMAP.md](./ROADMAP.md) — Roadmap open-source
- [TOOL_CATALOG.md](./TOOL_CATALOG.md) — Catalogue des intégrations
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Guide du contributeur
