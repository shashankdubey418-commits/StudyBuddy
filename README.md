# 📚 AI Study Assistant

Upload a PDF, DOCX, or PPTX and ask questions about it, or generate a
summary — all running **locally and free**, using a RAG (Retrieval-Augmented
Generation) pipeline with an open-source LLM via Ollama.

## How it works

```
Upload file → extract text → split into chunks → embed chunks (local model)
                                                          ↓
                                              store in ChromaDB (vector DB)
                                                          ↓
Your question → embed it → retrieve top-k similar chunks → build a prompt
                                (context + question) → send to local LLM (Ollama)
                                                          ↓
                                                     Answer displayed in the UI
```

- **Parsing**: `pdfplumber`, `python-docx`, `python-pptx`
- **Chunking**: custom overlapping character-based splitter (`chunker.py`)
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`) — runs on CPU, no API key
- **Vector store**: `ChromaDB` (persists to a local `chroma_db/` folder)
- **LLM**: any model served locally by [Ollama](https://ollama.com) (e.g. `llama3.1:8b`, `phi3`, `mistral`)
- **UI**: Streamlit

## Setup

### 1. Install Ollama and pull a model
```bash
# Install Ollama from https://ollama.com (one-time)
ollama pull llama3.1:8b
ollama serve   # starts the local model server on http://localhost:11434
```
If your laptop is low on RAM/GPU, try a smaller model instead, e.g. `ollama pull phi3` — just make sure the "Ollama model name" field in the app sidebar matches whatever you pulled.

### 2. Install Python dependencies
```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```
This opens the app in your browser at `http://localhost:8501`.

## Using it

1. Upload a PDF, DOCX, or PPTX from the sidebar. It's parsed, chunked, and indexed automatically.
2. **Ask Questions tab** — chat with your document; answers are grounded only in the retrieved chunks (reduces hallucination).
3. **Summarize tab** — click "Generate Summary" for a structured bullet-point summary of the whole document.

## Project structure
```
study-assistant/
├── app.py             # Streamlit UI — ties everything together
├── parser.py           # Extracts text from PDF / DOCX / PPTX
├── chunker.py           # Splits text into overlapping chunks
├── vector_store.py       # ChromaDB + local embeddings wrapper
├── rag.py                # Prompt building + calls to Ollama
├── requirements.txt
└── README.md
```

## Notes / known limitations

- **First upload is slow**: the first time you run it, `sentence-transformers` downloads the embedding model (~90MB) from Hugging Face. After that it's cached locally and fast.
- **Scanned/image-only PDFs** won't extract text (no OCR is included). If you need that, add `pytesseract` + `pdf2image`.
- **Local models are weaker than GPT-4/Claude-class models.** An 8B model on a CPU-only laptop can be slow and occasionally less precise. This is the trade-off for a free, offline, API-key-less project — try a smaller model like `phi3` if `llama3.1:8b` is too slow.
- **Each new upload resets the vector index** (by design, so you don't mix content from different documents). To support multiple documents at once, you'd tag chunks with a document ID and filter queries by it.

## Ideas to extend this (good for a resume bullet point)

- Add OCR support for scanned PDFs
- Support multiple documents simultaneously with source citations
- Add a "flashcard generator" mode using the same RAG context
- Swap Ollama for a cloud API (Claude/OpenAI) as an optional toggle for higher-quality answers
- Deploy with Docker so it runs anywhere without manual setup
