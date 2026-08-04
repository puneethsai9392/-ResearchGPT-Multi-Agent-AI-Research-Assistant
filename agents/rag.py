from typing import List, Dict, Any
from app.rag.retriever import retriever_instance
from app.utils.logger import get_logger

logger = get_logger("Agent.RAG")

def run_rag_agent(tasks: List[str], query: str) -> List[Dict[str, Any]]:
    """
    RAG Agent: Searches ChromaDB vector store across tasks and returns relevant chunks.
    """
    rag_results = []
    seen_chunks = set()

    search_terms = [query] + tasks
    for term in search_terms:
        chunks = retriever_instance.retrieve(term, top_k=3)
        for chunk in chunks:
            chunk_text = chunk["content"]
            if chunk_text not in seen_chunks:
                seen_chunks.add(chunk_text)
                rag_results.append({
                    "snippet": chunk_text,
                    "source": chunk["source"],
                    "chunk_index": chunk.get("chunk_index", 0),
                    "query": term,
                    "source_type": "vector_db"
                })

    logger.info(f"RAG Agent retrieved {len(rag_results)} unique vector store chunks.")
    return rag_results
