"""Pinecone vector store for document embeddings"""

from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from loguru import logger
import time

from src.config import settings as app_settings


class PineconeVectorStore:
    """Vector store using Pinecone"""

    def __init__(self, index_name: str = None):
        """
        Initialize Pinecone vector store

        Args:
            index_name: Name of the Pinecone index to use
        """
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=app_settings.pinecone_api_key)
        self.index_name = index_name or app_settings.pinecone_index_name

        # Initialize embedding model (matches Pinecone index: 1024 dimensions)
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.embedding_dimension = 1024  # bge-large-en-v1.5 dimension (matches Pinecone)
        logger.info("Embedding model loaded")

        # Get or create index
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

        logger.info(f"Pinecone initialized with index: {self.index_name}")
        logger.info(f"Index stats: {self.index.describe_index_stats()}")

    def _ensure_index_exists(self):
        """Verify index exists"""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            logger.error(f"Pinecone index '{self.index_name}' not found!")
            logger.error(f"Available indexes: {existing_indexes}")
            raise ValueError(
                f"Pinecone index '{self.index_name}' does not exist. "
                f"Please create it first or check PINECONE_INDEX_NAME in .env"
            )
        logger.info(f"Connected to existing Pinecone index: {self.index_name}")

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
            ids = [f"doc_{i}_{int(time.time())}" for i in range(len(texts))]

        logger.info(f"Adding {len(texts)} documents to Pinecone")

        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Prepare vectors for upsert
        vectors = []
        for i, (doc_id, embedding, text, metadata) in enumerate(zip(ids, embeddings, texts, metadatas)):
            vectors.append({
                "id": doc_id,
                "values": embedding.tolist(),
                "metadata": {
                    **metadata,
                    "text": text[:1000]  # Store first 1000 chars in metadata
                }
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")

        logger.info(f"Successfully added {len(texts)} documents to Pinecone")

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
        logger.info(f"Searching Pinecone for: {query[:100]}...")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search Pinecone
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=n_results,
            include_metadata=True,
            filter=filter_metadata
        )

        # Extract results
        documents = []
        metadatas = []
        distances = []

        for match in results['matches']:
            documents.append(match['metadata'].get('text', ''))
            # Remove 'text' from metadata as it's already in documents
            metadata = {k: v for k, v in match['metadata'].items() if k != 'text'}
            metadatas.append(metadata)
            distances.append(1 - match['score'])  # Convert similarity to distance

        logger.info(f"Found {len(documents)} results")

        return {
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances,
        }

    def clear(self):
        """Clear all documents from the index"""
        logger.warning("Deleting and recreating Pinecone index")
        self.pc.delete_index(self.index_name)
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def get_stats(self) -> Dict:
        """Get index statistics"""
        stats = self.index.describe_index_stats()
        return {
            "total_documents": stats.get('total_vector_count', 0),
            "index_name": self.index_name,
            "dimension": self.embedding_dimension,
        }


# Singleton instance
_vector_store = None


def get_vector_store() -> PineconeVectorStore:
    """Get or create Pinecone vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = PineconeVectorStore()
    return _vector_store
