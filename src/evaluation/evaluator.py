# =============================================================================
# MODULE : evaluator.py
# Rôle   : mesurer la qualité des réponses du système RAG
# =============================================================================
#
# L'évaluation d'un système RAG, c'est comparer ce qu'il répond avec
# ce qu'il aurait dû répondre (la réponse de référence du jeu de test).
#
# Plutôt que de faire une comparaison mot à mot (trop rigide), on utilise
# un LLM comme "juge" : on lui demande si les deux réponses ont le même
# sens, et il répond OUI ou NON.
# Cette technique s'appelle LLM-as-a-judge.
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Les imports
# ─────────────────────────────────────────────────────────────────────────────
# Tu auras besoin de :
#   - json
#   - os
#   - ChatMistralAI  (depuis langchain_mistralai)
#   - RetrievalQA    (depuis langchain.chains)
#   - load_dotenv
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Définir le prompt du juge
# ─────────────────────────────────────────────────────────────────────────────
# Définis une constante EVAL_PROMPT avec ce prompt :
#
#   Tu es un juge impartial chargé de comparer deux réponses.
#   Réponds uniquement par OUI si les deux réponses ont le même sens
#   et les mêmes informations essentielles,
#   ou par NON si elles diffèrent sur un point important.
#
#   Réponse attendue : {expected}
#   Réponse obtenue  : {actual}
#
#   Verdict (OUI ou NON) :
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Fonction evaluate(chain, qa_dataset_path)
# ─────────────────────────────────────────────────────────────────────────────
# Cette fonction évalue la qualité du RAG sur le jeu de données annoté.
#
# Enchaîne dans l'ordre :
#
#   1. Charge le fichier JSON du jeu de test avec json.load()
#
#   2. Instancie le LLM juge :
#      ChatMistralAI(model="mistral-large-latest", temperature=0)
#      (temperature=0 pour des verdicts déterministes et reproductibles)
#
#   3. Pour chaque paire question/réponse du jeu de test :
#
#      a. Appelle le RAG avec chain({"query": item["question"]})
#         et récupère la réponse : result["result"]
#
#      b. Formate le prompt du juge avec expected et actual
#
#      c. Appelle le juge : judge.invoke(prompt_formate).content.strip()
#
#      d. Détermine si la réponse est correcte :
#         correct = verdict.upper() == "OUI"
#
#      e. Ajoute un dict à ta liste de résultats :
#         { "question", "expected", "actual", "correct" }
#
#   4. Calcule le score :
#      score = nombre de "correct" / total
#
#   5. Affiche un résumé : "Score : X/Y (Z%)"
#
#   6. Retourne un dict :
#      { "score": float, "details": liste_des_résultats }
#
# Chemin par défaut : qa_dataset_path = "data/processed/qa_dataset.json"
