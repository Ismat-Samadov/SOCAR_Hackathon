"""RAG (Retrieval Augmented Generation) pipeline"""

from typing import List, Dict, Optional
from loguru import logger

from src.llm.deepseek_client import get_deepseek_client
from src.vectordb import get_vector_store
from src.api.models import SourceReference


class RAGPipeline:
    """RAG pipeline for document-based question answering"""

    def __init__(self):
        """Initialize RAG pipeline"""
        self.llm = get_deepseek_client()
        self.vector_store = get_vector_store()
        logger.info("RAG pipeline initialized")

    def query(
        self,
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        n_results: int = 3,
    ) -> Dict:
        """
        Answer a question using RAG

        Args:
            question: User's question
            chat_history: Previous chat messages
            n_results: Number of documents to retrieve

        Returns:
            Dict with 'answer' and 'sources'
        """
        logger.info(f"Processing query: {question[:100]}...")

        # Step 1: Retrieve relevant documents
        search_results = self.vector_store.search(question, n_results=n_results)

        # Step 2: Format sources
        sources = []
        context_chunks = []

        for doc, metadata in zip(search_results["documents"], search_results["metadatas"]):
            sources.append(
                SourceReference(
                    pdf_name=metadata.get("pdf_name", "unknown.pdf"),
                    page_number=metadata.get("page_number", 0),
                    content=doc[:500],  # Limit content length
                )
            )
            context_chunks.append(doc)

        logger.info(f"Retrieved {len(sources)} source documents")

        # Step 3: Generate answer using LLM
        answer = self.llm.generate_with_context(
            query=question,
            context_chunks=context_chunks,
            chat_history=chat_history,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    def add_processed_document(
        self,
        pdf_name: str,
        pages: List[Dict[str, any]],
        chunk_size: int = 600,
        chunk_overlap: int = 100,
    ):
        """
        Add a processed PDF to the vector store

        Args:
            pdf_name: Name of the PDF file
            pages: List of page dicts with page_number and MD_text
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        logger.info(f"Adding document to vector store: {pdf_name}")

        texts = []
        metadatas = []
        ids = []

        # Process each page
        for page in pages:
            page_num = page["page_number"]
            text = page["MD_text"]

            # Simple chunking by character count
            chunks = self._chunk_text(text, chunk_size, chunk_overlap)

            for chunk_idx, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({
                    "pdf_name": pdf_name,
                    "page_number": page_num,
                    "chunk_index": chunk_idx,
                })
                ids.append(f"{pdf_name}_p{page_num}_c{chunk_idx}")

        # Add to vector store
        self.vector_store.add_documents(texts, metadatas, ids)
        logger.info(f"Added {len(texts)} chunks from {pdf_name}")

    def _chunk_text(
        self, text: str, chunk_size: int, chunk_overlap: int
    ) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start += chunk_size - chunk_overlap

        return chunks


# Singleton instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
