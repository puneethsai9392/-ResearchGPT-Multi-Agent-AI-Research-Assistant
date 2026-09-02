import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from app.config import CHROMA_PERSIST_DIR
from app.rag.embeddings import get_embedding_model
from app.utils.logger import get_logger

logger = get_logger("RAG.VectorStore")

class InMemoryVectorStore:
    """Fallback vector store when ChromaDB is not available."""
    def __init__(self):
        self.docs: List[Document] = []

    def add_documents(self, documents: List[Document]):
        self.docs.extend(documents)
        logger.info(f"InMemoryVectorStore: added {len(documents)} docs. Total: {len(self.docs)}")

    def similarity_search_with_score(self, query: str, k: int = 4):
        # Keyword relevance fallback
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in self.docs:
            content_words = set(doc.page_content.lower().split())
            common = query_words.intersection(content_words)
            score = len(common) / max(1, len(query_words))
            scored_docs.append((doc, score))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:k]

    def get_sources(self) -> List[Dict[str, Any]]:
        sources_map = {}
        for d in self.docs:
            src = d.metadata.get("source", "unknown")
            sources_map[src] = sources_map.get(src, 0) + 1
        return [{"source": k, "chunks_count": v} for k, v in sources_map.items()]

    def count(self) -> int:
        return len(self.docs)

class VectorStoreManager:
    """Manages document vectorization and retrieval via ChromaDB."""
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.store = None
        self.fallback = False
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from langchain_community.vectorstores import Chroma
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
            self.store = Chroma(
                collection_name="researchgpt_docs",
                embedding_function=self.embedding_model,
                persist_directory=CHROMA_PERSIST_DIR
            )
            logger.info("ChromaDB vector store initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB ({e}). Falling back to InMemoryVectorStore.")
            self.store = InMemoryVectorStore()
            self.fallback = True

    def add_documents(self, documents: List[Document]):
        if not documents:
            return
        if self.fallback:
            self.store.add_documents(documents)
        else:
            self.store.add_documents(documents)
            try:
                self.store.persist()
            except AttributeError:
                pass
        logger.info(f"Successfully added {len(documents)} documents to vector store.")

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        try:
            if self.fallback:
                scored = self.store.similarity_search_with_score(query, k=k)
                return [doc for doc, _ in scored]
            return self.store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []

    def get_sources(self) -> List[Dict[str, Any]]:
        try:
            if self.fallback:
                return self.store.get_sources()
            
            collection = self.store._collection
            metadatas = collection.get().get("metadatas", [])
            sources_map = {}
            for meta in metadatas:
                src = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
                sources_map[src] = sources_map.get(src, 0) + 1
            return [{"source": k, "chunks_count": v} for k, v in sources_map.items()]
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return []

    def count(self) -> int:
        try:
            if self.fallback:
                return self.store.count()
            return self.store._collection.count()
        except Exception:
            return 0

# Singleton Instance
vector_store_manager = VectorStoreManager()
