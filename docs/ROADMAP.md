# 🗺️ AiToolIntegrator — Roadmap Open Source

> Version : 2026-05-12

---

## 🏗️ Phases de Développement

### ✅ Phase 0 — Foundation (Semaines 1-2)

| Tâche | Priorité | Statut |
|-------|----------|--------|
| Init repo GitHub | P0 | ✅ |
| Structure du projet Python | P0 | ✅ |
| Setup pyproject.toml + dépendances | P0 | ✅ |
| CLI Typer de base (hello world) | P0 | ✅ |
| CI/CD GitHub Actions (lint + test) | P1 | ✅ |
| README.md initial | P0 | ✅ |
| Licence MIT | P0 | ✅ |
| .gitignore + .editorconfig | P1 | ✅ |

---

### ✅ Phase 1 — MVP (Semaines 3-6)

| Tâche | Priorité | Statut |
|-------|----------|--------|
| Commande `search` | P0 | ✅ |
| Commande `install` | P0 | ✅ |
| Commande `list` | P0 | ✅ |
| Commande `run` | P0 | ✅ |
| Commande `info` | P1 | ✅ |
| Commande `uninstall` | P1 | ✅ |
| Registry statique JSON (≥5 outils) | P0 | ✅ |
| Plugin Spec V1 (plugin.yaml) | P0 | ✅ |
| Système d'installation (clone + venv) | P0 | ✅ |
| Système d'exécution (run dynamique) | P0 | ✅ |
| Plugin: Ruflo | P0 | ✅ |
| Plugin: Caveman | P0 | ✅ |
| Plugin: Ollama | P1 | ✅ |
| Tests unitaires (≥70% coverage) | P1 | ✅ 79 tests, 74% |
| Documentation utilisateur | P1 | ✅ |
| Premier release v0.1.0 | P0 | ✅ |

---

### 🧠 Phase 2 — Intelligence (Semaines 7-12)

| Tâche | Priorité | Statut |
|-------|----------|--------|
| Commande `doctor` | P1 | ✅ |
| Commande `update` | P1 | ✅ |
| GitHub API star refresh (`aitool refresh`) | P1 | ✅ |
| 12+ plugins dans le registry | P1 | ✅ crewai, autogen, whisper, tabby, litellm, llama-index, open-interpreter |
| Auto-tagging des outils | P2 | 🔲 |
| Ranking par pertinence / étoiles | P2 | 🔲 |
| Cache SQLite des résultats | P2 | 🔲 |
| Plugin hooks (pre/post install/run) | P1 | 🔲 |
| Config multi-profils | P2 | 🔲 |
| Release v0.5.0 | P0 | 🔲 |

---

### 🔗 Phase 3 — Orchestration (Semaines 13-20)

| Tâche | Priorité | Statut |
|-------|----------|--------|
| Pipeline YAML engine | P1 | 🔲 |
| Commande `workflow run <file>` | P1 | 🔲 |
| Chaining de plugins (output → input) | P1 | 🔲 |
| Exécution parallèle dans pipelines | P2 | 🔲 |
| Commande `create-plugin` (scaffold) | P2 | 🔲 |
| Docker isolation (opt-in) | P2 | 🔲 |
| Release v0.8.0 | P0 | 🔲 |

---

### 🌐 Phase 4 — Écosystème (v1.0+)

| Tâche | Priorité | Statut |
|-------|----------|--------|
| Registry centralisé (API) | P1 | 🔲 |
| Contribution workflow (PR → registry) | P1 | 🔲 |
| Interface web (dashboard) | P2 | 🔲 |
| Marketplace communautaire | P2 | 🔲 |
| Mode agent autonome | P3 | 🔲 |
| Intégration LLM (recommandations IA) | P3 | 🔲 |
| Release v1.0.0 | P0 | 🔲 |

---

## 🎨 Branding

### Identité

| Élément | Valeur |
|---------|--------|
| **Nom** | AiToolIntegrator |
| **Nom court** | `aitool` (commande CLI) |
| **Tagline** | *"Le package manager universel des outils IA"* |
| **Tagline EN** | *"The universal AI tools package manager"* |
| **Logo** | Icône de boîte à outils + symbole IA (⚡🧰) |
| **Couleurs** | Bleu électrique `#0066FF` + Violet `#8B5CF6` |
| **Ton** | Technique mais accessible, francophone-first |

### Présence en ligne

- **GitHub** : `github.com/<org>/aitoolintegrator`
- **PyPI** : `pip install aitoolintegrator`
- **Docs** : GitHub Pages ou ReadTheDocs
- **Discord** : Communauté de contributeurs
- **Twitter/X** : Annonces et updates

---

## 👥 Guide du Contributeur

### Comment contribuer

1. **Fork** le repo
2. **Clone** localement
3. **Créer une branche** : `feat/ma-feature` ou `fix/mon-bug`
4. **Développer** avec les conventions du projet
5. **Tester** : `pytest` avec ≥70% coverage
6. **PR** avec description claire

### Conventions

| Aspect | Convention |
|--------|-----------|
| Code style | Ruff (linter + formatter) |
| Type hints | Obligatoires (mypy strict) |
| Docstrings | Google style |
| Commits | Conventional Commits (`feat:`, `fix:`, `docs:`) |
| Branches | `main` (stable), `develop` (intégration) |
| Versions | Semantic Versioning (semver) |
| Tests | pytest + coverage ≥70% |

### Types de contributions

| Type | Description | Difficulté |
|------|-------------|------------|
| 🐛 Bug fix | Corriger un bug existant | 🟢 Facile |
| 📝 Docs | Améliorer la documentation | 🟢 Facile |
| 🔌 Plugin | Créer un nouveau plugin | 🟡 Moyen |
| ✨ Feature | Nouvelle fonctionnalité core | 🟡 Moyen |
| 🏗️ Architecture | Changement structurel | 🔴 Avancé |
| 🔧 Infra | CI/CD, tooling, release | 🔴 Avancé |

### Labels GitHub

| Label | Description |
|-------|-------------|
| `good first issue` | Idéal pour commencer |
| `help wanted` | Besoin d'aide |
| `plugin` | Relatif aux plugins |
| `core` | Relatif au core engine |
| `cli` | Relatif à l'interface CLI |
| `registry` | Relatif au catalogue |
| `documentation` | Documentation |
| `enhancement` | Amélioration |
| `bug` | Bug confirmé |

---

## 📈 Métriques de Succès

### MVP (v0.1)

- [ ] CLI fonctionnel avec ≥4 commandes
- [ ] ≥5 outils dans le registry
- [ ] ≥2 plugins fonctionnels end-to-end
- [ ] README complet
- [ ] Publié sur PyPI

### v0.5

- [ ] ≥15 outils dans le registry
- [ ] ≥5 plugins fonctionnels
- [ ] ≥10 étoiles GitHub
- [ ] ≥3 contributeurs externes
- [ ] Documentation complète

### v1.0

- [ ] ≥50 outils dans le registry
- [ ] Pipeline YAML fonctionnel
- [ ] ≥100 étoiles GitHub
- [ ] Communauté active (Discord ≥50 membres)
- [ ] Couvert par un article/blog technique

---

## 🔮 Vision Long Terme

```
Année 1 : CLI + Registry + Plugins → "pip pour les outils IA"
Année 2 : Orchestration + Marketplace → "Homebrew + npm pour l'IA"
Année 3 : Agents + Web UI → "Plateforme d'orchestration IA"
```
