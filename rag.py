"""
rag.py
Handles talking to a locally running Ollama model: builds prompts that
combine retrieved context with the user's question, and calls the model.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1:8b"


def _call_ollama(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.3) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. Make sure it's installed and running:\n"
            "1. Install from https://ollama.com\n"
            "2. Run `ollama pull llama3.1:8b` (or your chosen model)\n"
            "3. Run `ollama serve`"
        )
    except Exception as e:
        return f"Error calling the model: {e}"


def answer_question(question: str, context_chunks: list[str], model: str = DEFAULT_MODEL) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no relevant context found)"

    prompt = f"""You are a helpful study assistant. Answer the question using ONLY the context below.
If the answer is not contained in the context, say so honestly instead of guessing.

Context:
{context}

Question: {question}

Answer:"""

    return _call_ollama(prompt, model=model)


def summarize_text(full_text: str, model: str = DEFAULT_MODEL, max_chars: int = 12000) -> str:
    # Small local models have limited context windows, so truncate very long documents
    truncated = full_text[:max_chars]

    prompt = f"""Summarize the following study material into clear, well-organized bullet points.
Cover the key concepts, definitions, and any important examples. Group related points under short headings.

Material:
{truncated}

Summary:"""

    return _call_ollama(prompt, model=model, temperature=0.2)
