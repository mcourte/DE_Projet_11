# POC RAG – Puls-Events : Recommandation d'Événements Culturels

Proof of Concept d'un système RAG (Retrieval-Augmented Generation) pour recommander des événements culturels à partir des données Open Agenda.

**Stack technique :** Python 3.11 · LangChain · Mistral AI · FAISS

---

## Architecture du projet

```
OCR_Projet_11/
├── data/
│   ├── raw/              # Données brutes récupérées depuis Open Agenda
│   └── processed/        # Données nettoyées et structurées (JSON/CSV)
├── src/
│   ├── data_collection/
│   │   ├── open_agenda_client.py   # Client API Open Agenda
│   │   └── preprocessor.py        # Nettoyage, filtrage (<1 an, région)
│   ├── vectorstore/
│   │   ├── embeddings.py           # Génération des embeddings (Mistral)
│   │   └── faiss_store.py          # Création et gestion de l'index FAISS
│   ├── rag/
│   │   ├── chain.py                # Chaîne RAG LangChain
│   │   └── chatbot.py              # Interface chatbot (CLI)
│   └── evaluation/
│       ├── dataset_generator.py    # Génération du jeu de données Q/R annoté
│       └── evaluator.py            # Mesure de qualité des réponses
├── scripts/
│   ├── build_vectorstore.py        # Reconstruit la base vectorielle complète
│   └── run_chatbot.py              # Lance le chatbot en mode interactif
├── tests/
│   └── test_data_pipeline.py       # Tests unitaires (fraîcheur + région des données)
├── notebooks/
│   └── exploration.ipynb           # Exploration et prototypage
├── .env.example
├── requirements.txt
└── README.md
```

---

## Étapes pour lancer le projet

### Étape 1 — Télécharger le code

Cliquer sur le bouton vert **\<\> Code** en haut de la page GitHub, puis sur **Download ZIP**.
Extraire l'ensemble des fichiers dans le dossier où vous souhaitez stocker le projet et les données.

### Étape 2 — Installer Python et ouvrir le terminal

Télécharger [Python](https://www.python.org/downloads/) et [l'installer](https://fr.wikihow.com/installer-Python).

Ouvrir le terminal de commande :
- **Windows** : [démarche à suivre](https://support.kaspersky.com/fr/common/windows/14637#block0)
- **Mac OS** : [démarche à suivre](https://support.apple.com/fr-fr/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac)
- **Linux** : ouvrir directement le terminal de commande

### Étape 3 — Créer un environnement virtuel

```bash
# Créer l'environnement
python3 -m venv env

# Activer l'environnement — Linux / Mac OS
source env/bin/activate

# Activer l'environnement — Windows
env\Scripts\activate.bat
```

### Étape 4 — Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 5 — Créer le fichier `.env`

Copier `.env.example` en `.env` (le `.env` est ignoré par git, il peut contenir
des secrets sans risque) :

```bash
# Linux / Mac OS
cp .env.example .env

# Windows
copy .env.example .env
```

---

## Utilisation

### Construire la base vectorielle

```bash
python scripts/build_vectorstore.py
```

Ce script enchaîne automatiquement :
1. Récupération des événements depuis Open Agenda (région + 1 an glissant)
2. Nettoyage et structuration des données
3. Découpage en chunks
4. Vectorisation via l'API Mistral
5. Indexation dans FAISS et sauvegarde locale

### Lancer le chatbot

```bash
python scripts/run_chatbot.py
```

### Lancer les tests unitaires

```bash
pytest tests/ -v
```

---

## Variables d'environnement

| Variable | Description |
|---|---|
| `MISTRAL_API_KEY` | Clé API Mistral AI |
| `OPEN_AGENDA_API_KEY` | Clé API Open Agenda |
| `TARGET_CITY` | Ville ciblée (ex : `Paris`) |
| `TARGET_REGION` | Région ciblée (ex : `Île-de-France`) |
