"""Vector database factory and interface"""

from src.config import settings


def get_vector_store():
    """Factory function to get the configured vector store"""
    if settings.vector_db_type == "pinecone":
        from src.vectordb.pinecone_store import get_vector_store as get_pinecone_store
        return get_pinecone_store()
    else:  # Default to chroma
        from src.vectordb.chroma_store import get_vector_store as get_chroma_store
        return get_chroma_store()


__all__ = ["get_vector_store"]
