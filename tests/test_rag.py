import os
import pytest
from app.rag.loader import process_file
from app.rag.vector_store import vector_store_manager

def test_txt_loader_and_vector_store(tmp_path):
    # Create a temporary txt file
    test_file = tmp_path / "sample_rag_doc.txt"
    test_file.write_text(
        "Retrieval-Augmented Generation (RAG) is an AI architecture that enhances LLM responses "
        "by retrieving relevant document chunks from a vector database such as ChromaDB. "
        "It prevents hallucinations and ensures evidence-based citations.",
        encoding="utf-8"
    )

    documents = process_file(str(test_file))
    assert len(documents) > 0
    assert "Retrieval-Augmented Generation" in documents[0].page_content

    # Add to vector store
    initial_count = vector_store_manager.count()
    vector_store_manager.add_documents(documents)
    new_count = vector_store_manager.count()

    assert new_count >= initial_count + len(documents)

    # Search
    results = vector_store_manager.similarity_search("What is RAG?", k=1)
    assert len(results) > 0
