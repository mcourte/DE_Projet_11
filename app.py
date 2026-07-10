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
    page_title="Puls-Events",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

  /* ── Background ── */
  .stApp { background: #0d0d1a; color: #e8e8f0; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #12122a 0%, #1a0a2e 100%);
    border-right: 1px solid #2d2d5a;
  }

  /* ── Hero header ── */
  .hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
  }
  .hero h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ff6ec7, #a855f7, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
  }
  .hero p {
    color: #9090b8;
    font-size: 1.05rem;
  }

  /* ── Chat bubbles ── */
  [data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
  }

  /* ── Input box ── */
  [data-testid="stChatInput"] textarea {
    background: #1a1a30 !important;
    border: 1.5px solid #4a4a8a !important;
    border-radius: 14px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }
  [data-testid="stChatInput"] textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 2px rgba(168,85,247,0.25) !important;
  }

  /* ── Source cards ── */
  .source-card {
    background: linear-gradient(135deg, #1a1a30 0%, #1e0a34 100%);
    border: 1px solid #3d3d6e;
    border-left: 4px solid #a855f7;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
  }
  .source-card:hover { border-left-color: #ff6ec7; }
  .source-card .title {
    font-weight: 700;
    font-size: 1rem;
    color: #e8e8f0;
    margin-bottom: 0.3rem;
  }
  .source-card .meta {
    font-size: 0.85rem;
    color: #7070a8;
  }
  .source-card .meta span { margin-right: 1rem; }
  .source-card a {
    color: #a855f7;
    text-decoration: none;
    font-size: 0.85rem;
  }
  .source-card a:hover { color: #ff6ec7; }

  /* ── Stat badges in sidebar ── */
  .stat-badge {
    background: #1a1a30;
    border: 1px solid #3d3d6e;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: #9090b8;
  }
  .stat-badge strong { color: #a855f7; }

  /* ── Suggestion pills ── */
  .pill-row { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin: 1rem 0 1.5rem; }
  .pill {
    background: #1e1e3a;
    border: 1px solid #4a4a7a;
    border-radius: 999px;
    padding: 0.35rem 1rem;
    font-size: 0.85rem;
    color: #c0c0e8;
    cursor: pointer;
  }

  /* ── Spinner ── */
  .stSpinner > div { border-top-color: #a855f7 !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0d0d1a; }
  ::-webkit-scrollbar-thumb { background: #3d3d6e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Chargement de l'index FAISS…")
def load_chain():
    vectorstore = load_index()
    return build_rag_chain(vectorstore)


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎉 Puls-Events")
    st.markdown("Assistant culturel propulsé par **RAG + Mistral AI**.")
    st.divider()

    city = os.getenv("TARGET_CITY", "votre ville")
    st.markdown(f"""
    <div class="stat-badge">📍 Périmètre : <strong>{city}</strong></div>
    <div class="stat-badge">🧠 Modèle : <strong>mistral-large-latest</strong></div>
    <div class="stat-badge">🗂️ Index : <strong>FAISS · mistral-embed</strong></div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Les réponses s'appuient uniquement sur les données Open Agenda indexées.")


# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🎉 Puls-Events</h1>
  <p>Trouvez des événements culturels près de chez vous — concerts, expos, ateliers…</p>
</div>
""", unsafe_allow_html=True)

SUGGESTIONS = [
    "🎵 Concerts ce week-end ?",
    "🎨 Expositions d'art à Rennes",
    "🎭 Spectacles pour enfants",
    "🏃 Activités sportives gratuites",
    "🍷 Événements festifs en soirée",
]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show suggestion pills only when conversation is empty
if not st.session_state.messages:
    pills_html = '<div class="pill-row">'
    for s in SUGGESTIONS:
        pills_html += f'<span class="pill">{s}</span>'
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)

# ── Chat history ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📎 Sources"):
                for src in msg["sources"]:
                    date_str = src["first_date"][:10] if src["first_date"] and src["first_date"] != "N/A" else "—"
                    link = f'<a href="{src["url"]}" target="_blank">↗ En savoir plus</a>' if src["url"] else ""
                    st.markdown(f"""
                    <div class="source-card">
                      <div class="title">{src['title']}</div>
                      <div class="meta">
                        <span>📅 {date_str}</span>
                        <span>📍 {src['city']}</span>
                      </div>
                      {link}
                    </div>
                    """, unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
question = st.chat_input("Que cherchez-vous comme événement ? ✨")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Je fouille les événements… 🔍"):
            try:
                chain = load_chain()
                result = chain({"query": question})
                reponse = result["result"]
                sources = format_sources(result.get("source_documents", []))
            except Exception as e:
                reponse = f"Oups, une erreur est survenue : {e}"
                sources = []

        st.markdown(reponse)

        if sources:
            with st.expander("📎 Sources"):
                for src in sources:
                    date_str = src["first_date"][:10] if src["first_date"] and src["first_date"] != "N/A" else "—"
                    link = f'<a href="{src["url"]}" target="_blank">↗ En savoir plus</a>' if src["url"] else ""
                    st.markdown(f"""
                    <div class="source-card">
                      <div class="title">{src['title']}</div>
                      <div class="meta">
                        <span>📅 {date_str}</span>
                        <span>📍 {src['city']}</span>
                      </div>
                      {link}
                    </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reponse,
        "sources": sources,
    })
