# Script de soutenance — Puls-Events RAG *(15 min)*

---

## Introduction *(1 min)*

Bonjour. Je vais vous présenter **Puls-Events**, un système de recommandation d'événements culturels basé sur une architecture **RAG** — Retrieval-Augmented Generation.

La problématique est simple : comment permettre à un utilisateur de trouver des événements culturels locaux en langage naturel, sans moteur de recherche classique, et sans que le modèle hallucine des événements qui n'existent pas ?

La réponse que j'ai implémentée : indexer les données réelles de l'API Open Agenda dans une base vectorielle, et faire répondre Mistral uniquement à partir de ce contexte.

---

## 1. Configuration de l'environnement *(3 min)*

### Choix techniques

Pour répondre aux besoins du projet — recherche vectorielle rapide, génération NLP de qualité, orchestration des briques — j'ai retenu la stack suivante :

- **LangChain** pour l'orchestration du pipeline RAG
- **FAISS** pour la recherche vectorielle en mémoire — très rapide sur des corpus de quelques milliers de documents
- **Mistral AI** avec deux modèles distincts :
  - `mistral-embed` pour la vectorisation sémantique
  - `mistral-large-latest` à température 0.1 pour la génération de réponses précises et factuelles
- **Streamlit** pour l'interface web

### Performances et optimisation

La contrainte principale côté vectorisation, c'est l'API Mistral qui n'accepte pas des batchs de taille arbitraire. Sur un corpus de 1 078 chunks, un envoi en bloc provoquait une erreur 400.

J'ai mesuré et résolu ce goulot d'étranglement en **découpant la vectorisation en batchs de 32 chunks** — c'est le critère CE3 sur les optimisations pour réduire les goulots d'étranglement. Voici le code :

```python
for i in range(0, len(chunks), 32):
    batch = chunks[i : i + 32]
    faiss_index.add_documents(batch)
```

Résultat : pipeline de vectorisation stable, aucune perte de données.

Pour la recherche, FAISS est chargé **une seule fois en mémoire** via `@st.cache_resource` — le temps de réponse reste stable quelle que soit la fréquence des requêtes.

---

## 2. Pipeline de nettoyage des données *(3 min)*

### Collecte et particularités de l'API

L'API Open Agenda v2 a une structure non documentée que j'ai dû investiguer. Les événements n'exposent pas de tableau `timings[]` comme attendu, mais trois champs distincts : `firstTiming`, `nextTiming`, `lastTiming`. Ce genre d'incohérence de format, c'est exactement le CE1 sur la gestion des incohérences de données.

J'ai adapté la fonction de filtrage temporel en conséquence :

```python
for key in ("firstTiming", "nextTiming", "lastTiming"):
    begin_str = (event.get(key) or {}).get("begin", "")
```

Le `or {}` protège contre les valeurs `null` — autre incohérence réelle rencontrée sur le jeu de données.

### Filtrage géographique

L'API ne supporte pas le filtre `city[]` sur l'endpoint `/agendas/{uid}/events`. J'ai donc appliqué le filtre **en post-traitement**, dans le préprocesseur :

```python
df_cleaned = df_cleaned[df_cleaned["city"].str.lower() == TARGET_CITY.lower()]
```

Cela garantit que seuls les événements de la ville cible entrent dans l'index.

### Automatisation et traçabilité

Le pipeline complet — collecte, nettoyage, vectorisation, indexation — s'exécute en **une seule commande** :

```bash
python scripts/build_vectorstore.py
```

Chaque étape est loguée avec horodatage. Le pipeline est **entièrement reproductible** : il suffit de modifier `OPEN_AGENDA_UID` et `TARGET_CITY` dans le `.env` pour cibler une autre ville.

### Tests automatisés

J'ai mis en place **7 tests unitaires** qui vérifient en continu la cohérence des données — c'est le CE3 sur les mécanismes automatisés :

- Existence des fichiers bruts et nettoyés
- Fraîcheur temporelle (aucun événement de plus d'un an)
- Présence des colonnes requises
- Absence de descriptions vides
- Cohérence géographique
- Volume minimum d'événements

```bash
pytest tests/ -v
# → 7 passed
```

---

## 3. Modèle RAG *(3 min)*

### Choix du modèle

`mistral-large-latest` répond aux exigences de qualité pour de la génération factuelle en français. La température à 0.1 minimise les hallucinations — le modèle reste ancré dans le contexte fourni.

### Personnalisation du prompt

Le prompt système est conçu pour contraindre le modèle à n'utiliser **que** les documents récupérés par FAISS :

```
Tu es un assistant spécialisé dans les événements culturels.
Réponds uniquement à partir du contexte fourni.
Si l'information n'est pas dans le contexte, dis-le clairement.
```

C'est le CE2 sur la personnalisation aux spécificités métiers. Résultat concret : le modèle ne fabrique jamais d'événements inexistants.

### Architecture LangChain

LangChain orchestre l'interaction entre les trois briques — c'est le CE3 sur l'intégration :

1. La question utilisateur est vectorisée via `mistral-embed`
2. FAISS retourne les **5 documents les plus proches** (`k=5`)
3. Ces documents sont injectés dans le prompt de `mistral-large-latest`
4. La réponse est retournée avec les sources

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever,
                                     return_source_documents=True)
```

---

## 4. Démonstration *(3 min)*

> *(Lancer : `streamlit run app.py`)*

Je vais vous poser trois questions représentatives.

**Question 1 — Générale :**
> "Quels concerts sont prévus à Rennes ?"

> *(Attendre la réponse — montrer les sources dans l'expander)*

Vous voyez que la réponse cite des événements réels avec leur date et leur lien Open Agenda.

**Question 2 — Thématique :**
> "Y a-t-il des activités pour enfants ce mois-ci ?"

> *(Attendre la réponse)*

**Question 3 — Hors périmètre :**
> "Quels sont les événements à Paris ?"

> *(Attendre la réponse — le modèle doit indiquer qu'il n'a pas l'information)*

C'est le comportement attendu : le modèle ne répond pas au-delà de son contexte. Pas d'hallucination.

---

## Conclusion *(1 min)*

Pour résumer :

| Brique | Rôle |
|---|---|
| Open Agenda API | Source de données réelles, 1 an glissant |
| Préprocesseur | Nettoyage, filtrage géographique, tests automatisés |
| FAISS + mistral-embed | Index vectoriel, recherche sémantique en mémoire |
| mistral-large-latest | Génération ancrée dans le contexte |
| LangChain | Orchestration de l'ensemble |
| Streamlit | Interface utilisateur |

Le POC valide que la stack est opérationnelle sur des données réelles. Il est **configurable en deux variables** pour cibler n'importe quelle ville disposant d'un agenda Open Agenda.

Merci — je suis disponible pour vos questions.

---

*Durée estimée : 14–16 min selon le débit de parole et les temps de réponse de l'API en démo.*
