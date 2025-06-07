import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI
import os
from memory import load_memory, append_message, reset_memory
import glob

# ✅ Use Streamlit Cloud secret instead of .env
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not found in Streamlit secrets.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key

# 🧠 Load vector index
Settings.llm = OpenAI(model="gpt-4-turbo")
storage_context = StorageContext.from_defaults(persist_dir="luxor_index")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine(similarity_top_k=20)

# 🌌 Dark Mode Styling
st.set_page_config(page_title="Luxor - Speak to the Temple", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #121212;
        color: #e0d6c7;
        font-family: 'Georgia', serif;
    }
    .stApp {
        padding: 3rem 6rem;
    }
    h1 {
        color: #f5e4c3;
        font-family: 'Palatino Linotype', 'Georgia', serif;
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    h3 {
        color: #f5e4c3;
        border-bottom: 1px solid #d6a756;
        padding-bottom: 0.3rem;
        margin-top: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: #e0d6c7;
        font-weight: bold;
        border: 1px solid #d6a756;
    }
    .stExpanderHeader {
        font-weight: bold;
        color: #d6a756;
    }
    code {
        background-color: #222;
        color: #f4ecd8;
        padding: 0.75rem;
        border-radius: 0.5rem;
        display: block;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# 🛕 Title
st.title("🜂 Luxor, la Voz del Templo")
st.markdown("> *“El cuerpo humano es un templo. Su arquitectura es sagrada.”*  \n— Luxor")
st.markdown("---")

# 🗂️ Session browser
session_files = sorted(glob.glob("conversations/*.json"))
session_names = [os.path.splitext(os.path.basename(f))[0] for f in session_files]

st.markdown("### 📁 Selecciona o crea un hilo de conversación:")

selected = st.selectbox("Hilos disponibles:", options=session_names + ["Nuevo hilo..."], index=0)

if selected == "Nuevo hilo...":
    new_session = st.text_input("✍️ Nombre para el nuevo hilo:", value="")
    session_id = new_session if new_session else "default"
else:
    session_id = selected

if st.button("🧹 Reiniciar este hilo"):
    reset_memory(session_id)
    st.success(f"🧼 Memoria del hilo '{session_id}' limpiada.")

# 🌀 User Input
query = st.text_input("❓ Pregunta:")

if query:
    # 🧠 Include memory
    chat_history = load_memory(session_id)
    history_prompt = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in chat_history])
    full_query = f"{history_prompt}\n\nUser: {query}\nLuxor:"

    # 🔮 Ask Luxor
    response = query_engine.query(full_query)

    # 🧠 Store
    append_message(session_id, "user", query)
    append_message(session_id, "luxor", response.response)

    # 💬 Display
    st.markdown("### ✨ Respuesta de Luxor:")
    st.markdown(f"🜂 *{response.response}*")

    st.markdown("### 📜 Fuentes:")
    for node in response.source_nodes:
        meta = node.metadata
        file = meta.get("file_name", "Documento desconocido")
        page = meta.get("page_number", "?")
        line = meta.get("line_start", "?")

        with st.expander(f"📄 {file} — página {page}, línea {line}"):
            st.code(node.text.strip(), language="markdown")

    st.markdown("### 🧠 Fragmentos usados para responder:")
    for node in response.source_nodes:
        st.code(node.text[:400].strip() + "...", language="markdown")
