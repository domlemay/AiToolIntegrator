# 📚 AiToolIntegrator — Catalogue des Intégrations

> Chaque outil est documenté avec une **description courte** (1 ligne) et une **description longue** (détaillée).

---

## 🏷️ Catégories

| Icône | Catégorie | Description |
|-------|-----------|-------------|
| 🧠 | LLM Runtime | Exécution locale de modèles de langage |
| 💻 | Coding Assistant | Assistants de programmation IA |
| 🤖 | Agent Framework | Frameworks d'agents autonomes |
| 🎭 | Agent Orchestrator | Orchestration multi-agents |
| ✍️ | Prompt Engineering | Outils de gestion/optimisation de prompts |
| 🎨 | Image Generation | Génération d'images par IA |
| 🎤 | Speech-to-Text | Transcription audio vers texte |
| 📄 | RAG Framework | Retrieval-Augmented Generation / chat sur documents |
| 🛠️ | Dev Tool | Outils de développement IA généraux |

---

## 🧠 LLM Runtime

### 1. Ollama

- **Courte** : Télécharger et exécuter des LLMs localement en une commande.
- **Repo** : `github.com/ollama/ollama` | ⭐ ~130k | Licence : MIT
- **Tags** : `llm`, `local`, `inference`, `privacy`, `cli`
- **Longue** :

> Ollama est un runtime qui permet de télécharger, gérer et exécuter des modèles de langage (LLMs) directement sur votre machine locale. Il supporte une large gamme de modèles : Llama 3, Mistral, Gemma, Phi-3, CodeLlama, et des dizaines d'autres. L'installation se fait en une seule commande, et l'exécution est aussi simple que `ollama run llama3`.
>
> **Fonctionnalités clés** :
> - CLI intuitive (`ollama pull`, `ollama run`, `ollama list`)
> - API REST locale compatible OpenAI (port 11434)
> - Gestion automatique du téléchargement et du cache des modèles
> - Support CPU et GPU (NVIDIA, AMD, Apple Silicon)
> - Création de modèles personnalisés via Modelfile
> - Fonctionne 100% hors ligne une fois le modèle téléchargé
>
> **Pertinent pour vous si** : Vous voulez exécuter des LLMs localement sans configuration complexe, protéger vos données, ou éviter les coûts d'API cloud.

---

### 2. llama.cpp

- **Courte** : Moteur d'inférence LLM ultra-optimisé en C/C++ pour hardware grand public.
- **Repo** : `github.com/ggerganov/llama.cpp` | ⭐ ~75k | Licence : MIT
- **Tags** : `llm`, `inference`, `cpp`, `quantization`, `performance`
- **Longue** :

> llama.cpp est le moteur d'inférence de référence pour exécuter des LLMs sur du matériel grand public. Écrit en C/C++ pur, il est optimisé pour fonctionner sur CPU avec un support GPU optionnel. Il utilise le format GGUF qui permet la quantization (compression des modèles) pour les faire tourner sur des machines avec peu de RAM.
>
> **Fonctionnalités clés** :
> - Performances optimisées CPU-first (AVX, AVX2, ARM NEON)
> - Support GPU : CUDA, Metal (Apple), Vulkan, OpenCL
> - Quantization 2-bit à 8-bit pour réduire l'empreinte mémoire
> - Serveur HTTP intégré compatible OpenAI
> - Support des modèles multimodaux (texte + images)
> - Batch processing et parallel decoding
>
> **Pertinent pour vous si** : Vous êtes développeur et voulez un contrôle maximum sur l'inférence, ou si vous avez du hardware limité et devez optimiser chaque octet.

---

### 3. LocalAI

- **Courte** : Stack IA locale complète, drop-in replacement de l'API OpenAI.
- **Repo** : `github.com/mudler/LocalAI` | ⭐ ~30k | Licence : MIT
- **Tags** : `llm`, `api`, `openai-compatible`, `self-hosted`, `multi-modal`
- **Longue** :

> LocalAI est un serveur API auto-hébergé qui reproduit l'API OpenAI mais tourne entièrement en local. Il gère texte, images, audio (via whisper.cpp), et embeddings via un seul endpoint. Idéal pour remplacer les appels OpenAI dans vos applications existantes sans changer une ligne de code.
>
> **Fonctionnalités clés** :
> - API 100% compatible OpenAI (chat, completions, embeddings, images, audio)
> - Support multi-backend : llama.cpp, transformers, diffusers, whisper
> - Pas de GPU requis (mais supporté)
> - Galerie de modèles pré-configurés
> - Deploy via Docker en une commande
>
> **Pertinent pour vous si** : Vous avez des applications qui appellent l'API OpenAI et voulez les migrer vers du local sans réécriture.

---

## 💻 Coding Assistant

### 4. Aider

- **Courte** : Assistant de pair programming IA directement dans le terminal, intégré à Git.
- **Repo** : `github.com/Aider-AI/aider` | ⭐ ~44k | Licence : Apache 2.0
- **Tags** : `coding`, `git`, `terminal`, `pair-programming`, `multi-file`
- **Longue** :

> Aider est un outil de pair programming IA en terminal qui édite directement vos fichiers et fait des commits Git automatiques. Il comprend la structure de votre codebase via tree-sitter et peut modifier plusieurs fichiers simultanément pour implémenter des features complètes.
>
> **Fonctionnalités clés** :
> - Édition multi-fichiers avec commits Git automatiques
> - Carte du repository via tree-sitter (navigation intelligente)
> - Support de tous les LLMs majeurs (OpenAI, Anthropic, Google, Ollama)
> - Mode Architecte (2 modèles pour refactoring complexe)
> - Voice-to-code (commandes vocales)
> - Ajout d'images et pages web comme contexte
>
> **Pertinent pour vous si** : Vous codez principalement en terminal et voulez un assistant IA qui s'intègre naturellement dans votre workflow Git.

---

### 5. gptme

- **Courte** : Agent IA personnel en terminal pour coder, exécuter des scripts et naviguer le web.
- **Repo** : `github.com/ErikBjare/gptme` | ⭐ ~5k | Licence : MIT
- **Tags** : `coding`, `terminal`, `agent`, `privacy`, `local-first`
- **Longue** :

> gptme est un agent IA personnel qui tourne dans votre terminal. Il peut exécuter du code Python/Shell, manipuler des fichiers, naviguer sur le web, et même utiliser la vision par ordinateur. Conçu privacy-first, il supporte les modèles locaux et garde un historique d'apprentissage.
>
> **Fonctionnalités clés** :
> - Exécution de code (Python, Shell) directement
> - Manipulation de fichiers et navigation web
> - Agents persistants avec mémoire et apprentissage
> - Support modèles locaux (Ollama) et cloud
> - Vision par ordinateur intégrée
>
> **Pertinent pour vous si** : Vous cherchez un assistant terminal polyvalent qui peut agir de manière autonome tout en restant local.

---

### 6. Continue.dev

- **Courte** : Assistant de code IA open source intégré à VS Code et JetBrains.
- **Repo** : `github.com/continuedev/continue` | ⭐ ~25k | Licence : Apache 2.0
- **Tags** : `coding`, `ide`, `autocomplete`, `vscode`, `jetbrains`
- **Longue** :

> Continue est un assistant de code IA qui s'intègre directement dans votre IDE (VS Code, JetBrains). Il offre du chat, de l'autocomplétion, et de l'édition inline, le tout configurable via YAML pour choisir vos modèles et providers.
>
> **Fonctionnalités clés** :
> - Chat et autocomplétion dans l'IDE
> - Configuration YAML (switch facile entre modèles)
> - Contexte codebase complet (fichiers ouverts, diffs, terminal)
> - Agents custom pour automatiser des tâches (code review, debug)
> - Support modèles locaux via Ollama
>
> **Pertinent pour vous si** : Vous travaillez dans VS Code ou JetBrains et voulez une alternative open source à GitHub Copilot.

---

## 🤖 Agent Framework

### 7. CrewAI

- **Courte** : Framework pour créer des équipes d'agents IA spécialisés qui collaborent.
- **Repo** : `github.com/crewAIInc/crewAI` | ⭐ ~30k | Licence : MIT
- **Tags** : `agents`, `multi-agent`, `orchestration`, `roles`, `teams`
- **Longue** :

> CrewAI permet de créer des "équipes" d'agents IA où chaque agent a un rôle spécifique (Researcher, Coder, Reviewer). Les agents collaborent de manière autonome pour résoudre des tâches complexes. Le modèle "Crews + Flows" offre autonomie et contrôle précis.
>
> **Fonctionnalités clés** :
> - Agents basés sur des rôles (role-based)
> - Système Crews (autonomie) + Flows (orchestration précise)
> - Outils intégrés : web scraping, fichiers, API
> - Prototypage rapide de systèmes multi-agents
> - Intégrations LLM multiples
>
> **Pertinent pour vous si** : Vous voulez prototyper rapidement un système multi-agents avec des rôles clairs (chercheur, rédacteur, reviewer).

---

### 8. AutoGen (AG2)

- **Courte** : Framework Microsoft pour agents conversationnels multi-modèles.
- **Repo** : `github.com/microsoft/autogen` | ⭐ ~40k | Licence : MIT
- **Tags** : `agents`, `conversational`, `microsoft`, `research`, `event-driven`
- **Longue** :

> AutoGen de Microsoft est un framework où les agents interagissent via des conversations en langage naturel. Idéal pour des scénarios de négociation, débat multi-agents, ou workflows complexes dans l'écosystème Azure/Microsoft.
>
> **Fonctionnalités clés** :
> - Logique conversationnelle (agents dialoguent entre eux)
> - Architecture event-driven (v0.4+)
> - AutoGen Studio (interface no-code)
> - Support workflows asynchrones et longue durée
> - Extensibilité modulaire
>
> **Pertinent pour vous si** : Vous travaillez dans l'écosystème Microsoft/Azure ou avez besoin d'agents qui débattent et négocient.

---

### 9. LangChain / LangGraph

- **Courte** : Framework de référence pour apps LLM production-ready avec orchestration graphique.
- **Repo** : `github.com/langchain-ai/langchain` | ⭐ ~100k | Licence : MIT
- **Tags** : `llm`, `framework`, `production`, `graph`, `state-management`
- **Longue** :

> LangChain est l'écosystème standard pour construire des applications basées sur des LLMs. LangGraph ajoute l'orchestration par graphes dirigés pour des workflows complexes avec état, loops, et human-in-the-loop. C'est le choix production-grade.
>
> **Fonctionnalités clés** :
> - Composants modulaires (tools, LLM integrations, memory)
> - LangGraph : workflows en graphes avec checkpointing
> - Human-in-the-loop et "time-travel" debugging
> - Observabilité via LangSmith
> - Intégrations massives (100+ providers)
>
> **Pertinent pour vous si** : Vous construisez une application IA production-grade nécessitant contrôle, état, et observabilité.

---

## 🎭 Agent Orchestrator

### 10. Ruflo

- **Courte** : Plateforme d'orchestration multi-agents pour coding assistants (Claude Code, Codex).
- **Repo** : `github.com/ruvnet/ruflo` | ⭐ ~2k | Licence : MIT
- **Tags** : `orchestration`, `multi-agent`, `coding`, `mcp`, `swarm`
- **Longue** :

> Ruflo (ex Claude Flow) transforme un assistant de code IA en environnement multi-agents. Il déploie des swarms d'agents spécialisés (coding, testing, sécurité, docs) qui travaillent en parallèle avec mémoire persistante et knowledge graphs.
>
> **Fonctionnalités clés** :
> - Orchestration de swarms d'agents spécialisés
> - Mémoire persistante et knowledge graphs auto-apprenants
> - Exécution parallèle des agents
> - Support natif MCP (Model Context Protocol)
> - Outils d'observabilité et debugging
>
> **Pertinent pour vous si** : Vous utilisez Claude Code ou Codex et voulez passer à un workflow multi-agents parallélisé.

---

## ✍️ Prompt Engineering

### 11. Fabric

- **Courte** : Framework de patterns (prompts modulaires) pour augmenter les capacités humaines avec l'IA.
- **Repo** : `github.com/danielmiessler/fabric` | ⭐ ~30k | Licence : MIT
- **Tags** : `prompts`, `patterns`, `workflow`, `modular`, `cli`
- **Longue** :

> Fabric propose une bibliothèque de "Patterns" — des prompts modulaires et réutilisables créés par la communauté pour résoudre des tâches spécifiques : résumer un article, extraire des insights YouTube, écrire dans un style précis. Les patterns se chaînent en workflows.
>
> **Fonctionnalités clés** :
> - Bibliothèque massive de patterns crowdsourcés
> - Chaînage de patterns pour workflows complexes
> - CLI, GUI, et intégration API
> - Model-agnostic (OpenAI, Claude, Gemini, modèles locaux)
> - Patterns personnalisables et partageables
>
> **Pertinent pour vous si** : Vous voulez une boîte à outils de prompts prêts à l'emploi plutôt que de rédiger chaque prompt from scratch.

---

### 12. Caveman

- **Courte** : Skill/prompt qui réduit ~70% des tokens de sortie en forçant un style télégraphique.
- **Repo** : `github.com/explainx/skills` (caveman skill) | Licence : MIT
- **Tags** : `prompt`, `token-optimization`, `cost`, `speed`, `skill`
- **Longue** :

> Caveman est un "skill" (prompt système) qui force l'IA à communiquer en style caveman — éliminant les formules de politesse, les préambules, et la grammaire inutile. Résultat : ~65-75% de réduction des tokens de sortie, ce qui baisse les coûts API et accélère les réponses.
>
> **Fonctionnalités clés** :
> - Réduction drastique des tokens de sortie
> - Communication directe et télégraphique
> - Drop-in dans Claude Code, Cursor, ou tout agent
> - Fichier markdown simple à intégrer
> - Accélère les boucles agentiques
>
> **Pertinent pour vous si** : Vous payez à l'usage pour des API LLM et voulez réduire vos coûts sans perdre en qualité de code.

---

## 🎨 Image Generation

### 13. ComfyUI

- **Courte** : Interface node-based pour Stable Diffusion avec contrôle granulaire des pipelines.
- **Repo** : `github.com/comfyanonymous/ComfyUI` | ⭐ ~70k | Licence : GPL 3.0
- **Tags** : `image`, `stable-diffusion`, `node-based`, `workflow`, `gpu`
- **Longue** :

> ComfyUI traite la génération d'images comme du visual programming. Vous construisez des pipelines en connectant des nodes (Load Model → Sampler → VAE Decode). Les workflows sont exportables en JSON pour le partage et la reproductibilité.
>
> **Fonctionnalités clés** :
> - Interface visuelle node-based
> - Contrôle granulaire de chaque étape du pipeline
> - Gestion mémoire optimisée (lazy evaluation)
> - Workflows reproductibles (export JSON)
> - Extensible via custom nodes communautaires
> - Support vidéo et ControlNet avancé
>
> **Pertinent pour vous si** : Vous générez des images IA et voulez un contrôle total sur vos pipelines avec des workflows réutilisables.

---

### 14. Automatic1111 (SD WebUI)

- **Courte** : Interface web classique et complète pour Stable Diffusion, plug-and-play.
- **Repo** : `github.com/AUTOMATIC1111/stable-diffusion-webui` | ⭐ ~145k | Licence : AGPL 3.0
- **Tags** : `image`, `stable-diffusion`, `webui`, `extensions`, `beginner-friendly`
- **Longue** :

> A1111 est l'interface Stable Diffusion la plus populaire. UI web classique avec tabs (txt2img, img2img, inpainting). Écosystème massif d'extensions communautaires. Idéal pour débuter.
>
> **Fonctionnalités clés** :
> - UI intuitive en tabs
> - Écosystème d'extensions massif
> - Txt2img, img2img, inpainting, outpainting
> - Face restoration, model merging, prompt matrix
> - Compatible SD 1.5, SDXL
>
> **Pertinent pour vous si** : Vous débutez avec la génération d'images IA et voulez une interface simple avec un maximum d'extensions.

---

## 🎤 Speech-to-Text

### 15. Whisper.cpp

- **Courte** : Port C/C++ ultra-léger de Whisper (OpenAI) pour transcription offline.
- **Repo** : `github.com/ggerganov/whisper.cpp` | ⭐ ~40k | Licence : MIT
- **Tags** : `speech`, `transcription`, `offline`, `cpp`, `edge`
- **Longue** :

> whisper.cpp est un port performant du modèle Whisper d'OpenAI en C/C++. Il permet la transcription speech-to-text en local, même sur des appareils edge (Raspberry Pi, laptops). Aucune dépendance lourde requise.
>
> **Fonctionnalités clés** :
> - Transcription offline rapide
> - Fonctionne sur hardware minimal (Raspberry Pi)
> - Multi-langues (99 langues)
> - Formats audio multiples
> - Intégrable dans d'autres applications
>
> **Pertinent pour vous si** : Vous avez besoin de transcription audio privée et offline, ou vous intégrez du speech-to-text dans vos outils.

---

## 📄 RAG Framework

### 16. PrivateGPT

- **Courte** : Framework RAG pour chatter avec vos documents en local, axé entreprise.
- **Repo** : `github.com/zylon-ai/private-gpt` | ⭐ ~55k | Licence : Apache 2.0
- **Tags** : `rag`, `documents`, `privacy`, `enterprise`, `api`
- **Longue** :

> PrivateGPT est un framework RAG developer-centric basé sur LlamaIndex. Il permet de chatter avec vos documents (PDF, code, notes) en local. API compatible OpenAI, déployable on-premise pour la conformité.
>
> **Fonctionnalités clés** :
> - RAG sur documents locaux (PDF, code, markdown)
> - Built on LlamaIndex + FastAPI
> - API compatible OpenAI
> - Deploy on-premise pour conformité (GDPR, etc.)
> - Extensible et customizable
>
> **Pertinent pour vous si** : Vous gérez des documents sensibles et voulez un assistant IA qui ne les envoie jamais dans le cloud.

---

### 17. AnythingLLM

- **Courte** : App desktop all-in-one pour chatter avec vos documents, drag-and-drop.
- **Repo** : `github.com/Mintplex-Labs/anything-llm` | ⭐ ~35k | Licence : MIT
- **Tags** : `rag`, `documents`, `desktop`, `drag-drop`, `all-in-one`
- **Longue** :

> AnythingLLM est une application desktop qui rend le RAG accessible à tous. Drag-and-drop vos fichiers, choisissez votre modèle (local ou cloud), et commencez à poser des questions. Gère l'ingestion, le chunking, et le vector storage automatiquement.
>
> **Fonctionnalités clés** :
> - Desktop app offline (drag-and-drop)
> - Ingestion automatique (chunking + vectorisation)
> - Support multi-LLM (local Ollama ou API cloud)
> - Agent workflows intégrés
> - Multi-utilisateurs avec rôles admin
>
> **Pertinent pour vous si** : Vous voulez chatter avec vos fichiers locaux sans configuration technique, juste drag-and-drop.

---

## 🛠️ Dev Tool

### 18. Open Interpreter

- **Courte** : Interface langage naturel pour contrôler votre ordinateur via code.
- **Repo** : `github.com/OpenInterpreter/open-interpreter` | ⭐ ~58k | Licence : AGPL 3.0
- **Tags** : `automation`, `natural-language`, `code-execution`, `local`, `computer-control`
- **Longue** :

> Open Interpreter transforme votre terminal en interface langage naturel. Demandez en français de créer des fichiers, analyser des données, contrôler un navigateur — il génère et exécute le code correspondant (Python, JavaScript, Shell).
>
> **Fonctionnalités clés** :
> - Exécution locale de code généré (Python, JS, Shell)
> - Création/édition de documents et fichiers
> - Analyse de datasets
> - Contrôle de navigateur
> - Multi-LLM (OpenAI, Anthropic, modèles locaux)
>
> **Pertinent pour vous si** : Vous voulez automatiser des tâches sur votre ordinateur en décrivant simplement ce que vous voulez en langage naturel.

---

### 19. Jan.ai

- **Courte** : Application desktop ChatGPT-like 100% offline et open source.
- **Repo** : `github.com/janhq/jan` | ⭐ ~25k | Licence : AGPL 3.0
- **Tags** : `desktop`, `offline`, `chatgpt-like`, `privacy`, `local`
- **Longue** :

> Jan est une application desktop qui reproduit l'expérience ChatGPT mais tourne 100% en local. Interface intuitive, téléchargement de modèles en un clic, et serveur API local compatible OpenAI pour intégration avec d'autres outils.
>
> **Fonctionnalités clés** :
> - Interface ChatGPT-like desktop
> - 100% offline, données jamais envoyées
> - Téléchargement de modèles en un clic
> - Serveur API local compatible OpenAI
> - Support Llama, Gemma, Qwen, et plus
>
> **Pertinent pour vous si** : Vous voulez une expérience ChatGPT gratuite, privée, et offline sur votre desktop.

---

## 📊 Tableau Récapitulatif

| # | Outil | Catégorie | Difficulté d'intégration | Priorité MVP |
|---|-------|-----------|--------------------------|-------------|
| 1 | Ollama | LLM Runtime | 🟢 Facile | ✅ P1 |
| 2 | llama.cpp | LLM Runtime | 🔴 Avancé | ❌ P3 |
| 3 | LocalAI | LLM Runtime | 🟡 Moyen | ❌ P2 |
| 4 | Aider | Coding | 🟡 Moyen | ✅ P1 |
| 5 | gptme | Coding | 🟢 Facile | ❌ P2 |
| 6 | Continue.dev | Coding | 🔴 Avancé | ❌ P3 |
| 7 | CrewAI | Agent | 🟡 Moyen | ❌ P2 |
| 8 | AutoGen | Agent | 🟡 Moyen | ❌ P2 |
| 9 | LangChain | Agent | 🔴 Avancé | ❌ P3 |
| 10 | Ruflo | Orchestrator | 🟢 Facile | ✅ P0 |
| 11 | Fabric | Prompt | 🟢 Facile | ✅ P1 |
| 12 | Caveman | Prompt | 🟢 Facile | ✅ P0 |
| 13 | ComfyUI | Image | 🔴 Avancé | ❌ P3 |
| 14 | A1111 | Image | 🔴 Avancé | ❌ P3 |
| 15 | Whisper.cpp | Speech | 🟡 Moyen | ❌ P2 |
| 16 | PrivateGPT | RAG | 🟡 Moyen | ❌ P2 |
| 17 | AnythingLLM | RAG | 🟡 Moyen | ❌ P2 |
| 18 | Open Interpreter | Dev Tool | 🟡 Moyen | ❌ P2 |
| 19 | Jan.ai | Desktop | 🔴 Avancé | ❌ P3 |

### Recommandation MVP (5 premiers plugins)

1. **Ruflo** — Orchestration (preuve de concept originale)
2. **Caveman** — Prompt skill (intégration triviale, fichier markdown)
3. **Ollama** — LLM Runtime (le plus populaire, CLI simple)
4. **Aider** — Coding assistant (pip install, très populaire)
5. **Fabric** — Prompt patterns (CLI, modular, complémentaire)
