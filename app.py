# =============================================================================
# FICHIER : app.py
# Rôle    : interface web du chatbot RAG avec Streamlit
# =============================================================================
#
# C'est le fichier que Streamlit exécute. Lance-le avec :
#   streamlit run app.py
#
# Streamlit fonctionne différemment d'un script Python classique :
# le fichier est ré-exécuté de haut en bas à chaque interaction utilisateur.
# Pour éviter de recharger l'index FAISS à chaque message, on utilise
# st.cache_resource qui garde les objets lourds en mémoire entre les runs.
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Les imports
# ─────────────────────────────────────────────────────────────────────────────
# Tu auras besoin de :
#   - streamlit as st
#   - load_index      (depuis src.vectorstore.faiss_store)
#   - build_rag_chain (depuis src.rag.chain)
#   - load_dotenv
#
# N'oublie pas d'ajouter le répertoire racine au sys.path si nécessaire
# (même technique que dans les scripts/).
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Charger l'index et la chaîne RAG (avec cache)
# ─────────────────────────────────────────────────────────────────────────────
# Utilise le décorateur @st.cache_resource pour que l'index FAISS et la chaîne
# RAG ne soient chargés qu'une seule fois, même si Streamlit ré-exécute le
# fichier à chaque message.
#
# Crée une fonction load_chain() décorée avec @st.cache_resource :
#   1. load_dotenv()
#   2. vectorstore = load_index()
#   3. return build_rag_chain(vectorstore)
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Configuration de la page
# ─────────────────────────────────────────────────────────────────────────────
# En haut du script (avant tout autre st.*), configure la page :
#   st.set_page_config(
#       page_title="Puls-Events – Assistant culturel",
#       page_icon="🎭",
#       layout="centered"
#   )
#
# Ajoute ensuite un titre et une courte description :
#   st.title("🎭 Assistant événements culturels")
#   st.caption("Posez vos questions sur les événements culturels de votre région.")
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — Gérer l'historique des messages
# ─────────────────────────────────────────────────────────────────────────────
# Streamlit efface les variables à chaque re-run. Pour conserver l'historique
# de la conversation, utilise st.session_state.
#
# Au début de l'app, initialise l'historique s'il n'existe pas encore :
#   if "messages" not in st.session_state:
#       st.session_state.messages = []
#
# Chaque message est un dict : {"role": "user" ou "assistant", "content": "..."}
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 5 — Afficher l'historique existant
# ─────────────────────────────────────────────────────────────────────────────
# Parcours st.session_state.messages et affiche chaque message avec :
#   with st.chat_message(msg["role"]):
#       st.markdown(msg["content"])
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 6 — Champ de saisie et traitement de la question
# ─────────────────────────────────────────────────────────────────────────────
# Utilise st.chat_input() pour afficher la barre de saisie en bas de page :
#   question = st.chat_input("Que cherchez-vous comme événement ?")
#
# Si l'utilisateur a saisi quelque chose (question is not None) :
#
#   a. Ajoute le message utilisateur à l'historique et affiche-le :
#      st.session_state.messages.append({"role": "user", "content": question})
#      with st.chat_message("user"):
#          st.markdown(question)
#
#   b. Appelle la chaîne RAG et affiche la réponse en streaming simulé :
#      with st.chat_message("assistant"):
#          with st.spinner("Recherche en cours..."):
#              result = chain({"query": question})
#              reponse = result["result"]
#          st.markdown(reponse)
#
#   c. Affiche les sources dans un expander (bloc repliable) :
#      sources = result.get("source_documents", [])
#      if sources:
#          with st.expander("📎 Sources utilisées"):
#              for doc in sources[:3]:
#                  st.markdown(f"**{doc.metadata['title']}**")
#                  st.markdown(f"📅 {doc.metadata['first_date']}  |  🔗 {doc.metadata['url']}")
#                  st.divider()
#
#   d. Ajoute la réponse de l'assistant à l'historique :
#      st.session_state.messages.append({"role": "assistant", "content": reponse})
