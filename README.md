# 🧠 Synapse Studio V3 - Agentic Swarm

**Synapse Studio V3** est une plateforme avancée de débat asynchrone multi-agents. Contrairement aux architectures traditionnelles et synchrones (où les agents parlent tour à tour), ce système permet l'exécution **parallèle et concurrente** de plusieurs agents d'Intelligence Artificielle spécialisés qui débattent et collaborent en temps réel autour d'idées de projets, de conceptions architecturales, de stratégies et de code.

![Agentic Swarm](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B)

---

## ✨ Fonctionnalités Principales

- 🔄 **Débat Parallèle Concurrentiel** : Échappe au séquencement de LangGraph via l'utilisation d'`asyncio`. Les agents agissent et réfléchissent simultanément de façon indépendante, accélérant la création de solutions globales.
- ⚡ **Temps Réel avec WebSockets** : Une interface backend FastAPI couplée à un frontend Streamlit avec des composants de communication WebSocket (en full-duplex). Le flux de pensée (stream) des agents est diffusé instantanément sur l'interface.
- 🎯 **Moteur de Convergence Mathématique** : Un système autonome pour évaluer la distance de consensus (Cosine Similarity) entre les réponses des agents via des algorithmes d'Embeddings (`ChromaDB` / `MiniLM`) et `scikit-learn`.
- 👨‍💻 **Human-in-the-Loop** : L'utilisateur peut intervenir dans le débat à la "Slack-style", corriger la trajectoire, et poser des questions en plein vol. L'interface premium de type chat supporte l'interaction fluide avec différents rôles IA.
- 🤖 **Diversité Cognitive** : L'équipe est composée de profils experts dotés de prompts spécialisés : `Stratège`, `Architecte`, `Ingénieur`, `Critique`, `Product Owner`, `Business`, et un `Modérateur`.

---

## 🏗️ Architecture Technologique

L'architecture est totalement asynchrone et guidée par les événements. Elle est structurée en trois couches principales :

1. **Frontend (Streamlit)** : Interface graphique luxueuse, moderne et réactive (Dark Mode exclusif inspiré du style SaaS). Il permet une visualisation précise via un suivi en temps réel des logs des messages.
2. **Backend (FastAPI & WebSockets)** : Pipeline solide avec route de websockets `ws://localhost:8000/ws/debate`. Capte les impressions des agents pour les diffuser à l'utilisateur.
3. **Core IA (LLMs & Message Queues)** : Le cerveau des opérations s'appuie sur `asyncio.gather`. Des points de connexion asynchrones pour différents fournisseurs LLM (Groq, DeepSeek, OpenRouter) sont inclus pour esquiver les limitations de requêtes API (Rate limits). 

Pour une vision approfondie de l'architecture, consultez le fichier [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 📂 Structure du Répertoire

- `app.py` - Point de départ du Front-End (Streamlit). Interface visuelle du terminal de chat avec les agents.
- `main.py` - Point de départ du Back-End (FastAPI / Uvicorn Server).
- `api/routes.py` - Les gestionnaires du tunnel WebSockets pour le transfert de données en temps réel aux clients connectés.
- `agents/specialists.py & base_agent.py` - Configurations et prompts détaillés de chaque bot du "Swarm".
- `core/orchestrator.py` - Mécanisme orchestrateur gérant le cycle de vie du débat et le regroupement `asyncio`.
- `core/embeddings.py` - Intégration de Scikit-Learn/ChromaDB pour calculer l'indice de consensus "cosinus-distance".
- `core/message_queue.py` - Une base de données d'historique en mémoire (Lock Asyncio) centralisée gérant le flux d'échange sans conflits.
- `start_v3.bat` - Macro de lancement unifiée (Windows).
- `requirements.txt` - Configuration des dépendances.

---

## 🚀 Guide d'Installation Rapide

### Prérequis
- Python 3.10 ou supérieur.
- Clés API pour vos fournisseurs LLM, à configurer dans `.env` (ex: `GROQ_API_KEY`, `OPENROUTER_API_KEY`, etc.).

### 1️⃣ Cloner et Préparer l'Environnement

```bash
git clone https://github.com/votre_profil/synapse-studio.git
cd synapse-studio
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 2️⃣ Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 3️⃣ Lancer l'Application (Lancement unifié Microsoft Windows)

Double-cliquez sur le fichier `start_v3.bat` ou lancez la commande suivante depuis votre terminal :
```bash
.\start_v3.bat
```

*Le script se charge de démarrer le serveur FastAPI en arrière-plan sur le port 8000 et ouvre l'interface utilisateur Streamlit sur le port 8501.*

### 🛠️ Lancement Séparé (Linux / MacOS / Scripts Manuels)

**Termial 1 : Backend**
```bash
uvicorn main:app --reload --port 8000
```
**Terminal 2 : Frontend**
```bash
streamlit run app.py
```

---

## 💡 Comment ça Marche ?

1. Entrez un sujet complexe ou une architecture à designer dans l'interface (ex: *"Je veux créer une plateforme SaaS de machine learning pour les hôpitaux"*).
2. Cliquez sur **🚀 Start Debate**.
3. Observez l'**Architecte**, le **Stratège**, l'**Ingénieur**, etc., se lancer simultanément sur la problématique via WebSocket Stream. 
4. Insérez une **"Correction"** si le système s'oriente mal, les agents pivoterons sur-le-champ lors du round suivant.
5. Une fois que la similarité cosinus entre les réponses des agents atteint le seuil (Ex: `0.88`), le système arrête le débat de lui-même de manière convergente. 
6. Utilisez ensuite l'option en Sidebar pour archiver (**Conversation Export**) votre résultat validé au format `.txt`.

---

## 🤝 Contribution
Toute Pull Request ajoutant un nouveau modèle LLM, un nouveau workflow d'Agent ou optimisant le moteur de Consensus Embeddings est la bienvenue !
