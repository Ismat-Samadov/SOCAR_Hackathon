"""ChromaDB vector store for document embeddings"""

from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger

from src.config import settings as app_settings


class ChromaVectorStore:
    """Vector store using ChromaDB"""

    def __init__(self, collection_name: str = "socar_documents"):
        """
        Initialize ChromaDB vector store

        Args:
            collection_name: Name of the collection to use
        """
        # Initialize ChromaDB client
        self.db_path = app_settings.vector_db_path
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embedding model loaded")

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "SOCAR historical documents"},
        )

        logger.info(f"ChromaDB initialized with collection: {collection_name}")
        logger.info(f"Collection contains {self.collection.count()} documents")

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
    ):
        """
        Add documents to the vector store

        Args:
            texts: List of text chunks to add
            metadatas: List of metadata dicts (pdf_name, page_number, etc.)
            ids: Optional list of document IDs
        """
        if not texts:
            logger.warning("No texts provided to add")
            return

        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]

        logger.info(f"Adding {len(texts)} documents to vector store")

        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Add to ChromaDB
        self.collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Successfully added {len(texts)} documents")

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Search for similar documents

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            Dict with documents, metadatas, and distances
        """
        logger.info(f"Searching for: {query[:100]}...")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_metadata,
        )

        logger.info(f"Found {len(results['documents'][0])} results")

        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0],
        }

    def clear(self):
        """Clear all documents from the collection"""
        logger.warning("Clearing all documents from collection")
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"description": "SOCAR historical documents"},
        )

    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
            "db_path": str(self.db_path),
        }


# Singleton instance
_vector_store = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store
