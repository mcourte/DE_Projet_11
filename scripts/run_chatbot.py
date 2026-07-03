# =============================================================================
# SCRIPT : run_chatbot.py
# Rôle   : lancer le chatbot RAG en mode interactif
# =============================================================================
#
# Ce script suppose que la base vectorielle a déjà été construite
# avec build_vectorstore.py. Si ce n'est pas le cas, lance d'abord :
#   python scripts/build_vectorstore.py
#
# Ensuite lance ce script avec :
#   python scripts/run_chatbot.py
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Ajouter le répertoire racine au sys.path
# ─────────────────────────────────────────────────────────────────────────────
# Même manipulation que dans build_vectorstore.py :
#
#   import sys, os
#   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Les imports
# ─────────────────────────────────────────────────────────────────────────────
# Importe :
#   - load_index       (depuis src.vectorstore.faiss_store)
#   - build_rag_chain  (depuis src.rag.chain)
#   - run_interactive  (depuis src.rag.chatbot)
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Fonction main()
# ─────────────────────────────────────────────────────────────────────────────
# Enchaîne dans l'ordre :
#
#   1. Afficher "Chargement de l'index FAISS..."
#      → vectorstore = load_index()
#
#   2. Afficher "Initialisation de la chaîne RAG..."
#      → chain = build_rag_chain(vectorstore)
#
#   3. Lancer la boucle de conversation :
#      → run_interactive(chain)
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — Protection if __name__ == "__main__"
# ─────────────────────────────────────────────────────────────────────────────
#   if __name__ == "__main__":
#       main()
