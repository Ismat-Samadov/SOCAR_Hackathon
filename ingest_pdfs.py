"""Script to ingest all PDFs into the vector database"""

from pathlib import Path
from loguru import logger
import sys

from src.llm.rag_pipeline import get_rag_pipeline
from src.ocr.processor import get_ocr_processor

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")


def ingest_pdfs(pdf_dir: str = "data/pdfs", limit: int = None):
    """
    Ingest all PDFs from directory into vector database

    Args:
        pdf_dir: Directory containing PDF files
        limit: Optional limit on number of PDFs to process
    """
    pdf_path = Path(pdf_dir)

    if not pdf_path.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return

    # Get all PDF files
    pdf_files = list(pdf_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")

    if limit:
        pdf_files = pdf_files[:limit]
        logger.info(f"Processing only first {limit} files")

    # Initialize components
    ocr = get_ocr_processor()
    rag = get_rag_pipeline()

    # Process each PDF
    for idx, pdf_file in enumerate(pdf_files, 1):
        try:
            logger.info(f"[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")

            # Read PDF
            with open(pdf_file, "rb") as f:
                pdf_content = f.read()

            # Extract text with OCR
            pages = ocr.process_pdf(pdf_content, pdf_file.name)
            logger.info(f"Extracted {len(pages)} pages from {pdf_file.name}")

            # Add to vector database
            rag.add_processed_document(pdf_file.name, pages)

            logger.info(f"Successfully ingested {pdf_file.name}")

        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            continue

    # Print stats
    stats = rag.vector_store.get_stats()
    logger.info(f"\nIngestion complete!")
    logger.info(f"Total documents in vector store: {stats['total_documents']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest PDFs into vector database")
    parser.add_argument(
        "--dir",
        type=str,
        default="data/pdfs",
        help="Directory containing PDF files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of PDFs to process (for testing)",
    )

    args = parser.parse_args()
    ingest_pdfs(args.dir, args.limit)
