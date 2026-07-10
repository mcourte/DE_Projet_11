# 🎉 Puls-Events — Assistant RAG d'Événements Culturels

Proof of Concept d'un système RAG (Retrieval-Augmented Generation) pour recommander des événements culturels à partir des données **Open Agenda**.

**Stack technique :** Python 3.11 · LangChain · Mistral AI · FAISS · Streamlit

---

## Architecture du projet

```
OCR_Projet_11/
├── app.py                           # Interface Streamlit (chatbot web)
├── data/
│   ├── raw/                         # JSON brut Open Agenda (gitignored)
│   └── processed/                   # CSV nettoyé + index FAISS (gitignored)
├── src/
│   ├── data_collection/
│   │   ├── open_agenda_client.py    # Client API Open Agenda v2
│   │   └── preprocessor.py         # Nettoyage, filtrage (< 1 an, ville)
│   ├── vectorstore/
│   │   ├── embeddings.py            # Embeddings Mistral (mistral-embed)
│   │   └── faiss_store.py           # Index FAISS (batch_size=32)
│   ├── rag/
│   │   ├── chain.py                 # Chaîne RetrievalQA LangChain
│   │   └── chatbot.py               # Helper format_sources
│   └── evaluation/
│       ├── dataset_generator.py     # Génération jeu de données Q/R (Mistral)
│       └── evaluator.py             # Évaluation par juge Mistral
├── scripts/
│   ├── build_vectorstore.py         # Pipeline complet : collecte → index
│   └── run_chatbot.py               # Lance l'app Streamlit via subprocess
├── tests/
│   └── test_data_pipeline.py        # 7 tests unitaires (fraîcheur + géographie)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Installation

### 1 — Cloner le dépôt

```bash
git clone https://github.com/mcourte/DE_Projet_11.git
cd DE_Projet_11
```

### 2 — Créer un environnement virtuel

```bash
# Créer
python -m venv env

# Activer — Linux / Mac OS
source env/bin/activate

# Activer — Windows
env\Scripts\activate.bat
```

### 3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4 — Configurer les variables d'environnement

Copier `.env.example` en `.env` puis renseigner les valeurs :

```bash
# Linux / Mac OS
cp .env.example .env

# Windows
copy .env.example .env
```

---

## Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `MISTRAL_API_KEY` | ✅ | Clé API Mistral AI ([console.mistral.ai](https://console.mistral.ai)) |
| `OPEN_AGENDA_API_KEY` | ✅ | Clé publique Open Agenda (`oa_pk_…`) |
| `OPEN_AGENDA_UID` | ✅ | UID numérique de l'agenda ciblé (voir ci-dessous) |
| `TARGET_CITY` | ✅ | Ville ciblée (ex : `Rennes`) — filtre post-collecte |
| `TARGET_REGION` | ❌ | Région (ex : `Bretagne`) — informatif |

### Trouver l'UID d'un agenda Open Agenda

1. Rechercher un agenda sur [openagenda.com](https://openagenda.com)
2. Cliquer sur **Exporter** — l'URL API révèle l'UID : `/agendas/95408779/events`
3. Renseigner `OPEN_AGENDA_UID=95408779` dans `.env`

---

## Utilisation

### Construire la base vectorielle

```bash
python scripts/build_vectorstore.py
```

Le pipeline enchaîne automatiquement :
1. Collecte des événements via l'API Open Agenda (`/agendas/{uid}/events`)
2. Filtrage temporel (≤ 1 an) et géographique (`TARGET_CITY`)
3. Découpage en chunks (512 tokens, overlap 64)
4. Vectorisation par batches de 32 via `mistral-embed`
5. Indexation FAISS et sauvegarde dans `data/processed/`

### Lancer l'interface web

```bash
streamlit run app.py
# ou
python scripts/run_chatbot.py
```

L'app s'ouvre sur `http://localhost:8501` avec :
- Fond sombre, gradient violet/rose
- Suggestions de questions prédéfinies
- Cartes sources avec lien vers Open Agenda
- Bouton pour effacer la conversation

### Lancer les tests unitaires

```bash
pytest tests/ -v
```

7 tests couvrant : existence des fichiers, fraîcheur temporelle, colonnes requises, descriptions non vides, filtrage géographique, nombre minimum d'événements.

---

## Changer de ville / d'agenda

Il suffit de deux variables et d'une commande :

```bash
# 1. Mettre à jour .env
OPEN_AGENDA_UID=XXXXXXXX   # UID trouvé sur openagenda.com > Exporter
TARGET_CITY=NomVille

# 2. Reconstruire l'index
python scripts/build_vectorstore.py

# 3. Relancer l'app
streamlit run app.py
```
