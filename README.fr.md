<div align="center">

# AiToolIntegrator

**Le package manager universel des outils IA**

*Découvrez, installez et orchestrez des outils IA open source — un seul CLI pour les gouverner tous.*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-74%25-yellowgreen)]()

[English](README.md) · [Français](#français)

</div>

---

## Table des matières

- [Vision](#vision)
- [Pourquoi AiToolIntegrator ?](#pourquoi-aitoolintegrator-)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Référence des commandes](#référence-des-commandes)
- [Système de plugins](#système-de-plugins)
- [Catalogue intégré](#catalogue-intégré)
- [Développement](#développement)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Vision

L'écosystème des outils IA open source est **fragmenté**. Chaque outil a son propre processus d'installation, ses propres dépendances, sa propre interface. Gérer cinq outils différents signifie cinq workflows différents, cinq sources potentielles de conflits de dépendances, et cinq documentations à mémoriser.

**AiToolIntegrator** résout ce problème en agissant comme une couche d'abstraction universelle :

```
┌──────────────────────────────────────────────┐
│            Développeur / Utilisateur         │
└──────────────────┬───────────────────────────┘
                   │
          ┌────────▼────────┐
          │   aitool CLI    │  ← interface unique
          └────────┬────────┘
                   │
     ┌─────────────▼─────────────┐
     │       Core Engine         │
     │  Installer  ·  Executor   │
     │  Registry   ·  Doctor     │
     └─────────────┬─────────────┘
                   │
    ┌──────────────▼──────────────┐
    │     Système de plugins V1   │
    │  Ollama · Aider · Fabric    │
    │  Ruflo  · Caveman  · ...    │
    └─────────────────────────────┘
```

Une seule commande pour rechercher, installer, exécuter et gérer n'importe quel outil IA — avec isolation automatique des dépendances par plugin.

---

## Pourquoi AiToolIntegrator ?

| Problème | Solution AiToolIntegrator |
|---------|--------------------------|
| Chaque outil a un processus d'installation différent | `aitool install <outil>` — toujours identique |
| Conflits de dépendances entre outils | Chaque plugin obtient son propre `venv` isolé |
| Difficile de découvrir de bons outils IA | Registre consultable avec tags, étoiles, catégories |
| Pas d'interface standard pour exécuter les outils | Contrat unifié `run(config, args)` pour tous les plugins |
| Impossible de vérifier qu'un outil fonctionne | `aitool doctor` valide chaque plugin installé |

---

## Architecture

```
aitoolintegrator/
├── cli/
│   ├── main.py                 # App Typer, toutes les commandes enregistrées ici
│   └── commands/
│       ├── search.py           # aitool search
│       ├── install.py          # aitool install
│       ├── run.py              # aitool run
│       ├── list_tools.py       # aitool list
│       ├── info.py             # aitool info
│       ├── uninstall.py        # aitool uninstall
│       └── doctor.py           # aitool doctor
├── core/
│   ├── engine.py               # Orchestrateur central — toutes les opérations passent ici
│   ├── installer.py            # Clone + venv + deps + hook install.py
│   ├── executor.py             # Chargement dynamique des plugins + run()
│   ├── registry.py             # Lecture/recherche de tools.json
│   └── config.py               # Modèles Pydantic v2 (PluginManifest, RegistryEntry, ...)
├── plugins/                    # Plugins installés (gitignored)
│   └── <nom_outil>/
│       ├── plugin.yaml         # Manifeste (auto-généré à l'installation)
│       ├── run.py              # Point d'entrée du plugin
│       ├── .venv/              # Environnement virtuel isolé
│       └── src/                # Code source cloné
├── registry/
│   ├── tools.json              # Catalogue statique (5 outils inclus)
│   └── schema.json             # JSON Schema pour la validation
└── utils/
    ├── git.py                  # Helpers GitPython
    ├── venv.py                 # Création/gestion des venvs
    ├── http.py                 # Client async httpx
    └── logger.py               # Logging structuré Rich
```

### Flux d'installation

```
aitool install aider
       │
       ├─ 1. Recherche registre  → trouver "aider" dans tools.json
       ├─ 2. Clone repo          → git clone → plugins/aider/src/
       ├─ 3. Créer venv          → python -m venv plugins/aider/.venv/
       ├─ 4. Installer deps      → pip install -r requirements.txt (dans venv)
       ├─ 5. Hook install        → exécuter install.py si présent
       └─ 6. Générer manifeste   → écrire plugins/aider/plugin.yaml
```

### Flux d'exécution

```
aitool run aider
       │
       ├─ 1. Vérifier installé   → plugins/aider/ existe ?
       ├─ 2. Charger manifeste   → parser et valider plugin.yaml
       ├─ 3. Fusionner config    → défauts plugin.yaml < config.yaml < args CLI
       ├─ 4. Importer module     → importlib.util.spec_from_file_location(run.py)
       └─ 5. Appeler run()       → run(config, args) → afficher résultat
```

---

## Stack technique

| Composant | Bibliothèque | Rôle |
|-----------|-------------|------|
| Framework CLI | [Typer](https://typer.tiangolo.com/) | Interface en ligne de commande avec type hints |
| UI Terminal | [Rich](https://rich.readthedocs.io/) | Tableaux, barres de progression, panneaux, couleurs |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) | Validation des configs et manifestes de plugins |
| Intégration Git | [GitPython](https://gitpython.readthedocs.io/) | Clonage des dépôts |
| Client HTTP | [httpx](https://www.python-httpx.org/) | Requêtes HTTP asynchrones |
| Fichiers de config | [PyYAML](https://pyyaml.org/) | Parsing YAML des manifestes de plugins |
| Tests | [pytest](https://pytest.org/) | Suite de tests avec cible ≥70% de couverture |
| Linting | [Ruff](https://docs.astral.sh/ruff/) | Linter + formateur rapide |

---

## Installation

### Prérequis

- Python 3.11 ou supérieur
- pip
- Git (pour cloner les plugins)

### Installer depuis PyPI (bientôt disponible)

```bash
pip install aitoolintegrator
```

### Installer depuis les sources

```bash
# Cloner le dépôt
git clone https://github.com/aitoolintegrator/aitoolintegrator
cd aitoolintegrator

# Installer en mode éditable avec les dépendances de développement
pip install -e ".[dev]"

# Vérifier l'installation
aitool --help
```

### Installer dans un environnement virtuel (recommandé)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Démarrage rapide

```bash
# 1. Parcourir le catalogue d'outils
aitool list

# 2. Rechercher un outil ou une catégorie
aitool search "assistant de code"
aitool search --tags llm --tags local

# 3. Consulter les détails avant d'installer
aitool info ollama

# 4. Installer un outil
aitool install aider

# 5. Exécuter l'outil
aitool run aider

# 6. Vérifier que tous les plugins sont sains
aitool doctor
```

---

## Référence des commandes

### `aitool search <requête>`

Recherche dans le registre par nom, description, tags ou catégorie.

```bash
aitool search "llm"
aitool search "code" --tags git
aitool search "" --tags local --tags privacy --sort stars
aitool search "" --sort name
```

| Option | Court | Description |
|--------|-------|-------------|
| `--tags TAG` | `-t` | Filtrer par tag. Répétable — tous les tags doivent correspondre |
| `--sort stars\|name` | `-s` | Trier les résultats (défaut : `stars`) |

**Sortie :** Tableau Rich avec nom, catégorie, nombre d'étoiles, tags et description courte. Les outils installés sont mis en évidence.

---

### `aitool install <outil>`

Installer un outil depuis le registre avec isolation complète.

```bash
aitool install ollama
aitool install aider
aitool install fabric
```

**Ce qui se passe :**
1. Recherche l'outil dans `registry/tools.json`
2. Clone le dépôt vers `plugins/<outil>/src/`
3. Crée un environnement virtuel dédié dans `plugins/<outil>/.venv/`
4. Installe `requirements.txt` dans le venv (si présent)
5. Exécute le hook `install.py` personnalisé (si présent)
6. Génère le manifeste `plugins/<outil>/plugin.yaml`

Une barre de progression Rich suit chaque étape.

---

### `aitool list`

Lister les outils avec leur statut d'installation.

```bash
aitool list                  # tous les outils du registre
aitool list --installed      # uniquement les outils installés
```

| Option | Court | Description |
|--------|-------|-------------|
| `--installed` | `-i` | Afficher uniquement les outils installés |

**Sortie :** Tableau Rich avec indicateur de statut, nom, version, catégorie, étoiles et description.

---

### `aitool info <outil>`

Afficher un panneau d'information complet pour n'importe quel outil du registre.

```bash
aitool info ollama
aitool info aider
aitool info fabric
```

**Sortie :**
- Panneau Rich avec description courte et longue
- Tableau de métadonnées : statut, version, catégorie, tags, dépôt, licence, étoiles, prérequis plateforme

---

### `aitool run <outil> [args...]`

Exécuter un plugin installé.

```bash
aitool run caveman
aitool run aider --model gpt-4o
aitool run fabric --pattern summarize
```

Les arguments supplémentaires après le nom de l'outil sont transmis directement à la fonction `run(config, args)` du plugin. Les arguments au format `clé=valeur` sont parsés dans le dict de config ; les flags comme `--verbose` sont mis à `True`.

**Priorité de fusion des configs (de la plus faible à la plus forte) :**
```
défauts plugin.yaml  →  config.yaml  →  args CLI
```

---

### `aitool uninstall <outil>`

Supprimer complètement un plugin installé.

```bash
aitool uninstall aider           # demande confirmation
aitool uninstall aider --yes     # sauter la confirmation
```

| Option | Court | Description |
|--------|-------|-------------|
| `--yes` | `-y` | Sauter le prompt de confirmation |

Le hook de désinstallation (`uninstall()` dans `install.py`) est appelé avant la suppression s'il est présent.

---

### `aitool doctor [outil]`

Valider la santé des plugins.

```bash
aitool doctor              # vérifier tous les plugins installés
aitool doctor aider        # vérifier un plugin spécifique
```

**Vérifications effectuées :**
- `plugin.yaml` existe et passe la validation Pydantic
- L'environnement virtuel existe et a un binaire Python fonctionnel
- Le point d'entrée `run.py` est présent

**Sortie :** Tableau Rich avec statut OK / FAIL par plugin, listant chaque problème trouvé.

---

## Système de plugins

### Structure d'un répertoire de plugin

```
plugins/<nom_outil>/
├── plugin.yaml         # REQUIS — manifeste de métadonnées (Spec V1)
├── run.py              # REQUIS — point d'entrée d'exécution
├── install.py          # OPTIONNEL — script d'installation/désinstallation personnalisé
├── config.yaml         # OPTIONNEL — valeurs de configuration par défaut
├── requirements.txt    # OPTIONNEL — dépendances pip (installées dans .venv)
├── .venv/              # AUTO — environnement virtuel isolé
└── src/                # AUTO — code source cloné
```

### Schéma plugin.yaml

```yaml
name: mon-outil                  # slug unique (minuscules, tirets/underscores)
version: "1.0.0"                 # semver
spec_version: "1.0.0"            # version de la spec plugin (toujours 1.0.0)
display_name: "Mon Outil"        # nom lisible par un humain

description:
  short: "Description en une ligne"
  long: |
    Description multi-lignes détaillée. Expliquer ce que fait l'outil,
    pourquoi il est utile et qui devrait l'utiliser.

source:
  repo: https://github.com/vous/mon-outil
  branch: main

category: dev-tool               # voir catégories valides ci-dessous
tags: [utilitaire, exemple]

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

### Catégories valides

| Catégorie | Description | Exemples |
|----------|-------------|---------|
| `llm-runtime` | Exécution LLM locale | Ollama, llama.cpp |
| `coding-assistant` | Outils de codage IA | Aider, gptme |
| `agent-framework` | Frameworks multi-agents | CrewAI, AutoGen |
| `agent-orchestrator` | Orchestration d'agents | Ruflo |
| `prompt-engineering` | Outils de prompts | Fabric, Caveman |
| `image-generation` | Génération d'images | ComfyUI |
| `speech-to-text` | Transcription audio | Whisper.cpp |
| `rag-framework` | RAG / chat sur documents | PrivateGPT |
| `dev-tool` | Outils de développement généraux | Open Interpreter |

### Créer un plugin

#### 1. Créer le point d'entrée `run.py`

Chaque plugin **doit** exposer une fonction `run()` avec cette signature exacte :

```python
# plugins/mon-outil/run.py

def run(config: dict, args: list[str] | None = None) -> dict:
    """
    Args:
        config: Dict de configuration fusionné (manifeste + config.yaml + args CLI).
        args:   Arguments CLI supplémentaires passés par l'utilisateur.

    Returns:
        {"status": "success"|"error", "output": Any, "metadata": dict}
    """
    # La logique de votre outil ici
    resultat = faire_quelque_chose(config.get("param", "défaut"))

    return {
        "status": "success",
        "output": resultat,
        "metadata": {"version": config.get("version", "1.0.0")},
    }
```

#### 2. Créer `plugin.yaml`

Utiliser le schéma ci-dessus. Tous les champs `[REQUIS]` doivent être présents.

#### 3. (Optionnel) Créer `install.py`

```python
# plugins/mon-outil/install.py

def install(plugin_dir: str, config: dict) -> bool:
    """Logique d'installation personnalisée. Retourne True en cas de succès."""
    # Télécharger des binaires, configurer le système, etc.
    return True

def uninstall(plugin_dir: str) -> bool:
    """Nettoyage personnalisé à la désinstallation. Retourne True en cas de succès."""
    return True
```

#### 4. (Optionnel) Créer `config.yaml`

```yaml
# plugins/mon-outil/config.yaml
modele: modele-par-defaut
temperature: 0.7
max_tokens: 1024
```

#### 5. Tester votre plugin

```bash
aitool doctor mon-outil    # valider la structure du plugin
aitool run mon-outil       # l'exécuter
```

---

## Catalogue intégré

AiToolIntegrator est livré avec 5 outils sélectionnés :

| Outil | Catégorie | Étoiles | Description |
|-------|----------|---------|-------------|
| [ruflo](https://github.com/ruvnet/ruflo) | agent-orchestrator | ~2k | Plateforme d'orchestration multi-agents pour assistants de codage IA |
| [caveman](https://github.com/explainx/skills) | prompt-engineering | ~500 | Réduit les tokens de sortie de ~70% avec un style télégraphique |
| [ollama](https://github.com/ollama/ollama) | llm-runtime | ~130k | Exécuter des LLMs localement avec une seule commande |
| [aider](https://github.com/Aider-AI/aider) | coding-assistant | ~44k | Pair programming IA dans votre terminal, natif Git |
| [fabric](https://github.com/danielmiessler/fabric) | prompt-engineering | ~30k | Framework de patterns de prompts modulaires |

### Ajouter un outil au registre

Modifier `aitoolintegrator/registry/tools.json` et ajouter une entrée suivant ce schéma :

```json
{
  "name": "mon-outil",
  "version": "1.0.0",
  "description_short": "Description en une ligne (max 120 caractères)",
  "description_long": "Description détaillée expliquant quoi, pourquoi et pour qui.",
  "repo": "https://github.com/org/mon-outil",
  "homepage": "https://mon-outil.dev",
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

Puis ouvrez une pull request — l'entrée sera validée automatiquement contre `registry/schema.json`.

---

## Développement

### Configuration

```bash
git clone https://github.com/aitoolintegrator/aitoolintegrator
cd aitoolintegrator
python -m venv .venv
source .venv/bin/activate   # ou .venv\Scripts\activate sur Windows
pip install -e ".[dev]"
```

### Exécuter les tests

```bash
# Exécuter tous les tests avec rapport de couverture
pytest

# Exécuter un fichier de test spécifique
pytest tests/test_registry.py -v

# Exécuter une classe de test spécifique
pytest tests/test_cli.py::TestSearchCommand -v

# Exécuter sans couverture (plus rapide)
pytest --no-cov
```

### Linting et formatage

```bash
# Vérifier les problèmes de linting
ruff check .

# Corriger automatiquement les problèmes corrigeables
ruff check . --fix

# Formater le code
ruff format .

# Vérification de types
mypy aitoolintegrator
```

### Conventions du projet

| Aspect | Convention |
|--------|-----------|
| Version Python | 3.11+ (match statements, syntaxe `list[str] \| None`) |
| Type hints | Obligatoires sur toutes les fonctions publiques |
| Docstrings | Style Google |
| Commits | [Conventional Commits](https://www.conventionalcommits.org/) |
| Longueur de ligne | 100 caractères |
| Style d'import | `from __future__ import annotations` dans chaque module |

### Types de commits conventionnels

```
feat:     nouvelle fonctionnalité
fix:      correction de bug
docs:     changement de documentation
test:     ajout ou mise à jour de tests
refactor: changement de code qui ne corrige pas un bug ni n'ajoute une fonctionnalité
perf:     amélioration des performances
chore:    maintenance (mise à jour de dépendances, CI, outillage)
```

---

## Contribuer

Les contributions sont les bienvenues ! Voici comment commencer :

1. **Fork** le dépôt sur GitHub
2. **Cloner** votre fork localement
3. **Créer une branche** : `git checkout -b feat/ma-feature` ou `fix/mon-bug`
4. **Développer** en suivant les conventions du projet ci-dessus
5. **Tester** : `pytest` doit passer avec ≥70% de couverture
6. **Linter** : `ruff check .` ne doit signaler aucune erreur
7. **Ouvrir une PR** avec un titre et une description clairs

### Ce que vous pouvez contribuer

| Type | Description | Difficulté |
|------|-------------|------------|
| Correction de bug | Corriger un problème existant | Facile |
| Documentation | Améliorer README, docstrings, exemples | Facile |
| Nouveau plugin | Ajouter un outil dans `registry/tools.json` | Facile |
| Nouvelle commande | Ajouter une commande CLI (ex. `aitool update`) | Moyen |
| Nouvelle fonctionnalité | Améliorations de l'installeur, scraper GitHub, etc. | Moyen |
| Architecture | Isolation Docker, moteur de pipeline | Avancé |

---

## Feuille de route

- **v0.1** (actuel) — CLI de base, 5 outils dans le registre, Plugin Spec V1
- **v0.5** — Scraper trending GitHub, `aitool update`, 15+ outils
- **v0.8** — Moteur de pipeline YAML (`aitool workflow run fichier.yaml`)
- **v1.0** — API de registre centralisé, marketplace communautaire

Voir [docs/ROADMAP.md](docs/ROADMAP.md) pour la feuille de route complète.

---

## Licence

MIT — voir [LICENSE](LICENSE).

---

<div align="center">

*"Le package manager universel des outils IA"*

Fait avec Python, Typer et Rich.

</div>
