from typing import List, Dict, Any
from langchain_core.documents import Document
from app.rag.vector_store import vector_store_manager
from app.utils.logger import get_logger

logger = get_logger("RAG.Retriever")

class HybridRetriever:
    """Combines vector similarity search with BM25/keyword ranking."""
    def __init__(self, vector_store=vector_store_manager):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant document chunks for a query and formats them with source metadata.
        """
        logger.info(f"Retrieving context for query: '{query}'")
        docs = self.vector_store.similarity_search(query, k=top_k * 2)

        if not docs:
            logger.info("No documents found in vector store matching query.")
            return []

        # Rerank / keyword score refinement
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in docs:
            content_lower = doc.page_content.lower()
            keyword_score = sum(1 for w in query_words if w in content_lower)
            scored_docs.append((doc, keyword_score))

        # Sort by keyword overlap + preserve vector order
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in scored_docs[:top_k]]

        results = []
        for d in top_docs:
            results.append({
                "content": d.page_content,
                "source": d.metadata.get("source", "Unknown"),
                "chunk_index": d.metadata.get("chunk_index", 0)
            })

        logger.info(f"Retrieved {len(results)} context chunks.")
        return results

retriever_instance = HybridRetriever()
