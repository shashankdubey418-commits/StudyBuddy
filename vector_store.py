"""
vector_store.py
Wraps ChromaDB with a free, local sentence-transformers embedding model
so no API calls (and no cost) are needed for embeddings.
"""

import uuid
import chromadb
from chromadb.utils import embedding_functions


class VectorStore:
    def __init__(self, collection_name: str = "study_docs", persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Start fresh each time a new document is indexed in this session
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

    def add_chunks(self, chunks: list[str]) -> None:
        if not chunks:
            return
        ids = [str(uuid.uuid4()) for _ in chunks]
        self.collection.add(documents=chunks, ids=ids)

    def query(self, question: str, top_k: int = 4) -> list[str]:
        results = self.collection.query(query_texts=[question], n_results=top_k)
        return results.get("documents", [[]])[0]
