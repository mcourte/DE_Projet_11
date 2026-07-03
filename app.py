import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
from src.vectorstore.faiss_store import load_index
from src.rag.chain import build_rag_chain
from src.rag.chatbot import format_sources

load_dotenv()

st.set_page_config(
    page_title="Puls-Events – Assistant culturel",
    page_icon="🎭",
    layout="centered",
)


@st.cache_resource
def load_chain():
    vectorstore = load_index()
    return build_rag_chain(vectorstore)


st.title("🎭 Assistant événements culturels")
st.caption("Posez vos questions sur les événements culturels de votre région.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Que cherchez-vous comme événement ?")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            try:
                chain = load_chain()
                result = chain({"query": question})
                reponse = result["result"]
                sources = format_sources(result.get("source_documents", []))
            except Exception as e:
                reponse = f"Une erreur est survenue : {e}"
                sources = []

        st.markdown(reponse)

        if sources:
            with st.expander("📎 Sources utilisées"):
                for source in sources:
                    st.markdown(f"**{source['title']}**")
                    st.markdown(f"📅 {source['first_date']}  |  📍 {source['city']}")
                    if source["url"]:
                        st.markdown(f"🔗 {source['url']}")
                    st.divider()

    st.session_state.messages.append({"role": "assistant", "content": reponse})
