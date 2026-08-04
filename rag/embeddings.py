from typing import List
from app.config import EMBEDDING_MODEL_NAME, OPENAI_API_KEY
from app.utils.logger import get_logger

logger = get_logger("RAG.Embeddings")

class FallbackEmbeddings:
    """Lightweight fallback embeddings class using simple hash vectorization if model downloads fail."""
    def __init__(self, dim: int = 384):
        self.dim = dim

    def _embed_text(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        vec = [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, min(len(h), self.dim * 2), 2)]
        while len(vec) < self.dim:
            vec.extend(vec[:self.dim - len(vec)])
        return vec[:self.dim]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)

def get_embedding_model():
    """Initializes and returns the configured embedding model."""
    try:
        if OPENAI_API_KEY:
            from langchain_openai import OpenAIEmbeddings
            logger.info("Using OpenAI Embeddings")
            return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        from langchain_community.embeddings import HuggingFaceEmbeddings
        logger.info(f"Loading HuggingFace Embeddings: {EMBEDDING_MODEL_NAME}")
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    except Exception as e:
        logger.warning(f"Could not load standard embeddings ({e}). Using FallbackEmbeddings.")
        return FallbackEmbeddings()
