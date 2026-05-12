# 🔌 AiToolIntegrator — Plugin Specification V1

> Version : **1.0.0**  
> Statut : **Draft**  
> Date : 2026-05-12

---

## 1. Vue d'ensemble

Un **plugin** est l'unité fondamentale d'AiToolIntegrator. Il encapsule un outil IA externe et expose une interface standardisée pour l'installer, le configurer et l'exécuter.

### Principes de conception

1. **Convention over configuration** — Des valeurs par défaut intelligentes
2. **Isolation** — Chaque plugin vit dans son propre répertoire avec son propre venv
3. **Déclaratif** — Le `plugin.yaml` décrit tout ce qu'il faut savoir
4. **Extensible** — Hooks personnalisables à chaque étape du lifecycle
5. **Reproductible** — Même config = même résultat

---

## 2. Structure d'un Plugin

```
plugins/<tool_name>/
├── plugin.yaml          # [REQUIS] Métadonnées et configuration
├── install.py           # [OPTIONNEL] Script d'installation personnalisé
├── run.py               # [REQUIS] Point d'entrée d'exécution
├── config.yaml          # [OPTIONNEL] Configuration par défaut
├── hooks/               # [OPTIONNEL] Scripts de lifecycle
│   ├── pre_install.py
│   ├── post_install.py
│   ├── pre_run.py
│   └── post_run.py
├── README.md            # [RECOMMANDÉ] Documentation du plugin
├── requirements.txt     # [OPTIONNEL] Dépendances Python
├── .venv/               # [AUTO-GÉNÉRÉ] Environnement virtuel
└── src/                 # [AUTO-GÉNÉRÉ] Code source cloné
```

---

## 3. plugin.yaml — Spécification complète

```yaml
# ============================================================
# AiToolIntegrator Plugin Manifest — Spec V1
# ============================================================

# --- Identification -------------------------------------------
name: "ollama"                          # [REQUIS] Identifiant unique (slug)
version: "0.6.2"                        # [REQUIS] Version du plugin (semver)
spec_version: "1.0.0"                   # [REQUIS] Version de la spec plugin
display_name: "Ollama"                  # [OPTIONNEL] Nom d'affichage
author: "Ollama Inc."                   # [OPTIONNEL] Auteur/mainteneur
license: "MIT"                          # [OPTIONNEL] Licence

# --- Descriptions ---------------------------------------------
description:
  short: "Exécuter des LLMs localement via CLI"
  long: |
    Ollama est un runtime qui permet de télécharger, gérer et
    exécuter des modèles de langage (LLMs) directement sur votre
    machine. Il supporte Llama 3, Mistral, Gemma, Phi-3 et
    des dizaines d'autres modèles. Interface CLI simple et API
    REST compatible OpenAI incluse.
    
    Cas d'usage : prototypage local, développement offline,
    respect de la vie privée, réduction des coûts API.

# --- Source ----------------------------------------------------
source:
  repo: "https://github.com/ollama/ollama"
  branch: "main"                        # [OPTIONNEL] Branche à cloner
  homepage: "https://ollama.com"        # [OPTIONNEL]

# --- Classification -------------------------------------------
category: "llm-runtime"                 # [REQUIS] Catégorie principale
tags:                                   # [REQUIS] Tags pour la recherche
  - llm
  - local
  - inference
  - privacy
  - cli

# --- Exécution -------------------------------------------------
entry:
  module: "run.py"                      # [REQUIS] Fichier d'entrée
  function: "run"                       # [REQUIS] Fonction à appeler
  type: "python"                        # [REQUIS] python | binary | docker

# --- Installation ----------------------------------------------
install:
  method: "auto"                        # auto | script | binary | docker
  script: "install.py"                  # [OPTIONNEL] Script custom
  requirements: "requirements.txt"      # [OPTIONNEL] Dépendances pip
  system_deps:                          # [OPTIONNEL] Dépendances système
    - name: "curl"
      check: "curl --version"
  post_install_check: "ollama --version"  # [OPTIONNEL] Vérification

# --- Configuration ---------------------------------------------
config:
  file: "config.yaml"                   # [OPTIONNEL] Fichier de config
  schema:                               # [OPTIONNEL] Validation Pydantic
    model:
      type: string
      default: "llama3.2"
      description: "Modèle à utiliser"
    temperature:
      type: float
      default: 0.7
      min: 0.0
      max: 2.0

# --- Prérequis -------------------------------------------------
requirements:
  python: ">=3.11"                      # [OPTIONNEL]
  platforms:                            # [OPTIONNEL]
    - windows
    - macos
    - linux
  gpu: false                            # [OPTIONNEL] GPU requis ?
  min_ram_gb: 8                         # [OPTIONNEL]
  min_disk_gb: 5                        # [OPTIONNEL]

# --- Isolation --------------------------------------------------
isolation:
  type: "venv"                          # venv | docker | none
  docker_image: null                    # [SI docker] Image à utiliser

# --- Capabilities -----------------------------------------------
capabilities:                           # Ce que le plugin peut faire
  - text-generation
  - chat
  - embedding
  
# --- Health Check -----------------------------------------------
health:
  command: "ollama list"                # Commande pour vérifier l'état
  timeout: 10                           # Timeout en secondes
```

---

## 4. Points d'entrée Python

### run.py — Contrat d'interface

```python
"""
AiToolIntegrator Plugin Entrypoint — Spec V1
Chaque plugin DOIT exposer une fonction run().
"""
from typing import Any


def run(config: dict, args: list[str] | None = None) -> dict[str, Any]:
    """
    Point d'entrée principal du plugin.
    
    Args:
        config: Configuration fusionnée (défauts + utilisateur)
        args: Arguments CLI additionnels passés par l'utilisateur
        
    Returns:
        dict avec les clés suivantes :
        {
            "status": "success" | "error",
            "output": <résultat principal>,
            "metadata": { ... }  # optionnel
        }
    """
    # Implémentation spécifique au plugin
    ...


def info() -> dict[str, str]:
    """
    [OPTIONNEL] Retourne des informations runtime sur le plugin.
    Ex: version installée, modèles disponibles, etc.
    """
    return {
        "runtime_version": "0.6.2",
        "models_loaded": "3"
    }
```

### install.py — Contrat d'installation

```python
"""
AiToolIntegrator Plugin Installer — Spec V1
Script d'installation personnalisé (optionnel).
"""


def install(plugin_dir: str, config: dict) -> bool:
    """
    Effectue l'installation personnalisée du plugin.
    
    Args:
        plugin_dir: Chemin absolu du répertoire du plugin
        config: Configuration d'installation
        
    Returns:
        True si l'installation a réussi, False sinon
    """
    ...


def uninstall(plugin_dir: str) -> bool:
    """
    [OPTIONNEL] Nettoyage personnalisé lors de la désinstallation.
    """
    ...
```

---

## 5. Lifecycle d'un Plugin

```
  DISCOVERED ──► INSTALLING ──► INSTALLED ──► RUNNING
       │              │              │            │
       │         [pre_install]  [post_install]  [pre_run]
       │              │              │            │
       │         Échec ?         doctor       [post_run]
       │              │              │            │
       ▼              ▼              ▼            ▼
   REGISTRY       FAILED        OUTDATED      STOPPED
                                    │
                                    ▼
                               UPDATING
                                    │
                                    ▼
                               INSTALLED
```

### États

| État | Description |
|------|-------------|
| `DISCOVERED` | Présent dans le registry, pas installé |
| `INSTALLING` | Installation en cours |
| `INSTALLED` | Installé et prêt à l'emploi |
| `RUNNING` | En cours d'exécution |
| `STOPPED` | Exécution terminée |
| `FAILED` | Installation ou exécution échouée |
| `OUTDATED` | Mise à jour disponible |
| `UPDATING` | Mise à jour en cours |

---

## 6. Hooks de Lifecycle

Les hooks sont des scripts Python optionnels dans `hooks/` :

```python
# hooks/pre_install.py
def hook(context: dict) -> bool:
    """
    Exécuté avant l'installation.
    Retourne False pour annuler l'installation.
    """
    # Vérifier prérequis système
    if not check_gpu_available():
        print("Warning: GPU non détecté")
    return True
```

| Hook | Moment | Peut annuler ? |
|------|--------|----------------|
| `pre_install` | Avant clone + venv | ✅ Oui |
| `post_install` | Après installation complète | ❌ Non |
| `pre_run` | Avant exécution de run() | ✅ Oui |
| `post_run` | Après exécution de run() | ❌ Non |

---

## 7. Configuration — Fusion des valeurs

L'ordre de priorité (du plus faible au plus fort) :

```
plugin.yaml defaults  →  config.yaml  →  CLI args  →  env vars
```

Variables d'environnement préfixées par `AITOOL_<PLUGIN>_` :
```bash
export AITOOL_OLLAMA_MODEL="mistral"
export AITOOL_OLLAMA_TEMPERATURE="0.5"
```

---

## 8. Catégories Officielles

| Slug | Nom | Exemples |
|------|-----|----------|
| `llm-runtime` | Runtime LLM | Ollama, llama.cpp, LocalAI |
| `coding-assistant` | Assistant de code | Aider, gptme, Continue.dev |
| `agent-framework` | Framework d'agents | CrewAI, AutoGen, LangChain |
| `agent-orchestrator` | Orchestrateur d'agents | Ruflo |
| `prompt-engineering` | Ingénierie de prompts | Fabric, Caveman |
| `image-generation` | Génération d'images | ComfyUI, A1111 |
| `speech-to-text` | Parole vers texte | Whisper.cpp |
| `rag-framework` | RAG / Documents | PrivateGPT, AnythingLLM |
| `dev-tool` | Outil de développement | Open Interpreter |

---

## 9. Validation

Le Core Engine valide chaque `plugin.yaml` avec un JSON Schema et Pydantic. Les champs `[REQUIS]` sont obligatoires. Un plugin invalide ne sera pas chargé.

```bash
aitool doctor          # Vérifie tous les plugins installés
aitool doctor ruflo    # Vérifie un plugin spécifique
```

---

## 10. Créer un nouveau plugin — Guide rapide

```bash
# 1. Créer le répertoire
mkdir -p plugins/mon-outil

# 2. Créer plugin.yaml (copier le template)
cp templates/plugin.yaml plugins/mon-outil/

# 3. Implémenter run.py
cat > plugins/mon-outil/run.py << 'EOF'
def run(config: dict, args: list[str] | None = None) -> dict:
    return {"status": "success", "output": "Hello from mon-outil!"}
EOF

# 4. Tester
aitool run mon-outil
```

> **Futur** : `aitool create-plugin mon-outil` générera automatiquement le scaffold.
