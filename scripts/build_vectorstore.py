# =============================================================================
# SCRIPT : build_vectorstore.py
# Rôle   : script principal pour (re)construire la base vectorielle complète
# =============================================================================
#
# Ce script est le point d'entrée pour mettre à jour les données.
# Tu le lanceras depuis le terminal avec :
#   python scripts/build_vectorstore.py
#
# Il orchestre dans l'ordre les 3 grandes étapes du pipeline de données :
#   Étape 1 → Collecte   (open_agenda_client)
#   Étape 2 → Nettoyage  (preprocessor)
#   Étape 3 → Indexation (faiss_store)
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Ajouter le répertoire racine au sys.path
# ─────────────────────────────────────────────────────────────────────────────
# Comme ce script est dans le dossier scripts/ et non à la racine,
# Python ne sait pas où trouver le dossier src/.
# Tu dois ajouter manuellement la racine du projet au chemin de recherche :
#
#   import sys, os
#   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Les imports
# ─────────────────────────────────────────────────────────────────────────────
# Après avoir fixé le sys.path, importe :
#   - load_dotenv                              (depuis dotenv)
#   - fetch_events, save_raw_events            (depuis src.data_collection.open_agenda_client)
#   - preprocess                               (depuis src.data_collection.preprocessor)
#   - build_index                              (depuis src.vectorstore.faiss_store)
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Fonction main()
# ─────────────────────────────────────────────────────────────────────────────
# Enchaîne dans l'ordre :
#
#   1. load_dotenv()
#   2. Lire TARGET_CITY et TARGET_REGION depuis os.getenv()
#   3. Afficher "Étape 1/3 — Collecte des événements..."
#      → appeler fetch_events(city, region) puis save_raw_events(events)
#   4. Afficher "Étape 2/3 — Nettoyage des données..."
#      → appeler preprocess() et récupérer le DataFrame retourné
#   5. Afficher "Étape 3/3 — Construction de l'index FAISS..."
#      → appeler build_index(df)
#   6. Afficher "Base vectorielle construite avec succès."
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — Protection if __name__ == "__main__"
# ─────────────────────────────────────────────────────────────────────────────
# Ne pas oublier d'appeler main() uniquement si le script est exécuté
# directement (pas importé par un autre module) :
#
#   if __name__ == "__main__":
#       main()
