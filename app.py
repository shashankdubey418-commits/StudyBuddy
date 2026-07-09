import os
import tempfile

import streamlit as st

from parser import extract_text
from chunker import chunk_text
from vector_store import VectorStore
from rag import answer_question, summarize_text

st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")

st.title("📚 StudyBuddy ")
st.caption(
    "Upload a PDF, DOCX, or PPTX — then ask questions or get a summary. "
    "Runs fully locally with Ollama, no API cost."
)

# --- Session state setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "full_text" not in st.session_state:
    st.session_state.full_text = ""
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None

# --- Sidebar: upload + settings ---
with st.sidebar:
    st.header("1. Upload your document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "pptx"])

    model_name = st.text_input(
        "Ollama model name",
        value="llama3.1:8b",
        help="Must match a model you've pulled with `ollama pull <model>`",
    )

    if uploaded_file is not None and uploaded_file.name != st.session_state.doc_name:
        with st.spinner("Reading and indexing your document..."):
            suffix = os.path.splitext(uploaded_file.name)[1]
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                text = extract_text(tmp_path)
                if not text.strip():
                    st.error("No text could be extracted from this file. It may be a scanned/image-only document.")
                else:
                    st.session_state.full_text = text

                    chunks = chunk_text(text)
                    store = VectorStore()
                    store.add_chunks(chunks)

                    st.session_state.vector_store = store
                    st.session_state.doc_name = uploaded_file.name
                    st.session_state.chat_history = []

                    st.success(f"Indexed {len(chunks)} chunks from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Failed to process file: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    if st.session_state.doc_name:
        st.info(f"Active document: **{st.session_state.doc_name}**")

    st.divider()
    st.markdown(
        "**Setup checklist:**\n"
        "1. Install [Ollama](https://ollama.com)\n"
        "2. Run `ollama pull llama3.1:8b`\n"
        "3. Run `ollama serve` (if not already running)\n"
        "4. `pip install -r requirements.txt`\n"
        "5. `streamlit run app.py`"
    )

# --- Main area ---
if not st.session_state.doc_name:
    st.warning("Upload a document from the sidebar to get started.")
else:
    tab1, tab2 = st.tabs(["💬 Ask Questions", "📝 Summarize"])

    with tab1:
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

        question = st.chat_input("Ask something about your document...")
        if question:
            st.session_state.chat_history.append(("user", question))
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    relevant_chunks = st.session_state.vector_store.query(question, top_k=4)
                    answer = answer_question(question, relevant_chunks, model=model_name)
                    st.markdown(answer)
            st.session_state.chat_history.append(("assistant", answer))

    with tab2:
        st.write("Generate a structured summary of the entire document.")
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                summary = summarize_text(st.session_state.full_text, model=model_name)
                st.markdown(summary)
