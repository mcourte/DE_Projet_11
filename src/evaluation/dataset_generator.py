# =============================================================================
# MODULE : dataset_generator.py
# Rôle   : générer automatiquement un jeu de données annoté (questions / réponses)
# =============================================================================
#
# Pour évaluer la qualité du RAG, on a besoin d'un jeu de test avec des
# questions et leurs réponses "de référence" (ce qu'on appelle le gold standard).
#
# Créer ce jeu à la main serait long. L'idée ici est de demander à Mistral
# de générer des questions et réponses à partir des événements du CSV.
# Ce n'est pas parfait, mais c'est suffisant pour un POC.
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Les imports
# ─────────────────────────────────────────────────────────────────────────────
# Tu auras besoin de :
#   - json
#   - os
#   - pandas
#   - ChatMistralAI  (depuis langchain_mistralai)
#   - PromptTemplate (depuis langchain.prompts)
#   - load_dotenv
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Définir le prompt de génération
# ─────────────────────────────────────────────────────────────────────────────
# Définis une constante GENERATION_PROMPT (chaîne de caractères) avec ce prompt :
#
#   Tu es un testeur d'application. À partir de l'événement culturel suivant,
#   génère une question naturelle qu'un utilisateur pourrait poser à un chatbot,
#   ainsi que la réponse précise attendue.
#
#   Événement :
#   - Titre : {title}
#   - Description : {description}
#   - Ville : {city}
#   - Date : {first_date}
#
#   Réponds uniquement en JSON valide, sans texte autour :
#   {{"question": "...", "expected_answer": "..."}}
#
# Note : les doubles accolades {{ }} sont nécessaires pour échapper les
# accolades littérales dans une f-string / PromptTemplate.
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Fonction generate_qa_pairs(df, n_samples=20, output_path)
# ─────────────────────────────────────────────────────────────────────────────
# Cette fonction génère n_samples paires question/réponse à partir du DataFrame.
#
# Enchaîne dans l'ordre :
#
#   1. Instancie ChatMistralAI(model="mistral-large-latest", temperature=0.7)
#      (temperature plus haute = questions plus variées)
#
#   2. Crée un PromptTemplate avec GENERATION_PROMPT
#
#   3. Échantillonne le DataFrame : df.sample(min(n_samples, len(df)))
#
#   4. Pour chaque ligne de l'échantillon :
#      a. Formate le prompt avec les données de l'événement
#         (tronque la description à 400 caractères pour limiter les tokens)
#      b. Appelle llm.invoke(prompt_formaté)
#      c. Récupère response.content (c'est le JSON retourné par Mistral)
#      d. Si la réponse est entourée de ```json ... ```, nettoie-la d'abord
#      e. Parse avec json.loads()
#      f. Ajoute l'id de l'événement source : qa["source_event_id"] = row["id"]
#      g. Ajoute la paire à ta liste
#      h. En cas d'erreur de parsing JSON, passe à l'événement suivant (continue)
#
#   5. Sauvegarde la liste avec json.dump() dans output_path
#
#   6. Affiche le nombre de paires générées et retourne la liste
#
# Chemin par défaut : output_path = "data/processed/qa_dataset.json"
